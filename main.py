from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
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

@app.delete("/bookings/{booking_id}", response_model=schemas.BookingCancelResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = crud.cancel_booking(db, booking_id=booking_id)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if (db_booking.start_time - datetime.now() > timedelta(hours=24)) :
        payment.new_refund(db_booking.total_price, db_booking.payment_id)
    return {"message": "Booking cancelled successfully", "booking_id": booking_id}