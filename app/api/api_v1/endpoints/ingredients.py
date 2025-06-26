from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.db.postgres import get_ingredient_by_id, create_ingredient, get_all_ingredients
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db

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

class IngredientSearchResponse(BaseModel):
    ingredients: List[Ingredient]
    total: int
    query: str

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

@router.get("/search", response_model=IngredientSearchResponse)
def search_ingredients(
    query: str = Query(..., description="검색할 재료 이름"),
    limit: int = Query(5, ge=1, le=50, description="반환할 재료 개수"),
    db: Session = Depends(get_db)
):
    """
    재료를 검색합니다.
    """
    try:
        # 모든 재료를 가져와서 필터링 (실제로는 DB에서 검색해야 함)
        all_ingredients = get_all_ingredients()
        
        # 쿼리로 필터링 (대소문자 구분 없이)
        filtered_ingredients = [
            ingredient for ingredient in all_ingredients 
            if query.lower() in ingredient.name.lower()
        ]
        
        # limit만큼 반환
        result_ingredients = filtered_ingredients[:limit]
        
        return IngredientSearchResponse(
            ingredients=result_ingredients,
            total=len(result_ingredients),
            query=query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"재료 검색 중 오류가 발생했습니다: {str(e)}") 