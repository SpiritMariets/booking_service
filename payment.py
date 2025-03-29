import uuid
from yookassa import Configuration, Payment, Refund
from dotenv import load_dotenv
import os

load_dotenv()

SHOP_ID = os.getenv("SHOP_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET_KEY

# создание нового платежа
def new_payment(value : float):
    payment = Payment.create({
        "amount": {
            "value": f"{value}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.google.com/"
        },
        "capture": True,
        "description": "Order No. 1"
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
