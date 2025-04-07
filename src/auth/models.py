from sqlalchemy import Boolean, Column, DateTime, Integer, String, Enum
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime, timedelta
import enum

def get_expired_date():
    return datetime.now() + timedelta(days=30)


class UserType(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, index=True)
    key = Column(String, unique=True)
    type = Column(Enum(UserType), default=UserType.user, nullable=False)

    max_accounts_count = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    expired_at = Column(DateTime, default=get_expired_date, nullable=False)
    
    deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"
    

from src.manage_accounts.models import Account
User.accounts = relationship(Account, back_populates="user")
