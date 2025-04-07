from datetime import datetime
from pydantic import BaseModel

class AccountData(BaseModel):
    id: int
    name: str
    api_key: str
    secret_key: str
    symbol: str
    deposit: float
    current_balance_usd: float
    grid_count: int
    start_price: float
    end_price: float
    stop_loss: float
    status: str
    created_at: datetime

class AccountCreate(BaseModel):
    name: str
    api_key: str
    secret_key: str
    symbol: str
    deposit: float
    start_price: float
    grid_count: int
    end_price: float
    stop_loss: float
    
    
class AccountId(BaseModel):
    id: int    
    