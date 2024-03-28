from typing import Optional
from fastapi import Depends, HTTPException
from app.user.service.service import UserService
from app.board.repository.repository import BoardRepository
from app.board.dto.dto import BoardCreate, BoardUpdate, CommentCreate, CommentUpdate

user_service = UserService()

class BoardService:
    def __init__(self):
        self.board_repository = BoardRepository()

    def create_board(self, board_data: BoardCreate, user_id: int = Depends(user_service.get_userid_by_email)):
        return self.board_repository.create_board(board_data, user_id)

    def get_boards(self, category_id: Optional[int] = None, category_type: Optional[str] = None):
        return self.board_repository.get_boards(category_id, category_type)

    def get_board(self, board_id: int):
        return self.board_repository.get_board(board_id)

    def update_board(self, board_id: int, board_data: BoardUpdate, user_id: int = Depends(user_service.get_userid_by_email)):
        return self.board_repository.update_board(board_id, board_data, user_id)

    def delete_board(self, board_id: int, user_id: int = Depends(user_service.get_userid_by_email)):
        return self.board_repository.delete_board(board_id, user_id)

    def create_comment(self, board_id: int, comment_data: CommentCreate, user_id: int = Depends(user_service.get_userid_by_email)):
        return self.board_repository.create_comment(board_id, comment_data, user_id)

    def get_comments(self, board_id: int):
        return self.board_repository.get_comments(board_id)

    def update_comment(self, comment_id: int, comment_data: CommentUpdate, user_id: int = Depends(user_service.get_userid_by_email)):
        return self.board_repository.update_comment(comment_id, comment_data, user_id)

    def delete_comment(self, comment_id: int, user_id: int = Depends(user_service.get_userid_by_email)):
        return self.board_repository.delete_comment(comment_id, user_id)