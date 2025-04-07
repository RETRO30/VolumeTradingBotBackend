from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from src.config import Config

# Создаём движок (один на всё приложение)
engine = create_async_engine(Config.database_url, echo=False)

# Базовый класс для моделей
Base = declarative_base()