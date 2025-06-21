# app/db/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import User, Recipe, Ingredient, Location, Recommendation

# ---------------------- User ----------------------
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str, full_name: str) -> User:
    user = User(email=email, hashed_password=hashed_password, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---------------------- Recipe ----------------------
def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[Recipe]:
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()

def get_all_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[Recipe]:
    return db.query(Recipe).offset(skip).limit(limit).all()

def create_recipe(db: Session, name: str, description: str, instructions: str, cooking_time: int, difficulty: str) -> Recipe:
    recipe = Recipe(
        name=name,
        description=description,
        instructions=instructions,
        cooking_time=cooking_time,
        difficulty=difficulty,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe

# ---------------------- Ingredient ----------------------
def get_ingredient_by_id(db: Session, ingredient_id: int) -> Optional[Ingredient]:
    return db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()

def get_all_ingredients(db: Session, skip: int = 0, limit: int = 100) -> List[Ingredient]:
    return db.query(Ingredient).offset(skip).limit(limit).all()

def create_ingredient(db: Session, name: str, price: float, unit: str) -> Ingredient:
    ingredient = Ingredient(name=name, price=price, unit=unit)
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient

# ---------------------- Location ----------------------
def get_location_by_id(db: Session, location_id: int) -> Optional[Location]:
    return db.query(Location).filter(Location.id == location_id).first()

def get_all_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
    return db.query(Location).offset(skip).limit(limit).all()

def create_location(db: Session, name: str, address: str, latitude: float, longitude: float) -> Location:
    location = Location(name=name, address=address, latitude=latitude, longitude=longitude)
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

# ---------------------- Recommendation ----------------------
def get_recommendation_by_id(db: Session, recommendation_id: int) -> Optional[Recommendation]:
    return db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()

def get_user_recommendations(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Recommendation]:
    return (
        db.query(Recommendation)
        .filter(Recommendation.user_id == user_id)
        .order_by(Recommendation.score.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_recommendation(db: Session, user_id: int, recipe_id: int, score: float) -> Recommendation:
    recommendation = Recommendation(user_id=user_id, recipe_id=recipe_id, score=score)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation
