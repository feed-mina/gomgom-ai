from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 데이터베이스 연결 설정 개선
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # 1시간마다 연결 재생성
    pool_timeout=30,
    echo=False  # SQL 로그 비활성화
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        # 연결 테스트
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 연결 오류: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_db_connection():
    """데이터베이스 연결 테스트"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("데이터베이스 연결 테스트 성공")
        return True
    except Exception as e:
        logger.error(f"데이터베이스 연결 테스트 실패: {e}")
        return False 