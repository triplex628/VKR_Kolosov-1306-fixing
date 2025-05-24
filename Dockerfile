# Dockerfile
FROM python:3.10-slim

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и ставим Python-зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . .

# Переменные окружения для Alembic и SQLAlchemy
ENV PYTHONUNBUFFERED=1
# Можно положить нужные переменные в .env (см. ниже)

EXPOSE 8000

# При старте сначала прогоняем миграции, потом запускаем Uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn server.main:app --host 0.0.0.0 --port 8000"]
