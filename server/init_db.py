# server/init_db.py
import asyncio
from database import engine
from models import Base

async def init_models():
    # создаёт все таблицы, описанные в models.py
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")

if __name__ == "__main__":
    asyncio.run(init_models())
