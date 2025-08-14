from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    user_id: str
    ko_name: Optional[str] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    pw: str
    birth_date: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    preferred_food: Optional[str] = None
    preferred_tags: Optional[str] = None

class UserUpdate(BaseModel):
    ko_name: Optional[str]
    email: Optional[str]
    height: Optional[float]
    weight: Optional[float]
    birth_date: Optional[str]
    preferred_food: Optional[str]
    preferred_tags: Optional[str]

class UserOut(UserBase):
    class Config:
        orm_mode = True
