import sqlite3
from fastapi import Depends
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from app.user.dto.dto import User, UserInfo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


class UserRepository:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.conn = sqlite3.connect("sudden-attack.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def register(self, user: User):
        self.cursor.execute(
            """
            SELECT occupation_name 
            FROM occupation 
            WHERE id = ?
            """,
            (user.occupation,),
        )
        occupation_name = self.cursor.fetchone()
        if occupation_name:
            hashed_password = self.hash_password(user.password)
            # 검색된 직업 id와 함께 사용자 정보를 삽입하는 쿼리 실행
            self.cursor.execute(
                """
                INSERT INTO user (username, email, password, nickname, occupation_id) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user.username,
                    user.email,
                    hashed_password,
                    user.nickname,
                    user.occupation,
                ),
            )
            self.conn.commit()
        else:
            # 직업명에 해당하는 id를 찾을 수 없는 경우 에러 처리
            raise ValueError("Invalid occupation")

    def get_user_info(self, email: str) -> UserInfo:
        self.cursor.execute(
            """
            SELECT u.username, u.nickname, u.email, o.occupation_name, u.created_at, u.modified_at 
            FROM user u 
            JOIN occupation o ON u.occupation_id = o.id 
            WHERE u.email=?
            """,
            (email,),
        )
        user = self.cursor.fetchone()
        if user:
            return UserInfo(
                username=user[0],
                nickname=user[1],
                email=user[2],
                occupation_name=user[3],
                created_at=user[4],
                modified_at=user[5],
            )
        return None

    def update_user_info(
        self, email: str, username: str, nickname: str, occupation_name: str
    ) -> None:
        # 직업 이름으로부터 직업 ID를 가져오는 쿼리 실행
        self.cursor.execute(
            """
            SELECT id 
            FROM occupation 
            WHERE occupation_name=?
            """,
            (occupation_name,),
        )
        occupation_id = self.cursor.fetchone()[0]
        # 사용자 정보 업데이트
        if occupation_id:
            modified_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.cursor.execute(
                """
                UPDATE user
                SET username=?, nickname=?, occupation_id=?, modified_at=?
                WHERE email=?
                """,
                (username, nickname, occupation_id, modified_at, email),
            )
            self.conn.commit()
        else:
            # 직업명에 해당하는 id를 찾을 수 없는 경우 에러 처리
            raise ValueError("Invalid occupation")

    def update_user_password(self, email: str, new_password: str) -> None:
        # 새로운 비밀번호를 해싱합니다.
        hashed_password = self.hash_password(new_password)
        # 수정된 날짜를 현재 시간으로 설정합니다.
        modified_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        # 사용자 비밀번호와 수정된 날짜를 업데이트합니다.
        self.cursor.execute(
            """
            UPDATE user
            SET password=?, modified_at=?
            WHERE email=?
            """,
            (hashed_password, modified_at, email),
        )
        self.conn.commit()

    def withdrawal(self, email: str):
        self.cursor.execute(
            """
            UPDATE user
            SET activate=0, deleted_at=?
            WHERE email=?
            """,
            (datetime.now().strftime("%Y-%m-%d %H:%M"), email),
        )
        self.conn.commit()

    def authenticate(self, email: str, password: str):
        self.cursor.execute(
            """
            SELECT * 
            FROM user 
            WHERE email=? 
                AND activate=1
            """,
            (email,),
        )
        user = self.cursor.fetchone()
        if user and self.verify_password(password, user[4]):
            return User(
                username=user[1],
                nickname=user[2],
                email=user[3],
                password=user[4],
                occupation=user[5],
            )
        return None

    def get_userid_by_email(self, email):
        self.cursor.execute(
            """
            SELECT id
            FROM user
            WHERE email = ?
            """,
            (email,),
        )
        userid = self.cursor.fetchone()
        return userid[0]

    def update_refresh_token(self, email: str, refresh_token: str):
        self.cursor.execute(
            """
            UPDATE user 
            SET refresh_token=? 
            WHERE email=?
            """,
            (refresh_token, email),
        )
        self.conn.commit()

    def hash_password(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
