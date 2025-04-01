from sqlalchemy.orm import Session
import models
import schemas
from datetime import date

DAY_BEGINNING = 8
DAY_ENDING = 24

# получение информации о корте по id
def get_court(db: Session, court_id: int):
    return db.query(models.Court).filter(models.Court.id == court_id).first()

# получение цены 
def get_price(db: Session, court_id: int, day: int):
    db_price = db.query(models.Price).filter(models.Price.court_id == court_id, models.Price.day == day).all()
    price = [{p.hour : p.price} for p in db_price]
    return price

# получение свободного времени определенного корта в определённый день
def get_court_free_time(db: Session, court_id: int, date: date):
    db_court = db.query(models.Booking).filter(models.Booking.court_id == court_id, models.Booking.date == date, models.Booking.status != "canceled").order_by(models.Booking.start_time).all()
    free_time = [i for i in range(DAY_BEGINNING, DAY_ENDING)]
    for c in db_court:
        for i in range(c.start_time, c.end_time):
            free_time.remove(i)
    return free_time

# создание нового бронирования
def create_booking(db: Session, booking: schemas.BookingBase):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# добавление цен not working
def create_prices(db: Session, price: dict):
    db_price = models.Price(**price)
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price

# отмена бронирования
def cancel_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db.delete(db_booking)
    db.commit()
    return db_booking

# обновление статуса бронирования
def update_booking(db : Session, payment_id: str, status : str):
    db_booking = db.query(models.Booking).filter(models.Booking.payment_id == payment_id).first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db_booking.status = status
    db.commit()
    return db_booking