from datetime import datetime, timedelta
from fastapi import APIRouter, Request, HTTPException
from src.auth.schemas import LoginRequest, LoginResponse
from src.auth.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import Config
import jwt

auth_router = APIRouter()

async def generate_token(user: User) -> str:
    exp = datetime.now() + timedelta(days=7)
    payload = {
        "username": user.username,
        "id": user.id,
        "exp": int(exp.timestamp())
    }
    
    return jwt.encode(payload, Config.jwt_secret, algorithm="HS256")

@auth_router.post("/login")
async def login(payload: LoginRequest, request: Request) -> LoginResponse:
    username = payload.username
    key = payload.key
    
    db: AsyncSession = request.state.db
    
    user: User = (await db.execute(select(User).where(User.username == username, User.key == key))).scalar()
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or key")
    
    if user.expired_at < datetime.now():
        raise HTTPException(status_code=401, detail="Invalid username or key")
    
    token = await generate_token(user)
    
    return LoginResponse(token=token)
    
    
    