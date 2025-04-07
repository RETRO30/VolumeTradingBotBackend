import asyncio
from src.config import Config
import os
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection

from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Получаем URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Импортируем метаданные
from src.database import Base
import src.auth.models
import src.manage_accounts.models
target_metadata = Base.metadata

def run_migrations_offline():
    """Генерация SQL-файла без подключения к БД"""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Асинхронный запуск миграций с подключением к БД"""
    connectable = create_async_engine(Config.database_url, pool_pre_ping=True)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

run()