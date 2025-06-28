import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings
from app.db.postgres import get_db_connection, get_db_cursor

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()

def test_read_recipes():
    response = client.get("/api/v1/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]
    assert "description" in data[0]

def test_read_recipe():
    response = client.get("/api/v1/recipes/1")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "description" in data
    assert "instructions" in data

def test_read_ingredients():
    response = client.get("/api/v1/ingredients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]
    assert "price" in data[0]

def test_read_locations():
    response = client.get("/api/v1/locations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]
    assert "address" in data[0]

def test_read_recommendations():
    response = client.get("/api/v1/recommendations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "user_id" in data[0]
    assert "recipe_id" in data[0]
    assert "score" in data[0]

def test_create_recipe():
    recipe_data = {
        "name": "테스트 레시피",
        "description": "테스트용 레시피입니다.",
        "instructions": "1. 테스트\n2. 테스트",
        "cooking_time": 30,
        "difficulty": "쉬움"
    }
    response = client.post("/api/v1/recipes/", json=recipe_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == recipe_data["name"]
    assert data["description"] == recipe_data["description"]

def test_create_ingredient():
    ingredient_data = {
        "name": "테스트 재료",
        "price": 1000,
        "unit": "g"
    }
    response = client.post("/api/v1/ingredients/", json=ingredient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == ingredient_data["name"]
    assert data["price"] == ingredient_data["price"]

def test_create_location():
    location_data = {
        "name": "테스트 지점",
        "address": "서울시 테스트구 테스트로 123",
        "latitude": 37.5665,
        "longitude": 127.0280
    }
    response = client.post("/api/v1/locations/", json=location_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == location_data["name"]
    assert data["address"] == location_data["address"]

def test_create_recommendation():
    recommendation_data = {
        "user_id": 1,
        "recipe_id": 1,
        "score": 4.5
    }
    response = client.post("/api/v1/recommendations/", json=recommendation_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == recommendation_data["user_id"]
    assert data["recipe_id"] == recommendation_data["recipe_id"]
    assert data["score"] == recommendation_data["score"] 