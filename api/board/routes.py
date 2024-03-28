from fastapi import APIRouter, Depends
from typing import List, Optional
from app.user.service.service import UserService
from app.group.service.service import GroupService
from app.board.service.service import BoardService
from app.board.dto.dto import (
    BoardCreate, 
    BoardUpdate, 
    CommentCreate,
    CommentUpdate
)

router = APIRouter()
user_service = UserService()
group_service = GroupService()
board_service = BoardService()

router = APIRouter()

@router.post("/boards/", status_code=201)
def create_new_board(board_data: BoardCreate, user_id: int = Depends(user_service.get_userid_by_email)):
    return board_service.create_board(board_data, user_id)

@router.get("/boards/")
def get_all_boards(category_id: Optional[int] = None, category_type: Optional[str] = None):
    return board_service.get_boards(category_id, category_type)

@router.get("/boards/{board_id}/")
def get_board_by_id(board_id: int):
    return board_service.get_board(board_id)

@router.put("/boards/{board_id}/", status_code=200)
def update_board_by_id(board_id: int, board_data: BoardUpdate, user_id: int = Depends(user_service.get_userid_by_email)):
    return board_service.update_board(board_id, board_data, user_id)

@router.delete("/boards/{board_id}/", status_code=204)
def delete_board_by_id(board_id: int, user_id: int = Depends(user_service.get_userid_by_email)):
    return board_service.delete_board(board_id, user_id)

@router.post("/boards/{board_id}/comments/", status_code=201)
def create_new_comment(board_id: int, comment_data: CommentCreate, user_id: int = Depends(user_service.get_userid_by_email)):
    return board_service.create_comment(board_id, comment_data, user_id)

@router.get("/boards/{board_id}/comments/")
def get_comments_by_board_id(board_id: int):
    return board_service.get_comments(board_id)

@router.put("/comments/{comment_id}/", status_code=200)
def update_comment_by_id(comment_id: int, comment_data: CommentUpdate, user_id: int = Depends(user_service.get_userid_by_email)):
    return board_service.update_comment(comment_id, comment_data, user_id)

@router.delete("/comments/{comment_id}/", status_code=204)
def delete_comment_by_id(comment_id: int, user_id: int = Depends(user_service.get_userid_by_email)):
    return board_service.delete_comment(comment_id, user_id)