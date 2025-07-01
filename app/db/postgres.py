import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """
    PostgreSQL 데이터베이스 연결을 관리하는 컨텍스트 매니저
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            cursor_factory=RealDictCursor,
            connect_timeout=10
        )
        logger.debug("PostgreSQL 데이터베이스 연결 성공")
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"PostgreSQL 연결 오류: {e}")
        raise
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL 데이터베이스 오류: {e}")
        raise
    except Exception as e:
        logger.error(f"예상치 못한 데이터베이스 오류: {e}")
        raise
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("PostgreSQL 데이터베이스 연결 종료")
            except Exception as e:
                logger.error(f"데이터베이스 연결 종료 중 오류: {e}")

@contextmanager
def get_db_cursor(commit: bool = True):
    """
    데이터베이스 커서를 관리하는 컨텍스트 매니저
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
                    logger.debug("데이터베이스 트랜잭션 커밋 완료")
            except Exception as e:
                conn.rollback()
                logger.error(f"데이터베이스 트랜잭션 롤백: {e}")
                raise
            finally:
                cursor.close()
    except Exception as e:
        logger.error(f"데이터베이스 커서 생성 중 오류: {e}")
        raise

# User 관련 함수
def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """이메일로 사용자 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            logger.debug(f"사용자 조회 성공: {email}")
            return result
    except psycopg2.Error as e:
        logger.error(f"사용자 조회 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"사용자 조회 중 예상치 못한 오류: {e}")
        return None

def create_user(email: str, hashed_password: str, full_name: str) -> Optional[Dict[str, Any]]:
    """새 사용자 생성"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, hashed_password, full_name)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (email, hashed_password, full_name)
            )
            result = cursor.fetchone()
            # logger.info(f"사용자 생성 성공: {email}")
            return result
    except psycopg2.IntegrityError as e:
        logger.error(f"사용자 생성 중 무결성 오류 (중복 이메일): {e}")
        return None
    except psycopg2.Error as e:
        logger.error(f"사용자 생성 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"사용자 생성 중 예상치 못한 오류: {e}")
        return None

# Recipe 관련 함수
def get_recipe_by_id(recipe_id: int) -> Optional[Dict[str, Any]]:
    """ID로 레시피 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
            result = cursor.fetchone()
            logger.debug(f"레시피 조회 성공: ID {recipe_id}")
            return result
    except psycopg2.Error as e:
        logger.error(f"레시피 조회 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"레시피 조회 중 예상치 못한 오류: {e}")
        return None

def get_all_recipes(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """모든 레시피 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM recipes ORDER BY id LIMIT %s OFFSET %s",
                (limit, skip)
            )
            result = cursor.fetchall()
            logger.debug(f"레시피 목록 조회 성공: {len(result)}개")
            return result
    except psycopg2.Error as e:
        logger.error(f"레시피 목록 조회 중 데이터베이스 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"레시피 목록 조회 중 예상치 못한 오류: {e}")
        return []

def create_recipe(name: str, description: str, instructions: str, cooking_time: int, difficulty: str) -> Optional[Dict[str, Any]]:
    """새 레시피 생성"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO recipes (name, description, instructions, cooking_time, difficulty)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (name, description, instructions, cooking_time, difficulty)
            )
            result = cursor.fetchone()
            # logger.info(f"레시피 생성 성공: {name}")
            return result
    except psycopg2.IntegrityError as e:
        logger.error(f"레시피 생성 중 무결성 오류: {e}")
        return None
    except psycopg2.Error as e:
        logger.error(f"레시피 생성 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"레시피 생성 중 예상치 못한 오류: {e}")
        return None

# Ingredient 관련 함수
def get_ingredient_by_id(ingredient_id: int) -> Optional[Dict[str, Any]]:
    """ID로 재료 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
            result = cursor.fetchone()
            logger.debug(f"재료 조회 성공: ID {ingredient_id}")
            return result
    except psycopg2.Error as e:
        logger.error(f"재료 조회 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"재료 조회 중 예상치 못한 오류: {e}")
        return None

def get_all_ingredients(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """모든 재료 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM ingredients ORDER BY id LIMIT %s OFFSET %s",
                (limit, skip)
            )
            result = cursor.fetchall()
            logger.debug(f"재료 목록 조회 성공: {len(result)}개")
            return result
    except psycopg2.Error as e:
        logger.error(f"재료 목록 조회 중 데이터베이스 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"재료 목록 조회 중 예상치 못한 오류: {e}")
        return []

def create_ingredient(name: str, price: float, unit: str) -> Optional[Dict[str, Any]]:
    """새 재료 생성"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredients (name, price, unit)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (name, price, unit)
            )
            result = cursor.fetchone()
            # logger.info(f"재료 생성 성공: {name}")
            return result
    except psycopg2.IntegrityError as e:
        logger.error(f"재료 생성 중 무결성 오류: {e}")
        return None
    except psycopg2.Error as e:
        logger.error(f"재료 생성 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"재료 생성 중 예상치 못한 오류: {e}")
        return None

# Location 관련 함수
def get_location_by_id(location_id: int) -> Optional[Dict[str, Any]]:
    """ID로 위치 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM locations WHERE id = %s", (location_id,))
            result = cursor.fetchone()
            logger.debug(f"위치 조회 성공: ID {location_id}")
            return result
    except psycopg2.Error as e:
        logger.error(f"위치 조회 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"위치 조회 중 예상치 못한 오류: {e}")
        return None

def get_all_locations(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """모든 위치 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM locations ORDER BY id LIMIT %s OFFSET %s",
                (limit, skip)
            )
            result = cursor.fetchall()
            logger.debug(f"위치 목록 조회 성공: {len(result)}개")
            return result
    except psycopg2.Error as e:
        logger.error(f"위치 목록 조회 중 데이터베이스 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"위치 목록 조회 중 예상치 못한 오류: {e}")
        return []

def create_location(name: str, address: str, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """새 위치 생성"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO locations (name, address, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                RETURNING *
                """,
                (name, address, latitude, longitude)
            )
            result = cursor.fetchone()
            # logger.info(f"위치 생성 성공: {name}")
            return result
    except psycopg2.IntegrityError as e:
        logger.error(f"위치 생성 중 무결성 오류: {e}")
        return None
    except psycopg2.Error as e:
        logger.error(f"위치 생성 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"위치 생성 중 예상치 못한 오류: {e}")
        return None

# Recommendation 관련 함수
def get_recommendation_by_id(recommendation_id: int) -> Optional[Dict[str, Any]]:
    """ID로 추천 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM recommendations WHERE id = %s", (recommendation_id,))
            result = cursor.fetchone()
            logger.debug(f"추천 조회 성공: ID {recommendation_id}")
            return result
    except psycopg2.Error as e:
        logger.error(f"추천 조회 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"추천 조회 중 예상치 못한 오류: {e}")
        return None

def get_user_recommendations(user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """사용자의 추천 목록 조회"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT r.*, rec.name as recipe_name
                FROM recommendations r
                JOIN recipes rec ON r.recipe_id = rec.id
                WHERE r.user_id = %s
                ORDER BY r.score DESC
                LIMIT %s OFFSET %s
                """,
                (user_id, limit, skip)
            )
            result = cursor.fetchall()
            logger.debug(f"사용자 추천 목록 조회 성공: 사용자 {user_id}, {len(result)}개")
            return result
    except psycopg2.Error as e:
        logger.error(f"사용자 추천 목록 조회 중 데이터베이스 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"사용자 추천 목록 조회 중 예상치 못한 오류: {e}")
        return []

def create_recommendation(user_id: int, recipe_id: int, score: float) -> Optional[Dict[str, Any]]:
    """새 추천 생성"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO recommendations (user_id, recipe_id, score)
                VALUES (%s, %s, %s)
                RETURNING *
                """,
                (user_id, recipe_id, score)
            )
            result = cursor.fetchone()
            # logger.info(f"추천 생성 성공: 사용자 {user_id}, 레시피 {recipe_id}")
            return result
    except psycopg2.IntegrityError as e:
        logger.error(f"추천 생성 중 무결성 오류: {e}")
        return None
    except psycopg2.Error as e:
        logger.error(f"추천 생성 중 데이터베이스 오류: {e}")
        return None
    except Exception as e:
        logger.error(f"추천 생성 중 예상치 못한 오류: {e}")
        return None

def test_connection() -> bool:
    """
    데이터베이스 연결을 테스트하는 함수
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    # logger.info("PostgreSQL 연결 테스트 성공")
                    return True
                else:
                    logger.error("PostgreSQL 연결 테스트 실패: 예상치 못한 결과")
                    return False
    except Exception as e:
        logger.error(f"PostgreSQL 연결 테스트 실패: {e}")
        return False 