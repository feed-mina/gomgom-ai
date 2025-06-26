# app/db/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from app.models.models import User, Recipe, Ingredient, Location, Recommendation

# ---------------------- User ----------------------
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: dict) -> User:
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ---------------------- Recipe ----------------------
def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()

def get_all_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
    return db.query(Recipe).offset(skip).limit(limit).all()

def search_recipes(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Recipe]:
    """전문 검색을 사용한 레시피 검색"""
    return (
        db.query(Recipe)
        .filter(
            func.to_tsvector('english', Recipe.name + ' ' + func.coalesce(Recipe.description, ''))
            .op('@@')(func.plainto_tsquery('english', search_term))
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_recipes_with_recommendations(db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
    """추천 정보와 함께 레시피 조회 (eager loading)"""
    return (
        db.query(Recipe)
        .options(selectinload(Recipe.recommendations))
        .offset(skip)
        .limit(limit)
        .all()
    )

# ---------------------- Ingredient ----------------------
def get_ingredient_by_id(db: Session, ingredient_id: int) -> Optional[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

def get_all_ingredients(db: Session, skip: int = 0, limit: int = 100) -> List[Ingredient]:
    return db.query(Ingredient).offset(skip).limit(limit).all()

def search_ingredients(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[Ingredient]:
    """재료 검색 (한글명 포함)"""
    return (
        db.query(Ingredient)
        .outerjoin(Ingredient.korean_names)
        .filter(
            (Ingredient.name.ilike(f"%{search_term}%")) |
            (Ingredient.korean_names.any(name=search_term))
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

# ---------------------- Location ----------------------
def get_location_by_id(db: Session, location_id: int) -> Optional[Location]:
    return db.query(Location).filter(Location.id == location_id).first()

def get_all_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
    return db.query(Location).offset(skip).limit(limit).all()

def get_nearby_locations(db: Session, lat: float, lng: float, radius_km: float = 5.0, limit: int = 50) -> List[Location]:
    """주변 위치 검색 (간단한 거리 계산)"""
    # Haversine 공식을 사용한 거리 계산
    distance_formula = func.sqrt(
        func.pow(func.cos(func.radians(lat)) * func.cos(func.radians(Location.latitude)) * 
                func.cos(func.radians(Location.longitude) - func.radians(lng)) + 
                func.sin(func.radians(lat)) * func.sin(func.radians(Location.latitude)), 2)
    )
    
    return (
        db.query(Location, distance_formula.label('distance'))
        .filter(distance_formula <= radius_km / 6371.0)  # 지구 반지름으로 나누어 정규화
        .order_by(distance_formula)
        .limit(limit)
        .all()
    )

# ---------------------- Recommendation ----------------------
def get_recommendation_by_id(db: Session, recommendation_id: int) -> Optional[Recommendation]:
    return db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()

def get_user_recommendations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Recommendation]:
    """사용자 추천 목록 조회 (eager loading)"""
    return (
        db.query(Recommendation)
        .options(
            joinedload(Recommendation.recipe),
            joinedload(Recommendation.user)
        )
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.score.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_top_recommendations(db: Session, limit: int = 10) -> List[Recommendation]:
    """상위 추천 목록 조회"""
    return (
        db.query(Recommendation)
        .options(
            joinedload(Recommendation.recipe),
            joinedload(Recommendation.user)
        )
        .order_by(Recommendation.score.desc())
        .limit(limit)
        .all()
    )

def create_recommendation(db: Session, recommendation_data: dict) -> Recommendation:
    db_recommendation = Recommendation(**recommendation_data)
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation
