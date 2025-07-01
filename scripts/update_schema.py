#!/usr/bin/env python3
"""
데이터베이스 스키마 업데이트 스크립트
Redis 캐시 데이터를 PostgreSQL에 저장하기 위한 cache_data 테이블 생성
"""

import psycopg2
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.config import settings

def create_cache_data_table():
    """cache_data 테이블 생성"""
    try:
        # PostgreSQL 연결
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            connect_timeout=10
        )
        
        with conn.cursor() as cursor:
            # cache_data 테이블 생성
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
            
            # 인덱스 생성
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_data_key ON cache_data(cache_key)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_data_type ON cache_data(data_type)
            """)
            
            # updated_at 트리거 함수가 없으면 생성
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql'
            """)
            
            # 트리거 생성
            cursor.execute("""
                DROP TRIGGER IF EXISTS update_cache_data_updated_at ON cache_data
            """)
            
            cursor.execute("""
                CREATE TRIGGER update_cache_data_updated_at
                    BEFORE UPDATE ON cache_data
                    FOR EACH ROW
                    EXECUTE FUNCTION update_updated_at_column()
            """)
            
            conn.commit()
            print("✅ cache_data 테이블 생성 완료")
            
            # 테이블 정보 확인
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'cache_data'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\n📋 cache_data 테이블 구조:")
            for col in columns:
                # Print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            return True
            
    except Exception as e:
        # Print(f"❌ cache_data 테이블 생성 실패: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def check_existing_data():
    """기존 캐시 데이터 확인"""
    try:
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            connect_timeout=10
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM cache_data")
            count = cursor.fetchone()[0]
            # Print(f"\n📊 현재 cache_data 테이블에 {count}개의 레코드가 있습니다.")
            
            if count > 0:
                cursor.execute("""
                    SELECT data_type, COUNT(*) 
                    FROM cache_data 
                    GROUP BY data_type 
                    ORDER BY COUNT(*) DESC
                """)
                
                types = cursor.fetchall()
                print("\n📈 데이터 타입별 분포:")
                for data_type, count in types:
                    # Print(f"  - {data_type}: {count}개")
            
            return True
            
    except Exception as e:
        # Print(f"❌ 데이터 확인 실패: {e}")
        return False
    finally:
        if conn:
            conn.close()

def main():
    """메인 함수"""
    print("🚀 데이터베이스 스키마 업데이트 시작")
    print("=" * 50)
    
    # 1. cache_data 테이블 생성
    if create_cache_data_table():
        print("\n✅ 스키마 업데이트 완료")
        
        # 2. 기존 데이터 확인
        check_existing_data()
        
        print("\n🎉 모든 작업이 완료되었습니다!")
        print("\n💡 이제 Redis 캐시 데이터가 PostgreSQL에도 자동으로 저장됩니다.")
        print("   - 빠른 조회: Redis에서 먼저 조회")
        print("   - 영구 저장: PostgreSQL에 백업 저장")
        print("   - 복구 기능: Redis 장애 시 PostgreSQL에서 복구")
    else:
        print("\n❌ 스키마 업데이트 실패")
        sys.exit(1)

if __name__ == "__main__":
    main() 