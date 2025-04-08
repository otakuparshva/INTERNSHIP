from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    CANDIDATE = "candidate"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str = Field(..., alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    last_login: Optional[datetime] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str
    role: UserRole

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None 