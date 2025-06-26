from typing import List, Union
from pydantic import AnyHttpUrl, validator, field_validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

load_dotenv()
# 프로젝트 루트 디렉토리 찾기
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
# .env 파일 로드 (프로젝트 루트의 .env 파일 우선)
load_dotenv(dotenv_path=ROOT_DIR / ".env")
# app 디렉토리의 .env 파일도 로드 (없으면 무시)
load_dotenv(dotenv_path=ROOT_DIR / "app" / ".env", override=True)

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GomGom AI"
    
    # OpenAI API 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Google Cloud 설정
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24시간 (24 * 60 = 1440분)

    
    # Kakao API 설정
    KAKAO_REST_API: str = "ce290686267085588527fc7c5b9334b3"
    KAKAO_CLIENT_ID: str = "ac17c741aa8131e12604eac5e2d0441c"
    # KAKAO_TOKEN_ADMIN: str = "96ed9105639fb627fb2c710f39e6516f"
    KAKAO_REDIRECT_URI: str = "http://localhost:3000/oauth/callback"

    # 외부 API 설정
    SPOONACULAR_API_KEY: str = "3ed0322a90654cac919bf1c1996d80a8"
    
    # 번역 API 설정 (Google Translate)
    GOOGLE_TRANSLATE_API_KEY: str = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
    
    # 크롤링 설정
    CRAWLING_DELAY: float = 1.0  # 크롤링 간격 (초)
    MAX_CRAWLING_RETRIES: int = 3

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

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow"
    }

settings = Settings()

# API 키 검증 - 더 유연한 처리
if not settings.OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY가 설정되지 않았습니다. OpenAI 관련 기능이 제한될 수 있습니다.")

# 데이터베이스 연결 확인
try:
    import psycopg2
    from psycopg2 import OperationalError
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD
    )
    conn.close()
    logger.info("PostgreSQL 데이터베이스 연결 성공")
except Exception as e:
    logger.error(f"PostgreSQL 데이터베이스 연결 실패: {e}")
    logger.warning("데이터베이스 연결이 실패했습니다. 일부 기능이 제한될 수 있습니다.")

# Redis 연결 확인
try:
    import redis
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    redis_client.ping()
    logger.info("Redis 연결 성공")
except Exception as e:
    logger.error(f"Redis 연결 실패: {e}")
    logger.warning("Redis 연결이 실패했습니다. 캐시 기능이 비활성화됩니다.")
    settings.CACHE_ENABLED = False

kakao_key = settings.KAKAO_REST_API  # ✅ 정상 동작

 