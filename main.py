from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import threading
import models
import schemas
import crud
import payment
from database import SessionLocal, engine
from datetime import date
from fastapi.middleware.cors import CORSMiddleware

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5174",  # ваш фронтенд адрес
    "http://127.0.0.1:5174"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # или можно использовать ["*"] для разрешения всех доменов (не рекомендуется для продакшена)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Запуск в отдельном потоке
thread = threading.Thread(target=payment.make_get_request, daemon=True)
thread.start()

# Создание бронирования
@app.post("/bookings/", response_model=schemas.PaymentURL)
async def create_booking(booking: schemas.BookingPost, db: Session = Depends(get_db)):
    booking_payment = payment.new_payment(booking.total_price)

    page_booking = schemas.BookingBase(
        payment_id = booking_payment.id,
        date = booking.date,
        email = booking.email,
        name = booking.name,
        total_price = booking.total_price,
        phone = booking.phone,
        court_id = 1,
        start_time = 6,
        end_time = 7
    )

    for item in booking.slots:
        for t in booking.slots[item]:
            page_booking.court_id = int(item)
            page_booking.start_time = t
            page_booking.end_time = t + 1
            crud.create_booking(db=db, booking=page_booking)
    
    return {"url" : booking_payment.confirmation.confirmation_url}

# Получение информации о кортах
@app.get("/courts/", response_model=list[schemas.Court])
async def read_court(db: Session = Depends(get_db)):
    db_court = crud.get_courts(db)
    return db_court

@app.get("/price/{day}", response_model=list[schemas.Price])
async def get_price(day: int, db: Session = Depends(get_db)):
    db_price = crud.get_price(db, day=day)
    if len(db_price) == 0:
        raise HTTPException(status_code=404, detail="Day not in week")
    return db_price

# Отмена бронирования 
@app.delete("/bookings/{booking_id}", response_model=schemas.BookingCancelResponse)
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.cancel_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled successfully", "booking_id": booking_id}

# Получение информации о свободном времени корта
#@app.get("/free_time/{date}", response_model=list[schemas.CourtFreeTime])
#async def free_time(date: date, db: Session = Depends(get_db)):

    #return crud.get_free_time(db, date=date)

@app.get("/free_time/{date}/{start_time}/{end_time}")
async def free_time_window(date: date, start_time: int = 8, end_time: int = 24, db: Session = Depends(get_db)):
    return crud.get_free_time_window(db, date=date, start_time=start_time, end_time=end_time)