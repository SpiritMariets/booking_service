import uuid
from yookassa import Configuration, Payment, Refund
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
def log_webhook(data: dict):
    with open(LOG_FILE, "a") as f:
        from datetime import datetime
        f.write(f"\n[{datetime.now()}] {data}\n")

# создание нового платежа
def new_payment(value : float):
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
def new_refund(value : float, payment_id : str):
    refund = Refund.create({
        "amount": {
            "value": f"{value}",
            "currency": "RUB"
        },
        "payment_id": f"{payment_id}"
    })
    return refund
