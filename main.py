from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정
origins = [
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# SQLite 연결
conn = sqlite3.connect("sudden-attack.db")
cursor = conn.cursor()

# JWT 설정
SECRET_KEY = "asdasdqweasdqwea"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours
REFRESH_TOKEN_EXPIRE_MONTHS = 3
REFRESH_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 30  # 1 month

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer를 사용하여 토큰을 가져올 수 있도록 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 사용자 모델 정의
class User(BaseModel):
    username: str
    email: str
    password: str
    nickname: str
    refresh_token: Optional[str] = None


# 토큰 생성
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # 기본적으로 15분
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# 비밀번호 해싱
def hash_password(password: str):
    return pwd_context.hash(password)


# 비밀번호 확인
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# 회원가입 API
@app.post("/signup/")
async def register(user: User):
    hashed_password = hash_password(user.password)
    cursor.execute(
        "INSERT INTO user (username, email, password, nickname) VALUES (?, ?, ?, ?)",
        (user.username, user.email, hashed_password, user.nickname),
    )
    conn.commit()
    return {"message": "User registered successfully"}


# 로그인 API
@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("SELECT * FROM user WHERE email=?", (form_data.username,))
    user = cursor.fetchone()
    if user and verify_password(form_data.password, user[3]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            {"sub": user[1]}, expires_delta=access_token_expires
        )
        refresh_token_expires = timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
        refresh_token = create_access_token(
            {"sub": user[1]}, expires_delta=refresh_token_expires
        )
        cursor.execute(
            "UPDATE user SET refresh_token=? WHERE email=?", (refresh_token, user[2])
        )
        conn.commit()
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")


# 보호된 리소스에 접근하는 API
@app.get("/protected-resource/")
async def protected_resource(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username:
            return {"message": f"Welcome {username}!"}
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
