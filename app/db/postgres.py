import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from app.core.config import settings

@contextmanager
def get_db_connection():
    """
    PostgreSQL 데이터베이스 연결을 관리하는 컨텍스트 매니저
    """
    conn = psycopg2.connect(
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        cursor_factory=RealDictCursor
    )
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor(commit: bool = True):
    """
    데이터베이스 커서를 관리하는 컨텍스트 매니저
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()

# User 관련 함수
def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()

def create_user(email: str, hashed_password: str, full_name: str) -> Dict[str, Any]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (email, hashed_password, full_name)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (email, hashed_password, full_name)
        )
        return cursor.fetchone()

# Recipe 관련 함수
def get_recipe_by_id(recipe_id: int) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
        return cursor.fetchone()

def get_all_recipes(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM recipes ORDER BY id LIMIT %s OFFSET %s",
            (limit, skip)
        )
        return cursor.fetchall()

def create_recipe(name: str, description: str, instructions: str, cooking_time: int, difficulty: str) -> Dict[str, Any]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO recipes (name, description, instructions, cooking_time, difficulty)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
            """,
            (name, description, instructions, cooking_time, difficulty)
        )
        return cursor.fetchone()

# Ingredient 관련 함수
def get_ingredient_by_id(ingredient_id: int) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM ingredients WHERE id = %s", (ingredient_id,))
        return cursor.fetchone()

def get_all_ingredients(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM ingredients ORDER BY id LIMIT %s OFFSET %s",
            (limit, skip)
        )
        return cursor.fetchall()

def create_ingredient(name: str, price: float, unit: str) -> Dict[str, Any]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO ingredients (name, price, unit)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (name, price, unit)
        )
        return cursor.fetchone()

# Location 관련 함수
def get_location_by_id(location_id: int) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM locations WHERE id = %s", (location_id,))
        return cursor.fetchone()

def get_all_locations(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM locations ORDER BY id LIMIT %s OFFSET %s",
            (limit, skip)
        )
        return cursor.fetchall()

def create_location(name: str, address: str, latitude: float, longitude: float) -> Dict[str, Any]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO locations (name, address, latitude, longitude)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (name, address, latitude, longitude)
        )
        return cursor.fetchone()

# Recommendation 관련 함수
def get_recommendation_by_id(recommendation_id: int) -> Optional[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM recommendations WHERE id = %s", (recommendation_id,))
        return cursor.fetchone()

def get_user_recommendations(user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            SELECT r.*, rec.name as recipe_name
            FROM recommendations r
            JOIN recipes rec ON r.recipe_id = rec.id
            WHERE r.user_id = %s
            ORDER BY r.score DESC
            LIMIT %s OFFSET %s
            """,
            (user_id, limit, skip)
        )
        return cursor.fetchall()

def create_recommendation(user_id: int, recipe_id: int, score: float) -> Dict[str, Any]:
    with get_db_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO recommendations (user_id, recipe_id, score)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (user_id, recipe_id, score)
        )
        return cursor.fetchone() 