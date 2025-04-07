from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from src.auth.models import User, UserType
from src.config import Config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User
import jwt
import datetime

async def decode_token(token):
    try:
        payload = jwt.decode(token, Config.jwt_secret, algorithms=["HS256"])
        return payload
    except:
        return {}

class AdminMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
            payload = await decode_token(token)
            if payload.get("username") and payload.get("id") and payload.get("exp"):
                db: AsyncSession = request.state.db
                user = (await db.execute(select(User).where(User.id == payload.get("id"), User.username == payload.get("username")))).scalar()
                if user and user.expired_at > datetime.datetime.now() and payload.get("exp") > int(datetime.datetime.now().timestamp()):
                    request.state.user = user
                    if user.type == UserType.admin:
                        return await call_next(request)
        return JSONResponse(status_code=404, content={"detail": "Not found"})