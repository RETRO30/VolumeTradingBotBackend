from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import Request

from src.database import engine

# Создаём глобальный async session factory
async_session = async_sessionmaker(engine, expire_on_commit=False)

class SQLAlchemySessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async with async_session() as session:
            request.state.db = session
            response = await call_next(request)
            return response