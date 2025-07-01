#!/usr/bin/env python3
"""
Database Connection Test Script
"""

import psycopg2
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

def test_db_connection():
    """데이터베이스 연결과 테이블 상태를 확인합니다."""
    print("Testing database connection and tables...")
    
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

        # 테이블 목록 확인
        print("\n1. Checking tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print("Available tables:")
        for table in tables:
            # Print(f"  - {table[0]}")

        # locations 테이블 구조 확인
        print("\n2. Checking locations table structure...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'locations'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print("Locations table columns:")
        for col in columns:
            # Print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")

        # locations 테이블 데이터 확인
        print("\n3. Checking locations table data...")
        cursor.execute("SELECT COUNT(*) FROM locations")
        count = cursor.fetchone()[0]
        # Print(f"Locations count: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM locations LIMIT 3")
            rows = cursor.fetchall()
            print("Sample locations data:")
            for row in rows:
                # Print(f"  - {row}")

        # recipes 테이블 데이터 확인
        print("\n4. Checking recipes table data...")
        cursor.execute("SELECT COUNT(*) FROM recipes")
        count = cursor.fetchone()[0]
        # Print(f"Recipes count: {count}")

        # ingredients 테이블 데이터 확인
        print("\n5. Checking ingredients table data...")
        cursor.execute("SELECT COUNT(*) FROM ingredients")
        count = cursor.fetchone()[0]
        # Print(f"Ingredients count: {count}")

        print("\nDatabase connection test completed successfully!")

    except Exception as e:
        # Print(f"Error: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_db_connection() 