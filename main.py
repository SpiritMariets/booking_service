from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import hmac
import hashlib
import models
import schemas
import crud
import payment
from database import SessionLocal, engine
from datetime import date

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#with Session(autoflush=False, bind=engine) as db:
 #   for id in range(1, 5):
  #      for day in range(1, 8):
   #         for hour in range(8, 24):
    #            crud.create_prices(db=db, price={"court_id": id, "day": day, "hour": hour, "price": id * day * hour}) 

# Создание бронирования
@app.post("/bookings/", response_model=schemas.PaymentURL)
def create_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    booking_payment = payment.new_payment(booking.total_price)
    booking.payment_id = booking_payment.id
    crud.create_booking(db=db, booking=booking)
    return {"url" : booking_payment.confirmation.confirmation_url}

# Получение информации о корте
@app.get("/courts/{court_id}", response_model=schemas.Court)
def read_court(court_id: int, db: Session = Depends(get_db)):
    db_court = crud.get_court(db, court_id=court_id)
    if db_court is None:
        raise HTTPException(status_code=404, detail="Court not found")
    return db_court

@app.get("/price/{court_id}/{day}", response_model=schemas.Price)
def get_price(court_id: int, day: int, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, court_id=court_id, day=day)
    if db_price is None:
        raise HTTPException(status_code=404, detail="Price not found")
    return {"price": db_price}

# Отмена бронирования 
@app.delete("/bookings/{booking_id}", response_model=schemas.BookingCancelResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.cancel_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled successfully", "booking_id": booking_id}

# Получение информации о свободном времени корта
@app.get("/free_time/{court_id}/{date}", response_model=schemas.CourtFreeTime)
def get_free_time(court_id: int, date: date, db: Session = Depends(get_db)):
    db_court_free_time = crud.get_court_free_time(db, court_id=court_id, date=date)
    return {"free_time": db_court_free_time}

# Обработчик вебхуков (почему то не работает)
@app.post("/api/yookassa-webhook")
async def handle_webhook(request: Request, db : Session = Depends(get_db)):
    print('*')
    # Получаем тело запроса как bytes для проверки подписи
    body_bytes = await request.body()
    
    # Получаем подпись из заголовков
    signature = request.headers.get("Webhook-Signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Missing signature header"
        )
    
    # Проверяем подпись
    expected_signature = hmac.new(
        payment.SECRET_KEY.encode(),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid signature"
        )
    
    # Парсим JSON
    try:
        data = await request.json()
        webhook_data = models.WebhookData(**data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid webhook data: {str(e)}"
        )
    
    # Логируем вебхук
    payment.log_webhook(data)
    
    # Обрабатываем события
    payment_id = webhook_data.object.id
    
    if webhook_data.event == "payment.succeeded":
        # Платеж успешен
        await process_successful_payment(payment_id, db)
        return {"status": "payment processed"}

    elif webhook_data.event == "payment.canceled":
        # Платеж отменен
        await process_canceled_payment(payment_id)
        return {"status": "payment canceled"}
    
    return {"status": "unknown event"}

# Обработчики платежей
async def process_successful_payment(payment_id: str, db):
    """Обновляем статус заказа в БД и выполняем бизнес-логику"""
    crud.update_booking(db, payment_id = payment_id, status="succeeded")
    # Здесь должна быть ваша логика:
    # 1. Найти заказ по payment_id
    # 2. Обновить статус на "оплачено"
    # 3. Активировать услугу/отправить товар
    print(f"Платеж {payment_id} успешно обработан")


async def process_canceled_payment(payment_id: str, db):
    """Обработка отмененного платежа"""
    crud.update_booking(db, payment_id = payment_id, status="succeeded")
    print(f"Платеж {payment_id} был отменен")