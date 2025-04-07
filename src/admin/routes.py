from fastapi import APIRouter, Request, HTTPException
from src.admin.schemas import UserData, CreateUserRequest, UserId
from src.auth.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List



admin_router = APIRouter(prefix="/users")

@admin_router.get("/")
async def get_users(request: Request) -> List[UserData]:
    db: AsyncSession = request.state.db
    
    users_data = (await db.execute(select(User))).scalars().all()
    
    return [UserData(**user.__dict__) for user in users_data]

@admin_router.post("/new")
async def create_user(payload: CreateUserRequest, request: Request) -> UserData:
    db: AsyncSession = request.state.db
    
    user = User(
        username=payload.username,
        key=str(uuid.uuid4()),
        max_accounts_count=payload.max_accounts_count,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserData(**user.__dict__)


@admin_router.delete("/{id}")
async def delete_user(id: int, request: Request):
    db: AsyncSession = request.state.db
    
    user = (await db.execute(select(User).where(User.id == id))).scalar()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.deleted = True
    db.commit()
    db.refresh(user)
    
    return UserId(id=id)

@admin_router.post("/update")
async def update_user(payload: UserData, request: Request) -> UserData:
    db: AsyncSession = request.state.db
    
    user = (await db.execute(select(User).where(User.id == payload.id))).scalar()
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.username = payload.username
    user.max_accounts_count = payload.max_accounts_count
    user.key = payload.key
    user.expired_at = payload.expired_at
    db.commit()
    db.refresh(user)
    
    return UserData(**user.__dict__)