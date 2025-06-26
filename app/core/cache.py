import redis
import json
from typing import Any, Optional
import os
import logging
from functools import wraps
import hashlib
import psycopg2

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