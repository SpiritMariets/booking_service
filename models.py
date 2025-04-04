from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# таблица courts
class Court(Base):
    __tablename__ = "courts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    type = Column(String)

    bookings = relationship("Booking", back_populates="court")
    price = relationship("Price", back_populates="courts")

# таблица prices: цены кортов в определенный час и день недели
class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"))
    day = Column(Integer)
    hour = Column(Integer)
    price = Column(Float)

    courts = relationship("Court", back_populates="price")

# таблица bookings
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    court_id = Column(Integer, ForeignKey("courts.id"))
    date = Column(Date)
    start_time = Column(Integer)
    end_time = Column(Integer)
    total_price = Column(Float)
    status = Column(String, default="pending")
    payment_id = Column(String)

    court = relationship("Court", back_populates="bookings")