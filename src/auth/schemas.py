from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    key: str

class LoginResponse(BaseModel):
    token: str