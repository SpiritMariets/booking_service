from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    email: str
    full_name: str
    phone: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class CourtBase(BaseModel):
    name: str
    location: str
    type: str
    price_per_hour: float

class Court(CourtBase):
    id: int

    class Config:
        orm_mode = True

class BookingBase(BaseModel):
    user_id: int
    court_id: int
    start_time: datetime
    end_time: datetime
    total_price: float

class Booking(BookingBase):
    id: int

    class Config:
        orm_mode = True

class BookingCancelResponse(BaseModel):
    message: str
    booking_id: int