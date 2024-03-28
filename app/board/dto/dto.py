from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BoardBase(BaseModel):
    title: str
    content: str
    category_id: int
    category_type: str

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BoardBase):
    pass

class Board(BoardBase):
    id: int
    status: str
    user_id: int
    created_at: datetime

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    board_id: int
    created_at: datetime