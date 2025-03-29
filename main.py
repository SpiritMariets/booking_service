from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import hmac
import hashlib
import models
import schemas
import crud
import payment
from database import SessionLocal, engine
from datetime import datetime, timedelta

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

# Регистрация пользователя
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# Получение информации о пользователе
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Создание бронирования
@app.post("/bookings/", response_model=schemas.PaymentURL)
def create_booking(booking: schemas.BookingBase, db: Session = Depends(get_db)):
    booking_payment = payment.new_payment(booking.total_price)
    booking.payment_id = booking_payment.id
    crud.create_booking(db=db, booking=booking)
    return {"url" : booking_payment.confirmation.confirmation_url}
    #return crud.create_booking(db=db, booking=booking)

# Получение информации о корте
@app.get("/courts/{court_id}", response_model=schemas.Court)
def read_court(court_id: int, db: Session = Depends(get_db)):
    db_court = crud.get_court(db, court_id=court_id)
    if db_court is None:
        raise HTTPException(status_code=404, detail="Court not found")
    return db_court

# Отмена бронирования
@app.delete("/bookings/{booking_id}", response_model=schemas.BookingCancelResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.cancel_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if (db_booking.start_time - datetime.now() > timedelta(hours=24)) :
        payment.new_refund(db_booking.total_price, db_booking.payment_id)
    return {"message": "Booking cancelled successfully", "booking_id": booking_id}

# Получение информации о бронированиях пользователя
@app.get("/bookings/{user_id}", response_model=list[schemas.Booking])
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    db_booking = crud.get_user_bookings(db, user_id=user_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Bookings not found")
    return db_booking


# Обработчик вебхуков (почему то не работает)
@app.post(":443/api/yookassa-webhook")
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