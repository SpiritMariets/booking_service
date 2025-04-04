import uuid
import crud
import time
from yookassa import Configuration, Payment, Refund
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from dotenv import load_dotenv
import os

# загрузка переменных окружения и инициализация переменных
load_dotenv()

SHOP_ID = os.getenv("SHOP_ID")
SECRET_KEY = os.getenv("SECRET_KEY")
LOG_FILE = os.getenv("LOG_FILE")
RETURN_URL = os.getenv("RETURN_URL")

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

# логирование вебхуков
async def log_webhook(data: dict):
    with open(LOG_FILE, "a") as f:
        from datetime import datetime
        f.write(f"\n[{datetime.now()}] {data}\n")

# создание нового платежа
async def new_payment(value : float):
    payment = Payment.create({
        "amount": {
            "value": f"{value}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{RETURN_URL}"
        },
        "capture": True,
        "description": "Court's booking"
    }, uuid.uuid4())
    return payment

# создание возврата
async def new_refund(value : float, payment_id : str):
    refund = Refund.create({
        "amount": {
            "value": f"{value}",
            "currency": "RUB"
        },
        "payment_id": f"{payment_id}"
    })
    return refund

async def make_get_request():
    with Session(autoflush=False, bind=engine) as db:
        while True:
            db_bookings = crud.get_pending_bookings(db)
            for booking in db_bookings:
                payment = Payment.find_one(booking.payment_id)
                if payment.status == "succeeded":
                    crud.update_booking(db, payment_id = booking.payment_id, status="succeeded")
                elif payment.status == "canceled":
                    crud.update_booking(db, payment_id = booking.payment_id, status="canceled")
            time.sleep(30)  # Задержка 30 секунд