# alembic/env.py

import os
import sys
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

# ----------------------------
# 1) Подгружаем .env
# ----------------------------
load_dotenv(os.path.join(os.getcwd(), ".env"))

# ----------------------------
# 2) Настраиваем alembic.ini
# ----------------------------
# Теперь явно передаём DATABASE_URL из .env
config = context.config
# alembic/env.py, в самом начале после load_dotenv(...)
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL не задан в .env")

# Если в DATABASE_URL у вас схема asyncpg, заменяем её на синхронную:
if db_url.startswith("postgresql+asyncpg://"):
    sync_db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
else:
    sync_db_url = db_url

# Прописываем синхронный URL в конфигурацию Alembic
config.set_main_option("sqlalchemy.url", sync_db_url)


# ----------------------------
# 3) Делаем проект пакетом
# ----------------------------
sys.path.insert(0, os.path.abspath(os.getcwd()))

# ----------------------------
# 4) Импортируем вашу метадату
# ----------------------------
from server.database import Base   # Base = declarative_base()
import server.models               # noqa: регистрирует модели в Base.metadata

# ----------------------------
# 5) Настраиваем логирование
# ----------------------------
fileConfig(config.config_file_name)

# ----------------------------
# 6) Берём откуда сравнивать схему
# ----------------------------
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# ----------------------------
# 7) Выбор режима и запуск
# ----------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
