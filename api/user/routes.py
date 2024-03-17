from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.user.service.service import UserService
from app.user.repository.repository import UserRepository
from app.user.dto.dto import User, UserInfo

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

user_service = UserService()
user_repository = UserRepository()


@router.post("/signup/")
async def register(user: User):
    user_service.register(user)
    return {"message": "User registered successfully"}


@router.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate(form_data.username, form_data.password)
    if user:
        access_token = user_service.create_access_token(user.email)
        refresh_token = user_service.create_refresh_token(user.email)
        user_repository.update_refresh_token(user.email, refresh_token)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": user.username,
            "refresh_token": refresh_token,
        }
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")


@router.get("/user/info/", response_model=UserInfo)
async def get_user_info(email: str = Depends(user_service.get_email_from_token)):
    if email:
        user_info = user_service.get_user_info(email)
        if user_info:
            return user_info
        else:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/user/info/")
async def update_user_info(
    user_info_request: UserInfo, email: str = Depends(user_service.get_email_from_token)
):
    if email:
        user_service.update_user_info(
            email,
            user_info_request.username,
            user_info_request.nickname,
            user_info_request.occupation_name,
        )
        return {"message": "User information updated successfully"}
    else:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.put("/user/password/")
async def update_user_password(
    current_password: str,
    new_password: str,
    email: str = Depends(user_service.get_email_from_token),
):
    user = user_service.authenticate(email, current_password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect current password")

    # 새로운 해싱된 비밀번호로 사용자 정보를 업데이트합니다.
    try:
        user_service.update_user_password(email, new_password)
        return {"message": "User password updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/user/withdrawal/")
async def withdrawal(
    password: str, email: str = Depends(user_service.get_email_from_token)
):
    # 사용자의 현재 비밀번호를 확인합니다.
    user = user_service.authenticate(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect password")
    try:
        # 사용자의 회원탈퇴를 처리합니다.
        user_service.withdrawal(email)
        return {"message": "User account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
