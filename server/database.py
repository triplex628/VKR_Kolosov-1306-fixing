import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Загружаем переменные окружения из .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,               # для логирования SQL-запросов
    future=True
)

# Конфигурируем SessionLocal, чтобы он возвращал AsyncSession
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # не сбрасывать объекты после коммита
    autoflush=False,
    autocommit=False,
)

# Базовый класс для декларативных моделей
Base = declarative_base()

# Зависимость для FastAPI — отдаёт асинхронную сессию
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
