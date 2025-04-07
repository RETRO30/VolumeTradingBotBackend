from pydantic import BaseModel

class UserData(BaseModel):
    id: int
    username: str
    key: str
    type: str
    max_accounts_count: int
    expired_at: int
    created_at: int

class CreateUserRequest(BaseModel):
    username: str
    max_accounts_count: int
    
class UserId(BaseModel):
    id: int