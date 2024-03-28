from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    nickname: str
    email: str
    password: str
    occupation: int
    refresh_token: Optional[str] = None


class UserInfo(BaseModel):
    username: str
    nickname: str
    email: str
    occupation_name: str
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class UserID(BaseModel):
    id: int
