import redis
import json
from typing import Any, Optional
import os
import logging
from functools import wraps
import hashlib
import psycopg2
from app.core.config import settings

logger = logging.getLogger(__name__)

class Cache:
    def __init__(self):
        try:
            # Redis 연결 풀 설정으로 성능 향상
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20,  # 연결 풀 크기 증가
                health_check_interval=30
            )
            # 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 캐시 서비스 초기화 성공")
        except Exception as e:
            logger.error(f"Redis 캐시 서비스 초기화 실패: {e}")
            self.redis_client = None

    def get_postgres_connection(self):
        """PostgreSQL 연결 반환"""
        try:
            conn = psycopg2.connect(
                dbname=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                host=settings.POSTGRES_SERVER,
                port=settings.POSTGRES_PORT,
                connect_timeout=10
            )
            return conn
        except Exception as e:
            logger.error(f"PostgreSQL 연결 실패: {e}")
            return None

    def save_to_postgresql(self, cache_key: str, data: Any, data_type: str = "cache_data"):
        """Redis 데이터를 PostgreSQL에 저장"""
        try:
            conn = self.get_postgres_connection()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                # cache_data 테이블이 없으면 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cache_data (
                        id SERIAL PRIMARY KEY,
                        cache_key VARCHAR(255) UNIQUE NOT NULL,
                        data_type VARCHAR(100) NOT NULL,
                        data JSONB NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 데이터 저장 또는 업데이트
                cursor.execute("""
                    INSERT INTO cache_data (cache_key, data_type, data, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (cache_key) 
                    DO UPDATE SET 
                        data = EXCLUDED.data,
                        updated_at = CURRENT_TIMESTAMP
                """, (cache_key, data_type, json.dumps(data, ensure_ascii=False)))
                
                conn.commit()
                logger.debug(f"PostgreSQL에 캐시 데이터 저장: {cache_key}")
                return True
                
        except Exception as e:
            logger.error(f"PostgreSQL 저장 실패: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def get_from_postgresql(self, cache_key: str) -> Optional[Any]:
        """PostgreSQL에서 캐시 데이터 조회"""
        try:
            conn = self.get_postgres_connection()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT data FROM cache_data 
                    WHERE cache_key = %s
                """, (cache_key,))
                
                result = cursor.fetchone()
                if result:
                    logger.debug(f"PostgreSQL에서 캐시 데이터 조회: {cache_key}")
                    return result[0] if isinstance(result[0], dict) else json.loads(result[0])
                return None
                
        except Exception as e:
            logger.error(f"PostgreSQL 조회 실패: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def save_recommendation_to_db(self, user_id: int, recipe_id: int, score: float, recommendation_data: dict):
        """추천 결과를 PostgreSQL recommendations 테이블에 저장"""
        try:
            conn = self.get_postgres_connection()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO recommendations (user_id, recipe_id, score, created_at, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, recipe_id) 
                    DO UPDATE SET 
                        score = EXCLUDED.score,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, recipe_id, score))
                
                conn.commit()
                logger.info(f"추천 결과를 PostgreSQL에 저장: user_id={user_id}, recipe_id={recipe_id}")
                return True
                
        except Exception as e:
            logger.error(f"추천 결과 PostgreSQL 저장 실패: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def save_recipe_to_db(self, recipe_data: dict):
        """레시피 데이터를 PostgreSQL recipes 테이블에 저장"""
        try:
            conn = self.get_postgres_connection()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO recipes (name, description, instructions, cooking_time, difficulty, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON CONFLICT (name) 
                    DO UPDATE SET 
                        description = EXCLUDED.description,
                        instructions = EXCLUDED.instructions,
                        cooking_time = EXCLUDED.cooking_time,
                        difficulty = EXCLUDED.difficulty,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """, (
                    recipe_data.get('name', ''),
                    recipe_data.get('description', ''),
                    recipe_data.get('instructions', ''),
                    recipe_data.get('cooking_time', 0),
                    recipe_data.get('difficulty', 'medium')
                ))
                
                recipe_id = cursor.fetchone()[0]
                conn.commit()
                logger.info(f"레시피를 PostgreSQL에 저장: {recipe_data.get('name')}")
                return recipe_id
                
        except Exception as e:
            logger.error(f"레시피 PostgreSQL 저장 실패: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def serialize_for_cache(self, obj: Any) -> str:
        """객체를 JSON 문자열로 직렬화"""
        try:
            if hasattr(obj, "model_dump"):
                obj = obj.model_dump()
            elif hasattr(obj, "dict"):
                obj = obj.dict()
            return json.dumps(obj, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"객체 직렬화 실패: {e}")
            raise

    def deserialize_from_cache(self, data: str) -> Any:
        """JSON 문자열을 객체로 역직렬화"""
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 역직렬화 실패: {e}")
            raise
        except Exception as e:
            logger.error(f"객체 역직렬화 실패: {e}")
            raise

    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성 (해시 기반)"""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])
        
        key_string = "|".join(key_parts)
        return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"캐시 히트: {key}")
                return self.deserialize_from_cache(data)
            logger.debug(f"캐시 미스: {key}")
            return None
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (get): {e}")
            return None
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (get): {e}")
            return None
        except Exception as e:
            logger.error(f"Redis 조회 중 오류 (get): {e}")
            return None

    async def set(self, key: str, value: Any, timeout: int = 1800) -> bool:
        """데이터를 캐시에 저장"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            serialized_value = self.serialize_for_cache(value)
            self.redis_client.setex(key, timeout, serialized_value)
            logger.debug(f"캐시 저장: {key} (TTL: {timeout}s)")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (set): {e}")
            return False
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (set): {e}")
            return False
        except Exception as e:
            logger.error(f"Redis 저장 중 오류 (set): {e}")
            return False

    async def mget(self, keys: list) -> list:
        """여러 키를 한 번에 조회 (성능 향상)"""
        if not self.redis_client:
            return [None] * len(keys)
        
        try:
            values = self.redis_client.mget(keys)
            return [self.deserialize_from_cache(v) if v else None for v in values]
        except Exception as e:
            logger.error(f"Redis mget 오류: {e}")
            return [None] * len(keys)

    async def mset(self, data: dict, timeout: int = 1800) -> bool:
        """여러 키를 한 번에 저장 (성능 향상)"""
        if not self.redis_client:
            return False
        
        try:
            pipeline = self.redis_client.pipeline()
            for key, value in data.items():
                serialized_value = self.serialize_for_cache(value)
                pipeline.setex(key, timeout, serialized_value)
            pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Redis mset 오류: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (delete): {e}")
            return False
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (delete): {e}")
            return False
        except Exception as e:
            logger.error(f"Redis 삭제 중 오류 (delete): {e}")
            return False

    async def clear(self, pattern: str = "*") -> bool:
        """패턴과 일치하는 모든 캐시 삭제"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"캐시 삭제 완료: {len(keys)}개 키")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (clear): {e}")
            return False
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (clear): {e}")
            return False
        except Exception as e:
            logger.error(f"Redis 전체 삭제 중 오류 (clear): {e}")
            return False

    # 동기 메서드들 추가
    def get_sync(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회 (동기)"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"캐시 히트: {key}")
                return self.deserialize_from_cache(data)
            logger.debug(f"캐시 미스: {key}")
            return None
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (get_sync): {e}")
            return None
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (get_sync): {e}")
            return None
        except Exception as e:
            logger.error(f"Redis 조회 중 오류 (get_sync): {e}")
            return None

    def set_sync(self, key: str, value: Any, timeout: int = 1800) -> bool:
        """데이터를 캐시에 저장 (동기)"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            serialized_value = self.serialize_for_cache(value)
            self.redis_client.setex(key, timeout, serialized_value)
            logger.debug(f"캐시 저장: {key} (TTL: {timeout}s)")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (set_sync): {e}")
            return False
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (set_sync): {e}")
            return False
        except Exception as e:
            logger.error(f"Redis 저장 중 오류 (set_sync): {e}")
            return False

    def delete_sync(self, key: str) -> bool:
        """캐시에서 데이터 삭제 (동기)"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (delete_sync): {e}")
            return False
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (delete_sync): {e}")
            return False
        except Exception as e:
            logger.error(f"Redis 삭제 중 오류 (delete_sync): {e}")
            return False

    def clear_sync(self, pattern: str = "*") -> bool:
        """패턴과 일치하는 모든 캐시 삭제 (동기)"""
        if not self.redis_client:
            logger.warning("Redis 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"캐시 삭제 완료: {len(keys)}개 키")
            return True
        except redis.ConnectionError as e:
            logger.error(f"Redis 연결 오류 (clear_sync): {e}")
            return False
        except redis.TimeoutError as e:
            logger.error(f"Redis 타임아웃 오류 (clear_sync): {e}")
            return False
        except Exception as e:
            logger.error(f"Redis 전체 삭제 중 오류 (clear_sync): {e}")
            return False

# 전역 캐시 인스턴스
_cache_instance = None

def get_cache_instance() -> Cache:
    """전역 캐시 인스턴스 반환 (싱글톤 패턴)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache()
    return _cache_instance

# 편의 함수들
def get_cache(key: str) -> Optional[Any]:
    return get_cache_instance().get_sync(key)

def set_cache(key: str, value: Any, timeout: int = 1800) -> bool:
    return get_cache_instance().set_sync(key, value, timeout)

def delete_cache(key: str) -> bool:
    return get_cache_instance().delete_sync(key)

def clear_cache(pattern: str = "*") -> bool:
    return get_cache_instance().clear_sync(pattern)

# Redis + PostgreSQL 통합 저장 함수들
def set_cache_with_db(key: str, value: Any, timeout: int = 1800, data_type: str = "cache_data") -> bool:
    """Redis와 PostgreSQL에 동시에 저장"""
    cache_instance = get_cache_instance()
    
    # Redis에 저장
    redis_success = cache_instance.set_sync(key, value, timeout)
    
    # PostgreSQL에 저장
    db_success = cache_instance.save_to_postgresql(key, value, data_type)
    
    if redis_success and db_success:
        logger.info(f"Redis와 PostgreSQL에 동시 저장 성공: {key}")
        return True
    elif redis_success:
        logger.warning(f"Redis만 저장 성공, PostgreSQL 저장 실패: {key}")
        return True
    else:
        logger.error(f"Redis 저장 실패: {key}")
        return False

def get_cache_with_db_fallback(key: str) -> Optional[Any]:
    """Redis에서 조회 실패 시 PostgreSQL에서 조회"""
    cache_instance = get_cache_instance()
    
    # 1. Redis에서 조회
    redis_data = cache_instance.get_sync(key)
    if redis_data is not None:
        return redis_data
    
    # 2. Redis에 없으면 PostgreSQL에서 조회
    logger.info(f"Redis 캐시 미스, PostgreSQL에서 조회: {key}")
    db_data = cache_instance.get_from_postgresql(key)
    
    if db_data is not None:
        # PostgreSQL에서 조회된 데이터를 Redis에 다시 캐싱
        cache_instance.set_sync(key, db_data, timeout=1800)
        logger.info(f"PostgreSQL에서 복구된 데이터를 Redis에 재캐싱: {key}")
        return db_data
    
    return None

def save_recommendation_with_cache(user_id: int, recipe_id: int, score: float, recommendation_data: dict) -> bool:
    """추천 결과를 Redis와 PostgreSQL에 동시 저장"""
    cache_instance = get_cache_instance()
    
    # Redis에 저장
    cache_key = f"recommendation:{user_id}:{recipe_id}"
    redis_success = cache_instance.set_sync(cache_key, recommendation_data, timeout=3600)
    
    # PostgreSQL에 저장
    db_success = cache_instance.save_recommendation_to_db(user_id, recipe_id, score, recommendation_data)
    
    if redis_success and db_success:
        logger.info(f"추천 결과 Redis+PostgreSQL 동시 저장 성공: user_id={user_id}, recipe_id={recipe_id}")
        return True
    elif redis_success:
        logger.warning(f"추천 결과 Redis만 저장 성공: user_id={user_id}, recipe_id={recipe_id}")
        return True
    else:
        logger.error(f"추천 결과 저장 실패: user_id={user_id}, recipe_id={recipe_id}")
        return False

def save_recipe_with_cache(recipe_data: dict) -> Optional[int]:
    """레시피를 Redis와 PostgreSQL에 동시 저장"""
    cache_instance = get_cache_instance()
    
    # PostgreSQL에 저장하여 ID 획득
    recipe_id = cache_instance.save_recipe_to_db(recipe_data)
    
    if recipe_id:
        # Redis에 저장
        cache_key = f"recipe:{recipe_id}"
        redis_success = cache_instance.set_sync(cache_key, recipe_data, timeout=7200)
        
        if redis_success:
            logger.info(f"레시피 Redis+PostgreSQL 동시 저장 성공: recipe_id={recipe_id}")
        else:
            logger.warning(f"레시피 PostgreSQL만 저장 성공, Redis 저장 실패: recipe_id={recipe_id}")
        
        return recipe_id
    else:
        logger.error(f"레시피 저장 실패: {recipe_data.get('name', 'Unknown')}")
        return None

# 캐시 데코레이터
def cache_result(timeout: int = 1800, key_prefix: str = "func"):
    """함수 결과를 캐시하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_instance = get_cache_instance()
            cache_key = cache_instance.generate_cache_key(key_prefix, func.__name__, *args, **kwargs)
            
            # 캐시에서 조회
            cached_result = await cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과 캐시
            await cache_instance.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

def init_database():
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="postgres1234",
        dbname="gomgomdb",
        port=5432,
        client_encoding="UTF8"
    )
    conn.set_client_encoding('UTF8')
    # 또는 conn.set_client_encoding('UTF8') 추가
    # ... 이하 생략 ... 

# 전역 cache 인스턴스 생성 (다른 파일에서 import할 수 있도록)
cache = get_cache_instance()