import redis
import json
from typing import Any, Optional
import os

class Cache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )

    def serialize_for_cache(self, obj: Any) -> str:
        if hasattr(obj, "model_dump"):
            obj = obj.model_dump()
        return json.dumps(obj, ensure_ascii=False)

    def deserialize_from_cache(self, data: str) -> Any:
        """JSON 문자열을 객체로 역직렬화"""
        return json.loads(data)

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        data = self.redis_client.get(key)
        if data:
            return self.deserialize_from_cache(data)
        return None

    async def set(self, key: str, value: Any, timeout: int = 1800) -> None:
        """데이터를 캐시에 저장"""
        self.redis_client.setex(
            key,
            timeout,
            self.serialize_for_cache(value)
        )

    async def delete(self, key: str) -> None:
        """캐시에서 데이터 삭제"""
        self.redis_client.delete(key)

    async def clear(self, pattern: str = "*") -> None:
        """패턴과 일치하는 모든 캐시 삭제"""
        for key in self.redis_client.keys(pattern):
            self.redis_client.delete(key)

    # 동기 메서드들 추가
    def get_sync(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회 (동기)"""
        data = self.redis_client.get(key)
        if data:
            return self.deserialize_from_cache(data)
        return None

    def set_sync(self, key: str, value: Any, timeout: int = 1800) -> None:
        """데이터를 캐시에 저장 (동기)"""
        self.redis_client.setex(
            key,
            timeout,
            self.serialize_for_cache(value)
        )

    def delete_sync(self, key: str) -> None:
        """캐시에서 데이터 삭제 (동기)"""
        self.redis_client.delete(key)

    def clear_sync(self, pattern: str = "*") -> None:
        """패턴과 일치하는 모든 캐시 삭제 (동기)"""
        for key in self.redis_client.keys(pattern):
            self.redis_client.delete(key)

# 전역 캐시 객체 생성
cache = Cache()

# 기존 함수들은 캐시 객체의 메서드를 호출하도록 수정
def get_cache(key: str) -> Optional[Any]:
    return cache.get_sync(key)

def set_cache(key: str, value: Any, timeout: int = 1800) -> None:
    return cache.set_sync(key, value, timeout)

def delete_cache(key: str) -> None:
    return cache.delete_sync(key)

def clear_cache(pattern: str = "*") -> None:
    return cache.clear_sync(pattern)

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