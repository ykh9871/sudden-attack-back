from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Group(BaseModel):
    id: int 
    name: str
    description: str
    created_at: datetime

class GroupCreate(BaseModel):
    name: str
    description: str
    created_at: datetime

class GroupMembershipRequest(BaseModel):
    group_name: str
    created_at: Optional[str] = None

class MemberRequestsView(BaseModel):
    id:int
    username: str
    nickname: str
    occupation_name: str
    created_at: Optional[str] = None

class AllMembers(BaseModel):
    id: int
    nickname:str

class AdminUser(BaseModel):
    role: str
    group_id: int
    user_id: int