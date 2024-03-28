from typing import List, Optional
from app.board.dto.dto import (
    BoardCreate, 
    BoardUpdate, 
    CommentCreate, 
    CommentUpdate, 
    Board, 
    Comment
)
from typing import List, Optional
import sqlite3

class BoardRepository:
    def __init__(self):
        self.conn = sqlite3.connect("sudden-attack.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def get_board(self, board_id: int) -> Optional[Board]:
        self.cursor.execute(
            """
            SELECT b.id, b.title, b.content, b.category_id, b.category_type, b.status, b.user_id, b.created_at
            FROM board b
            WHERE b.id = ?
            """,
            (board_id,)
        )
        result = self.cursor.fetchone()
        if result:
            return Board(*result)
        else:
            return None

    def get_boards(self, category_id: Optional[int] = None, category_type: Optional[str] = None) -> List[Board]:
        self.cursor.execute( 
            """
            SELECT b.id, b.title, b.content, b.category_id, b.category_type, b.status, b.user_id, b.created_at
            FROM board b
            WHERE (? IS NULL OR b.category_id = ?)
              AND (? IS NULL OR b.category_type = ?)
            """,
            (category_id, category_id, category_type, category_type)
        )
        results = self.cursor.fetchall()
        return [Board(*result) for result in results]

    def create_board(self, board_data: BoardCreate, user_id: int) -> int:
        self.cursor.execute(
            """
            INSERT INTO board (title, content, category_id, category_type, user_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (board_data.title, board_data.content, board_data.category_id, board_data.category_type, user_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def update_board(self, board_id: int, board_data: BoardUpdate, user_id: int) -> bool:
        self.cursor.execute(
            """
            UPDATE board
            SET title = ?, content = ?, category_id = ?, category_type = ?
            WHERE id = ? AND user_id = ?
            """,
            (board_data.title, board_data.content, board_data.category_id, board_data.category_type, board_id, user_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_board(self, board_id: int, user_id: int) -> bool:
        self.cursor.execute(
            """
            DELETE FROM board
            WHERE id = ? AND user_id = ?
            """,
            (board_id, user_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def create_comment(self, board_id: int, comment_data: CommentCreate, user_id: int) -> int:
        self.cursor.execute(
            """
            INSERT INTO board_comment (content, board_id, user_id)
            VALUES (?, ?, ?)
            """,
            (comment_data.content, board_id, user_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_comments(self, board_id: int) -> List[Comment]:
        self.cursor.execute(
            """
            SELECT c.id, c.content, c.user_id, c.board_id, c.created_at
            FROM board_comment c
            WHERE c.board_id = ?
            """,
            (board_id,)
        )
        results = self.cursor.fetchall()
        return [Comment(*result) for result in results]

    def update_comment(self, comment_id: int, comment_data: CommentUpdate, user_id: int) -> bool:
        self.cursor.execute(
            """
            UPDATE board_comment
            SET content = ?
            WHERE id = ? AND user_id = ?
            """,
            (comment_data.content, comment_id, user_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        self.cursor.execute(
            """
            DELETE FROM board_comment
            WHERE id = ? AND user_id = ?
            """,
            (comment_id, user_id)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0