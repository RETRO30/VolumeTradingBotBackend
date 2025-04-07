from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from src.database import Base
import enum


class AccountStatus(enum.Enum):
    running = "running"
    stopped = "stopped"
    deleted = "deleted"
    error = "error"


class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    secret_key = Column(String, nullable=False)
    
    symbol = Column(String, nullable=False)    
    deposit = Column(Float, nullable=False)
    current_balance_usd = Column(Float, nullable=False)
    grid_count   = Column(Integer, nullable=False)
    start_price = Column(Float, nullable=False)
    end_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    
    status = Column(Enum(AccountStatus), default=AccountStatus.stopped, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    
    def __repr__(self):
        return f"Account(id={self.id}, name={self.name})"

class TradeSide(str, enum.Enum):
    buy = "buy"
    sell = "sell"
    
class TradeStatus(str, enum.Enum):
    open = "open"
    closed = "closed"

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String, nullable=False)  # Например: BTCUSDT
    side = Column(Enum(TradeSide), nullable=False)  # buy или sell

    price = Column(Float, nullable=False)  # Цена сделки
    quantity = Column(Float, nullable=False)  # Кол-во куплено/продано
    
    status = Column(Enum(TradeStatus), default=TradeStatus.open, nullable=False)

    created_at = Column(DateTime, default=datetime.now(), nullable=False)
    

Trade.account_id = Column(Integer, ForeignKey(Account.id), nullable=False)
Trade.account = relationship(Account, back_populates="trades")    
    
from src.auth.models import User

Account.user_id = Column(Integer, ForeignKey(User.id), nullable=False)
Account.user = relationship(User, back_populates="accounts")
Account.trades = relationship(Trade, back_populates="account")
    