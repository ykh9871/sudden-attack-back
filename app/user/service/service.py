from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from app.user.repository.repository import UserRepository
from app.user.dto.dto import User, UserInfo
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours
        self.REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 1 month
        self.SECRET_KEY = "asdasdqweasdqwea"
        self.ALGORITHM = "HS256"

    def register(self, user: User):
        return self.user_repository.register(user)

    def get_user_info(self, email: str) -> UserInfo:
        return self.user_repository.get_user_info(email)

    def update_user_info(
        self, email: str, username: str, nickname: str, occupation_name: str
    ) -> None:
        return self.user_repository.update_user_info(
            email, username, nickname, occupation_name
        )

    def update_user_password(self, email: str, new_password: str) -> None:
        return self.user_repository.update_user_password(email, new_password)

    def withdrawal(self, email: str):
        return self.user_repository.withdrawal(email)

    def authenticate(self, email: str, password: str):
        return self.user_repository.authenticate(email, password)

    def get_userid_by_email(self, token: str = Depends(oauth2_scheme)):
        email = self.get_email_from_token(token)
        return self.user_repository.get_userid_by_email(email)

    def update_refresh_token(self, email: str, refresh_token: str):
        return self.user_repository.update_refresh_token(email, refresh_token)

    def create_access_token(self, username: str):
        data = {
            "sub": username,
            "exp": datetime.utcnow()
            + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        access_token = jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return access_token

    def create_refresh_token(self, username: str):
        data = {
            "sub": username,
            "exp": datetime.utcnow()
            + timedelta(minutes=self.REFRESH_TOKEN_EXPIRE_SECONDS),
        }
        refresh_token = jwt.encode(data, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return refresh_token

    def get_email_from_token(self, token: str = Depends(oauth2_scheme)):
        payload = jwt.decode(token, self.SECRET_KEY, self.ALGORITHM)
        return payload.get("sub")
