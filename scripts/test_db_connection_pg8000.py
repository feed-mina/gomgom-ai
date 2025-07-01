import pg8000
import sys
import os

# 프로젝트 루트 경로를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def test_connection():
    """PostgreSQL 연결을 테스트하는 함수 (pg8000 사용)"""
    print("Testing PostgreSQL connection with pg8000...")
    # Print(f"Host: {settings.POSTGRES_SERVER}")
    # Print(f"Port: {settings.POSTGRES_PORT}")
    # Print(f"User: {settings.POSTGRES_USER}")
    # Print(f"Password: {settings.POSTGRES_PASSWORD}")
    # Print(f"Database: {settings.POSTGRES_DB}")
    
    try:
        # 기본 postgres 데이터베이스에 연결 시도
        print("\n1. Testing connection to default 'postgres' database...")
        conn = pg8000.Connection(
            host=settings.POSTGRES_SERVER,
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database='postgres'
        )
        print("✓ Successfully connected to 'postgres' database")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        # Print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        # gomgomdb 데이터베이스 존재 여부 확인
        print("\n2. Checking if 'gomgomdb' database exists...")
        conn = pg8000.Connection(
            host=settings.POSTGRES_SERVER,
            port=int(settings.POSTGRES_PORT),
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database='postgres'
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'gomgomdb'")
        exists = cursor.fetchone()
        
        if exists:
            print("✓ Database 'gomgomdb' exists")
            
            # gomgomdb에 연결 시도
            cursor.close()
            conn.close()
            
            print("\n3. Testing connection to 'gomgomdb' database...")
            conn = pg8000.Connection(
                host=settings.POSTGRES_SERVER,
                port=int(settings.POSTGRES_PORT),
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database='gomgomdb'
            )
            print("✓ Successfully connected to 'gomgomdb' database")
            conn.close()
            
        else:
            print("✗ Database 'gomgomdb' does not exist")
            print("Creating 'gomgomdb' database...")
            cursor.execute('CREATE DATABASE gomgomdb')
            print("✓ Database 'gomgomdb' created successfully")
        
        cursor.close()
        conn.close()
        
        print("\n✓ All connection tests passed!")
        return True
        
    except Exception as e:
        # Print(f"\n✗ Connection test failed: {e}")
        # Print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_connection() 