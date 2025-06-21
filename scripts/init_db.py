import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
import argparse

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def execute_sql_file(cursor, file_path):
    """SQL 파일을 실행하는 함수"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql = file.read()
            cursor.execute(sql)
            print(f"Successfully executed: {file_path}")
    except Exception as e:
        print(f"Error executing {file_path}: {e}")
        raise

def init_database(use_spatial=False):
    """데이터베이스 초기화 함수"""
    print("Starting database initialization...")
    
    # 기본 PostgreSQL 연결 (데이터베이스 생성용)
    try:
        conn = psycopg2.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # 데이터베이스가 없으면 생성
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{settings.POSTGRES_DB}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            print(f"Database '{settings.POSTGRES_DB}' created successfully")
        else:
            print(f"Database '{settings.POSTGRES_DB}' already exists")

        cursor.close()
        conn.close()

        # 특정 데이터베이스에 연결
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT
        )
        cursor = conn.cursor()

        # 초기 스키마 생성
        print("Creating initial schema...")
        execute_sql_file(cursor, "migrations/init.sql")
        print("Initial schema created successfully")

        # 인덱스 생성
        print("Creating indexes...")
        if use_spatial:
            print("Using spatial indexes with earthdistance extension...")
            execute_sql_file(cursor, "migrations/add_indexes_with_spatial.sql")
        else:
            print("Using standard indexes (no spatial extensions)...")
            execute_sql_file(cursor, "migrations/add_indexes.sql")
        print("Indexes created successfully")

        # 테스트 데이터 삽입
        print("Inserting test data...")
        execute_sql_file(cursor, "migrations/seed_data.sql")
        print("Test data inserted successfully")

        conn.commit()
        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize the database')
    parser.add_argument('--spatial', action='store_true', 
                       help='Use spatial indexes with earthdistance extension')
    
    args = parser.parse_args()
    init_database(use_spatial=args.spatial) 