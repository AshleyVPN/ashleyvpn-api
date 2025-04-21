from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from datetime import datetime
from enum import Enum

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    telegram_id: Optional[int] = None
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    telegram_id: Optional[int] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    joined_at: datetime
    ref_id: Optional[str] = None
    source_id: Optional[str] = None

    class Config:
        from_attributes = True

class ReferalBase(BaseModel):
    parent: UUID
    child: UUID

class ReferalCreate(ReferalBase):
    pass

class ReferalResponse(ReferalBase):
    id: UUID

    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    name: str
    src_id: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class SourceResponse(SourceBase):
    id: int

    class Config:
        from_attributes = True
