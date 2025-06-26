#!/usr/bin/env python3
"""
Database Performance Optimization Script

This script optimizes database performance by:
1. Creating additional indexes
2. Analyzing table statistics
3. Vacuuming tables
4. Optimizing query performance
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """데이터베이스 연결"""
    return psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT
    )

def execute_sql_file(cursor, file_path):
    """SQL 파일 실행"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
            cursor.execute(sql_content)
        logger.info(f"SQL 파일 실행 완료: {file_path}")
    except Exception as e:
        logger.error(f"SQL 파일 실행 실패 {file_path}: {e}")
        raise

def create_performance_indexes(cursor):
    """성능 최적화 인덱스 생성"""
    logger.info("성능 최적화 인덱스 생성 중...")
    
    # 추가 성능 인덱스
    performance_indexes = [
        # 복합 인덱스
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recipes_difficulty_cooking_time ON recipes(difficulty, cooking_time);",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ingredients_category_price ON ingredients(category, price);",
        
        # 부분 인덱스 (조건부 인덱스)
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recipes_active ON recipes(id) WHERE difficulty IS NOT NULL;",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ingredients_available ON ingredients(id) WHERE price > 0;",
        
        # 함수 인덱스
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recipes_name_lower ON recipes(LOWER(name));",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ingredients_name_lower ON ingredients(LOWER(name));",
        
        # 시간 기반 인덱스
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recipes_recent ON recipes(created_at DESC) WHERE created_at > NOW() - INTERVAL '30 days';",
        "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recommendations_recent ON recommendations(created_at DESC) WHERE created_at > NOW() - INTERVAL '7 days';",
        
        # 공간 인덱스 (PostGIS 확장이 있는 경우)
        # "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_locations_geom ON locations USING GIST (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326));",
    ]
    
    for index_sql in performance_indexes:
        try:
            cursor.execute(index_sql)
            logger.info(f"인덱스 생성 완료: {index_sql[:50]}...")
        except Exception as e:
            logger.warning(f"인덱스 생성 실패: {e}")

def analyze_tables(cursor):
    """테이블 통계 분석"""
    logger.info("테이블 통계 분석 중...")
    
    tables = [
        'users', 'recipes', 'ingredients', 'ingredients_ko', 
        'locations', 'recommendations'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"ANALYZE {table};")
            logger.info(f"테이블 분석 완료: {table}")
        except Exception as e:
            logger.error(f"테이블 분석 실패 {table}: {e}")

def vacuum_tables(cursor):
    """테이블 정리 및 최적화"""
    logger.info("테이블 정리 및 최적화 중...")
    
    tables = [
        'users', 'recipes', 'ingredients', 'ingredients_ko', 
        'locations', 'recommendations'
    ]
    
    for table in tables:
        try:
            cursor.execute(f"VACUUM ANALYZE {table};")
            logger.info(f"테이블 정리 완료: {table}")
        except Exception as e:
            logger.error(f"테이블 정리 실패 {table}: {e}")

def optimize_query_performance(cursor):
    """쿼리 성능 최적화"""
    logger.info("쿼리 성능 최적화 중...")
    
    # 쿼리 플랜 캐시 정리
    try:
        cursor.execute("DISCARD PLANS;")
        logger.info("쿼리 플랜 캐시 정리 완료")
    except Exception as e:
        logger.warning(f"쿼리 플랜 캐시 정리 실패: {e}")
    
    # 통계 정보 업데이트
    try:
        cursor.execute("SELECT pg_stat_statements_reset();")
        logger.info("통계 정보 리셋 완료")
    except Exception as e:
        logger.warning(f"통계 정보 리셋 실패: {e}")

def check_database_health(cursor):
    """데이터베이스 상태 확인"""
    logger.info("데이터베이스 상태 확인 중...")
    
    # 테이블 크기 확인
    cursor.execute("""
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats 
        WHERE schemaname = 'public'
        ORDER BY tablename, attname;
    """)
    
    stats = cursor.fetchall()
    logger.info(f"통계 정보 조회 완료: {len(stats)}개 컬럼")
    
    # 인덱스 사용률 확인
    cursor.execute("""
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
    """)
    
    indexes = cursor.fetchall()
    logger.info(f"인덱스 사용률 조회 완료: {len(indexes)}개 인덱스")
    
    # 느린 쿼리 확인 (pg_stat_statements 확장이 있는 경우)
    try:
        cursor.execute("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements
            ORDER BY mean_time DESC
            LIMIT 10;
        """)
        
        slow_queries = cursor.fetchall()
        logger.info(f"느린 쿼리 조회 완료: {len(slow_queries)}개 쿼리")
        
        if slow_queries:
            logger.info("상위 10개 느린 쿼리:")
            for i, query in enumerate(slow_queries, 1):
                logger.info(f"{i}. 평균 시간: {query['mean_time']:.2f}ms, 호출 횟수: {query['calls']}")
    
    except Exception as e:
        logger.warning(f"느린 쿼리 조회 실패: {e}")

def main():
    """메인 함수"""
    logger.info("데이터베이스 성능 최적화 시작")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 성능 최적화 인덱스 생성
        create_performance_indexes(cursor)
        
        # 2. 테이블 통계 분석
        analyze_tables(cursor)
        
        # 3. 테이블 정리 및 최적화
        vacuum_tables(cursor)
        
        # 4. 쿼리 성능 최적화
        optimize_query_performance(cursor)
        
        # 5. 데이터베이스 상태 확인
        check_database_health(cursor)
        
        # 변경사항 커밋
        conn.commit()
        
        logger.info("데이터베이스 성능 최적화 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 최적화 중 오류 발생: {e}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 