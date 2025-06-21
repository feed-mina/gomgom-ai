from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리 찾기
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# .env 파일 로드 (프로젝트 루트의 .env 파일 우선)
load_dotenv(dotenv_path=ROOT_DIR / ".env")
# app 디렉토리의 .env 파일도 로드 (없으면 무시)
load_dotenv(dotenv_path=ROOT_DIR / "app" / ".env", override=True)

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GomGom AI"
    
    # OpenAI API 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 데이터베이스 설정 (FastApi settings.py와 동일하게)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres1234"  # 일반적인 기본 비밀번호
    POSTGRES_DB: str = "gomgomdb"  # FastApi와 동일
    POSTGRES_PORT: str = "5432"
    
    # 추가된 필드들 (환경 변수에서 로드되는 것들)
    POSTGRES_HOST: str = "localhost"
    DATABASE_URL: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT 설정
    SECRET_KEY: str = "django-insecure-k3=p4i=(mu-)*2w4d6-_)3h+w(o&sk5*tl)c-#n^%7(!w6co8@"
    JWT_SECRET_KEY: str = "d6ac9ecc0a3aa3c395313fb236e0ec10d71ab78fb36f54ba626664eba0b842b1"
    JWT_ISSUER: str = "admin"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    
    # Kakao API 설정
    KAKAO_REST_API: str = "ce290686267085588527fc7c5b9334b3"
    KAKAO_CLIENT_ID: str = "2d22c7fa1d59eb77a5162a3948a0b6fe"
    KAKAO_TOKEN_ADMIN: str = "96ed9105639fb627fb2c710f39e6516f"
    KAKAO_REDIRECT_URI: str = "http://localhost:4000/oauth/callback"

    # Redis 설정 (FastApi와 동일)
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    CACHE_ENABLED: bool = True

    # 로깅 설정
    LOG_LEVEL: str = "INFO"

    # 추가된 필드
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# API 키 검증
if not settings.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

kakao_key = settings.KAKAO_REST_API  # ✅ 정상 동작

 