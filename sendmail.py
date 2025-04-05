import smtplib
from datetime import date
from email.message import EmailMessage
from dotenv import load_dotenv
import os

# загрузка переменных окружения и инициализация переменных
load_dotenv()

# Настройки
email_sender = os.getenv("EMAIL_SENDER")  # Ваш Gmail
email_password = os.getenv("EMAIL_PASSWORD")  # Пароль приложения (не основной!)

    # Создаем письмо
def send_mail(email_receiver: str, date: date, hour: int, name: str, court_id: int):
    msg = EmailMessage()
    msg['Subject'] = 'Бронирование корта'
    msg['From'] = email_sender
    msg['To'] = email_receiver
    msg.set_content(f'''Здравствуйте, {name}!\n Ваше бронирование подтверждено\n Ожидаем вас {date} в {hour} часов на корте номер {court_id}''')

    # Отправляем
    with smtplib.SMTP_SSL('smtp.mail.ru', 465) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(msg)