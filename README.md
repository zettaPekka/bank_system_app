![architecture](https://i.ibb.co/wNRynHDg/image.png)
# Банковское API

Этот проект представляет собой банковское API, разработанное с использованием FastAPI. В проекте реализована очередь транзакций через RabbitMQ, миграции базы данных с помощью Alembic, работа с базой данных через SQLAlchemy и авторизация на основе JWT.

## Настройка проекта

### Установка

1. **Создание виртуального окружения**

   ```bash
   python -m venv venv
   ```

2. **Активация виртуального окружения**

   - На Windows:

     ```bash
     venv\Scripts\activate
     ```

   - На macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

3. **Установка зависимостей**

   ```bash
   pip install -r requirements.txt
   ```

4. **Создание файла .env**

   Создайте файл `.env` в корне проекта и добавьте следующие переменные окружения:

   ```plaintext
   DB_PATH=ваш_путь_к_базе_данных
   RABBITMQ_HOST=ваш_хост_rabbitmq
   ```

5. **Запуск приложения**

   - Запуск основного приложения FastAPI:

     ```bash
     python app/main.py
     ```

   - Запуск потребителя очереди транзакций:

     ```bash
     python app/consumer.py
     ```

