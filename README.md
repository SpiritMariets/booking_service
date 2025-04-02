Creating booking service for paddle club

Запуск бека: uvicorn main:app --reload

Если нет бд:
1. установить posgresql
2. далее в терминале команды:
    sudo -u postgres psql (ввести пароль, далее работаешь как бы в postgresql)
    create database booking_db;
    \c booking_db
