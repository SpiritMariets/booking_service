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
    free_time: list[int]

class PriceAdd(BaseModel):
    court_id: int
    day: int
    hour: int
    price: float

class Price(BaseModel):
    price: list[dict[int, float]]

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