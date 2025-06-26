from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.db.session import get_db
from app.models.models import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
import logging
# from app.core.cache import get_cache, set_cache, delete_cache

logger = logging.getLogger(__name__)
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
    try:
        # cache_key = f"recipes:list:{skip}:{limit}:{search}"
        # cached_result = get_cache(cache_key)
        # if cached_result:
        #     return cached_result

        query = db.query(Recipe)
        if search:
            query = query.filter(Recipe.name.ilike(f"%{search}%"))
        
        recipes = query.offset(skip).limit(limit).all()
        # set_cache(cache_key, recipes)
        logger.info(f"레시피 목록 조회 성공: {len(recipes)}개")
        return recipes
    
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.get("/{recipe_id}", response_model=RecipeResponse)
def read_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 레시피를 조회합니다.
    """
    try:
        # cache_key = f"recipe:{recipe_id}"
        # cached_result = get_cache(cache_key)
        # if cached_result:
        #     return cached_result

        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if recipe is None:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        # set_cache(cache_key, recipe)
        logger.info(f"레시피 조회 성공: ID {recipe_id}")
        return recipe
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 조회): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 조회): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 레시피를 생성합니다.
    """
    try:
        db_recipe = Recipe(**recipe.dict())
        db.add(db_recipe)
        db.commit()
        db.refresh(db_recipe)
        # delete_cache("recipes:list:*")  # 캐시 무효화
        logger.info(f"레시피 생성 성공: ID {db_recipe.id}")
        return db_recipe
    
    except IntegrityError as e:
        logger.error(f"데이터 무결성 오류 (레시피 생성): {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="중복된 레시피이거나 잘못된 데이터입니다.")
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 생성): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 생성): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db)
):
    """
    레시피를 수정합니다.
    """
    try:
        db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if db_recipe is None:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        for field, value in recipe.dict(exclude_unset=True).items():
            setattr(db_recipe, field, value)
        
        db.commit()
        db.refresh(db_recipe)
        # delete_cache(f"recipe:{recipe_id}")
        # delete_cache("recipes:list:*")
        logger.info(f"레시피 수정 성공: ID {recipe_id}")
        return db_recipe
    
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"데이터 무결성 오류 (레시피 수정): {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="잘못된 데이터입니다.")
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 수정): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 수정): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    레시피를 삭제합니다.
    """
    try:
        db_recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if db_recipe is None:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        db.delete(db_recipe)
        db.commit()
        # delete_cache(f"recipe:{recipe_id}")
        # delete_cache("recipes:list:*")
        logger.info(f"레시피 삭제 성공: ID {recipe_id}")
        return {"message": "레시피가 성공적으로 삭제되었습니다."}
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 삭제): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 삭제): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.") 