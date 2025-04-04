from sqlalchemy.orm import Session
import models
import schemas
from datetime import date
from dotenv import load_dotenv
import os

# загрузка переменных окружения и инициализация переменных
load_dotenv()

DAY_BEGINNING = int(os.getenv("DAY_BEGINNING"))
DAY_ENDING = int(os.getenv("DAY_ENDING"))

# получение информации о корте по id
async def get_courts(db: Session):
    return db.query(models.Court).all()

# получение цены 
async def get_price(db: Session, day: int):
    return db.query(models.Price).filter(models.Price.day == day).all()

# получение свободного времени всех кортов в определённый день
async def get_free_time(db: Session, date: date):
    db_courts = get_courts(db=db)
    free_time = []
    for c in db_courts:
        db_court = db.query(models.Booking).filter(models.Booking.court_id == c.id, 
                                                   models.Booking.date == date, 
                                                   models.Booking.status != "canceled").order_by(models.Booking.start_time).all()
        court_free_time = [i for i in range(DAY_BEGINNING, DAY_ENDING)]
        for court in db_court:
            for i in range(court.start_time, court.end_time):
                court_free_time.remove(i)
        free_time.append({"court_id": c.id, "free_time": court_free_time})
    return free_time

# получение всех кортов в определенный дату и временное окно
async def get_free_time_window(db: Session, date: date, start_time: int, end_time: int):
    db_prices = get_price(db=db, day=(date.weekday() + 1))
    free_time = get_free_time(db=db, date=date)
    free_court = {i: [] for i in range(start_time, end_time)}
    for court in free_time:
        for t in range(start_time, end_time):
            if t in court["free_time"]:
                free_court[t].append({"court_id": court["court_id"], 
                                 "price": next((item for item in db_prices if item.court_id == court["court_id"] and item.hour == t), None).price})

    return free_court

# получение свободного времени определенного корта в определённый день
async def get_court_free_time(db: Session, court_id: int, date: date):
    db_court = db.query(models.Booking).filter(models.Booking.court_id == court_id, 
                                               models.Booking.date == date, 
                                               models.Booking.status != "canceled").order_by(models.Booking.start_time).all()
    free_time = [i for i in range(DAY_BEGINNING, DAY_ENDING)]
    for c in db_court:
        for i in range(c.start_time, c.end_time):
            free_time.remove(i)
    return free_time

# создание нового бронирования
async def create_booking(db: Session, booking: schemas.BookingBase):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# получения бронирований, ожидающих подтверждения
async def get_pending_bookings(db: Session):
    return db.query(models.Booking).filter(models.Booking.status == "pending").all()

# добавление цен
async def create_prices(db: Session, price: dict):
    db_price = models.Price(**price)
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

# отмена бронирования
async def cancel_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.status == "succeeded").first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db_booking.status = "canceled"
    db.commit()
    db.refresh(db_booking)
    return db_booking

# обновление статуса бронирования
async def update_booking(db : Session, payment_id: str, status : str):
    db_booking = db.query(models.Booking).filter(models.Booking.payment_id == payment_id).first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db_booking.status = status
    db.commit()
    db.refresh(db_booking)
    return db_booking