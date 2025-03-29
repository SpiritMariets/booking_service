from sqlalchemy.orm import Session
import models
import schemas

# получение информации о пользователе по id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# получение информации о пользователе по email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# регистрация нового пользователя
def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, full_name=user.full_name, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# получение информации о корте по id
def get_court(db: Session, court_id: int):
    return db.query(models.Court).filter(models.Court.id == court_id).first()

# получение информации о бронированиях пользователя
def get_user_bookings(db: Session, user_id: int):
    return db.query(models.Booking).filter(models.Booking.user_id == user_id).order_by(models.Booking.start_time).all()

# создание нового бронирования
def create_booking(db: Session, booking: schemas.BookingBase):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

# отмена бронирования
def cancel_booking(db: Session, booking_id: int):
    db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db.delete(db_booking)
    db.commit()
    return db_booking

def update_booking(db : Session, payment_id: str, status : str):
    db_booking = db.query(models.Booking).filter(models.Booking.payment_id == payment_id).first()
    if db_booking is None:
        return None  # Бронирование не найдено
    db_booking.status = "status"
    db.commit()
    return db_booking