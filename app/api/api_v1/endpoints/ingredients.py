from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.db.postgres import get_ingredient_by_id, create_ingredient, get_all_ingredients
from pydantic import BaseModel

router = APIRouter()

class IngredientBase(BaseModel):
    name: str
    price: int
    unit: str

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[Ingredient])
def read_ingredients():
    ingredients = get_all_ingredients()
    return ingredients

@router.get("/{ingredient_id}", response_model=Ingredient)
def read_ingredient(ingredient_id: int):
    ingredient = get_ingredient_by_id(ingredient_id)
    if ingredient is None:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient

@router.post("/", response_model=Ingredient)
def create_new_ingredient(ingredient: IngredientCreate):
    db_ingredient = create_ingredient(
        name=ingredient.name,
        price=ingredient.price,
        unit=ingredient.unit
    )
    return db_ingredient 