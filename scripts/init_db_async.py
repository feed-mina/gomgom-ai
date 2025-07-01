import asyncio
import asyncpg
import os
import sys

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

async def execute_sql_file(conn, file_path):
    """SQL 파일을 실행하는 함수"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql = file.read()
            await conn.execute(sql)
            # Print(f"Successfully executed: {file_path}")
    except Exception as e:
        # Print(f"Error executing {file_path}: {e}")
        raise

async def init_database():
    """데이터베이스 초기화 함수"""
    print("Starting database initialization...")
    
    # 기본 PostgreSQL 연결 (데이터베이스 생성용)
    try:
        # 기본 postgres 데이터베이스에 연결
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database='postgres'
        )

        # 데이터베이스가 없으면 생성
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = $1",
            settings.POSTGRES_DB
        )
        
        if not exists:
            await conn.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            # Print(f"Database '{settings.POSTGRES_DB}' created successfully")
        else:
            # Print(f"Database '{settings.POSTGRES_DB}' already exists")

        await conn.close()

        # 특정 데이터베이스에 연결
        conn = await asyncpg.connect(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB
        )

        # 초기 스키마 생성
        print("Creating initial schema...")
        await execute_sql_file(conn, "migrations/init.sql")
        print("Initial schema created successfully")

        # 인덱스 생성
        print("Creating indexes...")
        await execute_sql_file(conn, "migrations/add_indexes.sql")
        print("Indexes created successfully")

        # 테스트 데이터 삽입
        print("Inserting test data...")
        await execute_sql_file(conn, "migrations/seed_data.sql")
        print("Test data inserted successfully")

        await conn.close()
        print("Database initialization completed successfully!")

    except Exception as e:
        # Print(f"An error occurred during database initialization: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database()) 