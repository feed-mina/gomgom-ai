from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
# from app.core.cache import get_cache, set_cache, delete_cache

router = APIRouter()

@router.get("/", response_model=List[RecipeResponse])
def read_recipes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """
    레시피 목록을 조회합니다.
    """
    # cache_key = f"recipes:list:{skip}:{limit}:{search}"
    # cached_result = get_cache(cache_key)
    # if cached_result:
    #     return cached_result

    query = db.query(Recipe)
    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))
    
    recipes = query.offset(skip).limit(limit).all()
    # set_cache(cache_key, recipes)
    return recipes

@router.get("/{recipe_id}", response_model=RecipeResponse)
def read_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 레시피를 조회합니다.
    """
    # cache_key = f"recipe:{recipe_id}"
    # cached_result = get_cache(cache_key)
    # if cached_result:
    #     return cached_result

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    # set_cache(cache_key, recipe)
    return recipe

@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 레시피를 생성합니다.
    """
    db_recipe = Recipe(**recipe.dict())
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    # delete_cache("recipes:list:*")  # 캐시 무효화
    return db_recipe

@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db)
):
    """
    레시피를 수정합니다.
    """
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    for field, value in recipe.dict(exclude_unset=True).items():
        setattr(db_recipe, field, value)
    
    db.commit()
    db.refresh(db_recipe)
    # delete_cache(f"recipe:{recipe_id}")
    # delete_cache("recipes:list:*")
    return db_recipe

@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    레시피를 삭제합니다.
    """
    db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if db_recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    db.delete(db_recipe)
    db.commit()
    # delete_cache(f"recipe:{recipe_id}")
    # delete_cache("recipes:list:*")
    return {"message": "Recipe deleted successfully"} 