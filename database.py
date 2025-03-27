from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем данные для подключения к PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем подключение к PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase): pass