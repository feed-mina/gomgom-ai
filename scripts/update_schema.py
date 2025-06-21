#!/usr/bin/env python3
"""
Database Schema Update Script
"""

import psycopg2
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def update_schema():
    """데이터베이스 스키마를 업데이트합니다."""
    print("Updating database schema...")
    
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(
            dbname=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT
        )
        cursor = conn.cursor()

        # locations 테이블에 누락된 컬럼 추가
        print("Adding missing columns to locations table...")
        cursor.execute("""
            ALTER TABLE locations 
            ADD COLUMN IF NOT EXISTS phone VARCHAR,
            ADD COLUMN IF NOT EXISTS website VARCHAR,
            ADD COLUMN IF NOT EXISTS description TEXT
        """)

        # recipes 테이블에 누락된 컬럼 추가
        print("Adding missing columns to recipes table...")
        cursor.execute("""
            ALTER TABLE recipes 
            ADD COLUMN IF NOT EXISTS servings INTEGER DEFAULT 1,
            ADD COLUMN IF NOT EXISTS image_url VARCHAR
        """)

        # ingredients 테이블에 누락된 컬럼 추가
        print("Adding missing columns to ingredients table...")
        cursor.execute("""
            ALTER TABLE ingredients 
            ADD COLUMN IF NOT EXISTS category VARCHAR,
            ADD COLUMN IF NOT EXISTS image_url VARCHAR
        """)

        conn.commit()
        print("Database schema updated successfully!")

    except Exception as e:
        print(f"Error updating schema: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_schema() 