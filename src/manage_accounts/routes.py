from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.models import User
from src.manage_accounts.models import Account, AccountStatus
from src.manage_accounts.schemas import AccountData, AccountCreate, AccountId
from typing import List

accounts_router = APIRouter(prefix="/accounts")

@accounts_router.get("/")
async def get_accounts(request: Request) -> List[AccountData]:
    db: AsyncSession = request.state.db
    user: User = request.state.user
    
    accounts: List[Account] = (await db.execute(select(Account).where(Account.user_id == user.id))).scalars().all()
    
    return [AccountData(**account.__dict__) for account in accounts]


@accounts_router.post("/new")
async def create_account(payload: AccountCreate, request: Request) -> AccountData:
    db: AsyncSession = request.state.db
    user: User = request.state.user
    
    account = Account(**payload.model_dump(), current_balance_usd=payload.deposit, user_id=user.id)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    return AccountData(**account.__dict__)

@accounts_router.delete("/{id}")
async def delete_account(id: int, request: Request) -> AccountId:
    db: AsyncSession = request.state.db
    user: User = request.state.user
    
    account = (await db.execute(select(Account).where(Account.id == id, Account.user_id == user.id))).scalar()
    
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.status = AccountStatus.deleted
    await db.commit()
    await db.refresh(account)
    
    return AccountId(id=id)

@accounts_router.post("/{id}/start")
async def start_account(id: int, request: Request) -> AccountId:
    db: AsyncSession = request.state.db
    user: User = request.state.user
    
    account = (await db.execute(select(Account).where(Account.id == id, Account.user_id == user.id))).scalar()
    
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.status = AccountStatus.running
    await db.commit()
    await db.refresh(account)
    
    return AccountId(id=id)

@accounts_router.post("/{id}/stop")
async def stop_account(id: int, request: Request) -> AccountId:
    db: AsyncSession = request.state.db
    user: User = request.state.user
    
    account = (await db.execute(select(Account).where(Account.id == id, Account.user_id == user.id))).scalar()
    
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account.status = AccountStatus.stopped
    await db.commit()
    await db.refresh(account)
    
    return AccountId(id=id)
