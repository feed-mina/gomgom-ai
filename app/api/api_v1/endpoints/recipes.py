from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.db.session import get_db
from app.db.crud import get_all_recipes, search_recipes, get_recipes_with_recommendations, save_recommendation_history
from app.models.models import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.utils.external_apis import spoonacular_client
from app.core.cache import get_cache, set_cache, cache_result
from app.utils.translator import translator
import logging
# from app.core.cache import get_cache, set_cache, delete_cache

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[RecipeResponse])
@cache_result(timeout=300, key_prefix="recipes")
async def read_recipes(
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

        if search:
            recipes = search_recipes(db, search, skip, limit)
        else:
            recipes = get_all_recipes(db, skip, limit)
        
        if search:
            save_recommendation_history(
                db=db,
                user_id=None,  # 로그인 유저 정보가 있다면 user_id로 교체
                request_type="search_recipe",
                input_data={"search": search, "skip": skip, "limit": limit},
                result_data=[r.id for r in recipes]  # 또는 recipes 전체, 필요에 따라 조정
            )
        
        # set_cache(cache_key, recipes)
        logger.info(f"레시피 목록 조회 성공: {len(recipes)}개")
        return recipes
    
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.get("/with-recommendations", response_model=List[RecipeResponse])
@cache_result(timeout=180, key_prefix="recipes_with_recs")
async def read_recipes_with_recommendations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    추천 정보와 함께 레시피 목록을 조회합니다.
    """
    try:
        recipes = get_recipes_with_recommendations(db, skip, limit)
        logger.info(f"레시피 목록 조회 성공 (추천 포함): {len(recipes)}개")
        return recipes
    
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.get("/{recipe_id}", response_model=RecipeResponse)
@cache_result(timeout=600, key_prefix="recipe")
async def read_recipe(
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

        from app.db.crud import get_recipe_by_id
        recipe = get_recipe_by_id(db, recipe_id)
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
async def create_recipe(
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
        raise HTTPException(status_code=400, detail="중복된 레시피이거나 잘못된 데이터입니다.")
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 생성): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 생성): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: int,
    recipe: RecipeUpdate,
    db: Session = Depends(get_db)
):
    """
    레시피를 수정합니다.
    """
    try:
        from app.db.crud import get_recipe_by_id
        db_recipe = get_recipe_by_id(db, recipe_id)
        if db_recipe is None:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        update_data = recipe.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_recipe, field, value)
        
        db.commit()
        db.refresh(db_recipe)
        # delete_cache(f"recipe:{recipe_id}")
        # delete_cache("recipes:list:*")
        logger.info(f"레시피 수정 성공: ID {recipe_id}")
        return db_recipe
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (레시피 수정): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 수정): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.delete("/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db)
):
    """
    레시피를 삭제합니다.
    """
    try:
        from app.db.crud import get_recipe_by_id
        db_recipe = get_recipe_by_id(db, recipe_id)
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
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (레시피 삭제): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.get("/external/{recipe_id}")
async def get_external_recipe(recipe_id: int):
    """
    Spoonacular API에서 레시피 상세 정보를 가져옵니다.
    """
    try:
        # 캐시 키 생성
        cache_key = f"recipe_detail:{recipe_id}"
        
        # 캐시에서 결과 확인
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info(f"캐시에서 레시피 상세 정보 반환: ID {recipe_id}")
            return cached_result
        
        # 캐시에 없으면 API 호출
        recipe_info = await spoonacular_client.get_recipe_by_id(recipe_id)
        
        if not recipe_info:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        # 제목 번역
        if recipe_info.get("title"):
            recipe_info["title"] = await translator.translate_to_korean(recipe_info["title"])

        # 요약 번역
        if recipe_info.get("summary"):
            recipe_info["summary"] = await translator.translate_to_korean(recipe_info["summary"])

        # instructions 번역
        analyzed = recipe_info.get("analyzedInstructions")
        if analyzed and len(analyzed) > 0 and "steps" in analyzed[0]:
            for step in analyzed[0]["steps"]:
                step["step"] = await translator.translate_to_korean(step["step"])
                
                # 각 단계의 재료 이름 번역
                if step.get("ingredients"):
                    for ingredient in step["ingredients"]:
                        if ingredient.get("localizedName"):
                            ingredient["localizedName"] = await translator.translate_to_korean(ingredient["localizedName"])
                        if ingredient.get("name"):
                            ingredient["name"] = await translator.translate_to_korean(ingredient["name"])
                
                # 각 단계의 도구 이름 번역
                if step.get("equipment"):
                    for equipment in step["equipment"]:
                        if equipment.get("localizedName"):
                            equipment["localizedName"] = await translator.translate_to_korean(equipment["localizedName"])
                        if equipment.get("name"):
                            equipment["name"] = await translator.translate_to_korean(equipment["name"])
            
            # 프론트에서 사용하기 쉽게 배열로 가공
            recipe_info["instructions"] = [step["step"] for step in analyzed[0]["steps"]]
        elif isinstance(recipe_info.get("instructions"), str):
            recipe_info["instructions"] = await translator.translate_to_korean(recipe_info["instructions"])

        # 재료 번역 (선택)
        for ing in recipe_info.get("extendedIngredients", []):
            ing["name"] = await translator.translate_to_korean(ing["name"])
            ing["original"] = await translator.translate_to_korean(ing["original"])

        # 태그 번역
        if recipe_info.get("cuisines"):
            translated_cuisines = []
            for cuisine in recipe_info["cuisines"]:
                translated_cuisines.append(await translator.translate_to_korean(cuisine))
            recipe_info["cuisines"] = translated_cuisines

        if recipe_info.get("dishTypes"):
            translated_dish_types = []
            for dish_type in recipe_info["dishTypes"]:
                translated_dish_types.append(await translator.translate_to_korean(dish_type))
            recipe_info["dishTypes"] = translated_dish_types

        if recipe_info.get("diets"):
            translated_diets = []
            for diet in recipe_info["diets"]:
                translated_diets.append(await translator.translate_to_korean(diet))
            recipe_info["diets"] = translated_diets

        # 결과를 캐시에 저장 (2시간)
        set_cache(cache_key, recipe_info, timeout=7200)
        
        logger.info(f"외부 레시피 조회 성공: ID {recipe_id}")
        return recipe_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"외부 레시피 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="레시피 조회 중 오류가 발생했습니다.") 