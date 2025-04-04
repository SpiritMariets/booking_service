from pydantic import BaseModel
from datetime import date
from typing import Optional

class CourtBase(BaseModel):
    name: str
    location: str
    type: str

class Court(CourtBase):
    id: int

    class Config:
        orm_mode = True

class CourtFreeTime(BaseModel):
    court_id: int
    free_time: list[int]

class PriceAdd(BaseModel):
    court_id: int
    day: int
    hour: int
    price: float

class Price(BaseModel):
    court_id: int
    hour: int
    price: float

class BookingPost(BaseModel):
    name: str
    email: str
    phone: str
    date : date
    total_price: float
    slots: dict[str, list[int]]

class BookingBase(BaseModel):
    court_id: int
    name: str
    email: str
    phone: str
    date : date
    start_time: int
    end_time: int
    total_price: float
    payment_id: str

class Booking(BookingBase):
    id: int

    class Config:
        orm_mode = True

class BookingCancelResponse(BaseModel):
    message: str
    booking_id: int

class PaymentURL(BaseModel):
    url: str

# Модели данных для вебхука
class PaymentObject(BaseModel):
    id: str
    status: str
    amount: dict
    metadata: Optional[dict] = None

class WebhookData(BaseModel):
    event: str
    object: PaymentObject