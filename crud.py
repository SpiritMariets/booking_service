from sqlalchemy.orm import Session
import models
import schemas
import sendmail
from datetime import date
from dotenv import load_dotenv
import os

# загрузка переменных окружения и инициализация переменных
load_dotenv()

DAY_BEGINNING = int(os.getenv("DAY_BEGINNING"))
DAY_ENDING = int(os.getenv("DAY_ENDING"))

# получение информации о корте по id
def get_courts(db: Session):
    return db.query(models.Court).all()

# получение цены 
def get_price(db: Session, day: int):
    return db.query(models.Price).filter(models.Price.day == day).all()

# получение свободного времени всех кортов в определённый день
def get_free_time(db: Session, date: date):
    all_courts = get_courts(db=db)
    free_time = []
    for court in all_courts:
        db_bookings = db.query(models.Booking).filter(models.Booking.court_id == court.id, 
                                                   models.Booking.date == date, 
                                                   models.Booking.status != "canceled").order_by(models.Booking.start_time).all()
        court_free_time = [i for i in range(DAY_BEGINNING, DAY_ENDING)]
        for booking in db_bookings:
            for i in range(booking.start_time, booking.end_time):
                if i in court_free_time:   
                    court_free_time.remove(i)
        free_time.append({"court_id": court.id, "free_time": court_free_time})
    return free_time

# получение всех кортов в определенный дату и временное окно
def get_free_time_window(db: Session, date: date, start_time: int, end_time: int):
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
def get_court_free_time(db: Session, court_id: int, date: date):
    db_court = db.query(models.Booking).filter(models.Booking.court_id == court_id, 
                                               models.Booking.date == date, 
                                               models.Booking.status != "canceled").order_by(models.Booking.start_time).all()
    free_time = [i for i in range(DAY_BEGINNING, DAY_ENDING)]
    for c in db_court:
        for i in range(c.start_time, c.end_time):
            if i in free_time:   
                free_time.remove(i)
    return free_time

# создание нового бронирования
def create_booking(db: Session, booking: schemas.BookingBase):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# получения бронирований, ожидающих подтверждения
def get_pending_bookings(db: Session):
    return db.query(models.Booking.payment_id).filter(models.Booking.status == "pending").group_by(models.Booking.payment_id).all()

# добавление цен
def create_prices(db: Session, price: dict):
    db_price = models.Price(**price)
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

# отмена бронирования
def cancel_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.status == "succeeded").first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db_booking.status = "canceled"
    db.commit()
    db.refresh(db_booking)
    return db_booking

# обновление статуса бронирования
def update_booking(db : Session, payment_id: str, status : str):
    db_booking = db.query(models.Booking).filter(models.Booking.payment_id == payment_id).all()
    if len(db_booking) == 0:
        return None  # Бронирование не найдено
    for booking in db_booking:
        booking.status = status
        if status == "succeeded":
            sendmail.send_mail(email_receiver=booking.email,
                               date=booking.date,
                               hour=booking.start_time,
                               name=booking.name,
                               court_id=booking.court_id)
    db.commit()
    return db_booking