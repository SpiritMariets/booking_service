from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone = Column(String)

    bookings = relationship("Booking", back_populates="user")

class Court(Base):
    __tablename__ = "courts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    type = Column(String)
    price_per_hour = Column(Float)

    bookings = relationship("Booking", back_populates="court")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    court_id = Column(Integer, ForeignKey("courts.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    total_price = Column(Float)
    status = Column(String, default="pending")
    payment_id = Column(String, unique=True)

    user = relationship("User", back_populates="bookings")
    court = relationship("Court", back_populates="bookings")