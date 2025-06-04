from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False
    security_code: Optional[str] = None

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class TicketBase(BaseModel):
    title: str
    description: str

class TicketCreate(TicketBase):
    pass

class TicketResponse(TicketBase):
    id: int
    status: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    ticket_id: int

class MessageResponse(MessageBase):
    id: int
    created_at: datetime
    ticket_id: int
    user_id: int

    class Config:
        from_attributes = True 
class UserLogin(BaseModel):
    username: str
    password: str        