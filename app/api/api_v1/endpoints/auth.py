from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import httpx
import json
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.models import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.core.cache import set_cache

router = APIRouter()

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 호환 토큰 로그인을 수행합니다.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register", response_model=UserResponse)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    새로운 사용자를 등록합니다.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    현재 로그인한 사용자의 정보를 조회합니다.
    """
    return current_user

@router.get("/kakao/login")
async def kakao_login():
    """
    카카오 로그인 URL을 반환합니다.
    """
    kakao_auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    return {"auth_url": kakao_auth_url}

@router.get("/kakao/callback")
async def kakao_callback(code: str, db: Session = Depends(get_db)):
    """
    카카오 OAuth 콜백을 처리합니다.
    """
    try:
        # 1. 인가 코드로 액세스 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_CLIENT_ID,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            access_token = token_info.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            
            # 2. 액세스 토큰으로 사용자 정보 요청
            user_info_url = "https://kapi.kakao.com/v2/user/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            user_response = await client.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # 3. 사용자 정보 추출 및 로깅
            kakao_id = str(user_info.get("id"))
            kakao_account = user_info.get("kakao_account", {})
            email = kakao_account.get("email")
            nickname = user_info.get("properties", {}).get("nickname", "카카오 사용자")
            
            # 디버깅을 위한 로그
            print(f"Kakao user info: {user_info}")
            print(f"Kakao account: {kakao_account}")
            print(f"Email: {email}")
            print(f"Nickname: {nickname}")
            
            # 이메일이 없는 경우 처리
            if not email:
                # 카카오 ID를 기반으로 임시 이메일 생성
                email = f"kakao_{kakao_id}@kakao.com"
                print(f"Generated email: {email}")
            
            # 4. 기존 사용자 확인 또는 새 사용자 생성
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # 새 사용자 생성 (카카오 ID를 비밀번호 대신 사용)
                user = User(
                    email=email,
                    hashed_password=get_password_hash(f"kakao_{kakao_id}"),  # 카카오 ID 기반 해시
                    full_name=nickname,
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"Created new user: {user.email}")
            else:
                print(f"Found existing user: {user.email}")

            # Redis에 사용자 정보 캐싱
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser
            }
            set_cache(f"user_id:{user.id}", user_data)
            
            # 5. JWT 토큰 생성
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            jwt_token = create_access_token(
                subject=user.id, expires_delta=access_token_expires
            )
            
            return {
                "access_token": jwt_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name
                }
            }
            
    except httpx.HTTPStatusError as e:
        print(f"HTTP error in Kakao callback: {e}")
        print(f"Response content: {e.response.content}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Kakao API error: {e}")
    except Exception as e:
        print(f"Unexpected error in Kakao callback: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/kakao/logout")
async def kakao_logout(request: Request):
    """
    카카오 로그아웃을 처리합니다.
    """
    # 실제 카카오 로그아웃은 프론트엔드에서 처리
    return {"message": "Logout successful"}

@router.get("/kakao/share")
async def get_kakao_share_info():
    """
    카카오 공유를 위한 정보를 반환합니다.
    """
    return {
        "app_key": settings.KAKAO_CLIENT_ID,
        "redirect_uri": settings.KAKAO_REDIRECT_URI
    } 