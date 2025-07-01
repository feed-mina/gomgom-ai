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
from app.utils.korean_recipe_crawler import get_recipe_by_id as korean_recipe_crawler_get_recipe_by_id
# from app.core.cache import get_cache, set_cache, delete_cache
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

# 번역 헬퍼 함수들
async def _translate_title_async(recipe_info: dict, field: str):
    """제목 번역"""
    try:
        translated = await translator.translate_to_korean(recipe_info[field])
        recipe_info[field] = translated
    except Exception as e:
        logger.warning(f"제목 번역 실패: {e}")

async def _translate_field_async(recipe_info: dict, field: str, text: str):
    """필드 번역"""
    try:
        translated = await translator.translate_to_korean(text)
        recipe_info[field] = translated
    except Exception as e:
        logger.warning(f"{field} 번역 실패: {e}")

async def _translate_step_async(steps: list, index: int, text: str):
    """단계 번역"""
    try:
        translated = await translator.translate_to_korean(text)
        steps[index]["step"] = translated
    except Exception as e:
        logger.warning(f"단계 {index} 번역 실패: {e}")

async def _translate_ingredient_async(ingredients: list, index: int, text: str):
    """재료 번역"""
    try:
        translated = await translator.translate_to_korean(text)
        ingredients[index]["name"] = translated
    except Exception as e:
        logger.warning(f"재료 {index} 번역 실패: {e}")

async def _translate_cuisine_async(cuisines: list, index: int, text: str):
    """요리 타입 번역"""
    try:
        translated = await translator.translate_to_korean(text)
        cuisines[index] = translated
    except Exception as e:
        logger.warning(f"요리 타입 {index} 번역 실패: {e}")

async def _translate_dish_type_async(dish_types: list, index: int, text: str):
    """요리 종류 번역"""
    try:
        translated = await translator.translate_to_korean(text)
        dish_types[index] = translated
    except Exception as e:
        logger.warning(f"요리 종류 {index} 번역 실패: {e}")

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
        # logger.info(f"레시피 목록 조회 성공: {len(recipes)}개")
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
        # logger.info(f"레시피 목록 조회 성공 (추천 포함): {len(recipes)}개")
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
        # logger.info(f"레시피 조회 성공: ID {recipe_id}")
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
        # logger.info(f"레시피 생성 성공: ID {db_recipe.id}")
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
        # logger.info(f"레시피 수정 성공: ID {recipe_id}")
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
        # logger.info(f"레시피 삭제 성공: ID {recipe_id}")
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
async def get_external_recipe(recipe_id: str, translate: bool = Query(False, description="번역 여부")):
    """
    Spoonacular API에서 레시피 상세 정보를 가져옵니다.
    """
    try:
        # 캐시 키 생성 (번역 여부에 따라 다른 키 사용)
        cache_key = f"recipe_detail:{recipe_id}:translate_{translate}"
        
        # 캐시에서 결과 확인
        cached_result = get_cache(cache_key)
        if cached_result:
            # logger.info(f"캐시에서 레시피 상세 정보 반환: ID {recipe_id}, 번역={translate}")
            return cached_result
        
        # 캐시에 없으면 API 호출
        recipe_info = await spoonacular_client.get_recipe_by_id(recipe_id)
        
        if not recipe_info:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        # 번역이 요청된 경우에만 번역 수행
        if translate:
            # logger.info(f"번역 시작: ID {recipe_id}")
            
            # 배치 번역을 위한 텍스트 수집
            texts_to_translate = []
            text_mapping = []  # (타입, 인덱스, 필드) 튜플
            
            # 제목 번역
            if recipe_info.get("title"):
                texts_to_translate.append(recipe_info["title"])
                text_mapping.append(("title", 0, "title"))

            # 요약 번역 (HTML 태그 제거 후)
            if recipe_info.get("summary"):
                import re
                clean_summary = re.sub(r'<[^>]+>', '', recipe_info["summary"])
                texts_to_translate.append(clean_summary)
                text_mapping.append(("summary", 0, "summary"))

            # instructions 번역 (가장 중요한 부분만)
            analyzed = recipe_info.get("analyzedInstructions")
            if analyzed and len(analyzed) > 0 and "steps" in analyzed[0]:
                # 처음 3단계만 번역 (성능 최적화)
                steps_to_translate = analyzed[0]["steps"][:3]
                for i, step in enumerate(steps_to_translate):
                    if step.get("step"):
                        texts_to_translate.append(step["step"])
                        text_mapping.append(("step", i, "step"))
                
                # 프론트에서 사용하기 쉽게 배열로 가공
                recipe_info["instructions"] = [step["step"] for step in analyzed[0]["steps"]]
            elif isinstance(recipe_info.get("instructions"), str):
                # 문자열인 경우 처음 500자만 번역
                instructions_text = recipe_info["instructions"][:500]
                texts_to_translate.append(instructions_text)
                text_mapping.append(("instructions", 0, "instructions"))

            # 재료 번역 (처음 5개만)
            ingredients = recipe_info.get("extendedIngredients", [])
            for i, ing in enumerate(ingredients[:5]):
                if ing.get("name"):
                    texts_to_translate.append(ing["name"])
                    text_mapping.append(("ingredient", i, "name"))

            # 태그 번역 (처음 3개만)
            if recipe_info.get("cuisines"):
                cuisines = recipe_info["cuisines"][:3]
                for i, cuisine in enumerate(cuisines):
                    texts_to_translate.append(cuisine)
                    text_mapping.append(("cuisine", i, None))

            if recipe_info.get("dishTypes"):
                dish_types = recipe_info["dishTypes"][:3]
                for i, dish_type in enumerate(dish_types):
                    texts_to_translate.append(dish_type)
                    text_mapping.append(("dish_type", i, None))

            # 배치 번역 실행
            if texts_to_translate:
                try:
                    translated_texts = await asyncio.wait_for(
                        translator.translate_batch_to_korean(texts_to_translate),
                        timeout=30.0  # 30초 타임아웃
                    )
                    
                    # 번역 결과를 원래 위치에 적용
                    for i, (text_type, index, field) in enumerate(text_mapping):
                        if i < len(translated_texts):
                            translated_text = translated_texts[i]
                            
                            if text_type == "title":
                                recipe_info["title"] = translated_text
                            elif text_type == "summary":
                                recipe_info["summary"] = translated_text
                            elif text_type == "instructions":
                                recipe_info["instructions"] = translated_text
                            elif text_type == "step":
                                analyzed[0]["steps"][index]["step"] = translated_text
                            elif text_type == "ingredient":
                                ingredients[index]["name"] = translated_text
                            elif text_type == "cuisine":
                                recipe_info["cuisines"][index] = translated_text
                            elif text_type == "dish_type":
                                recipe_info["dishTypes"][index] = translated_text
                    
                    # logger.info(f"배치 번역 완료: ID {recipe_id}, {len(texts_to_translate)}개 텍스트")
                    
                except asyncio.TimeoutError:
                    logger.warning(f"번역 타임아웃: ID {recipe_id}, 원본 데이터 반환")
                except Exception as e:
                    logger.warning(f"번역 중 오류: {e}, 원본 데이터 반환")

        # 결과를 캐시에 저장 (번역 여부에 따라 다른 TTL)
        cache_timeout = 7200 if translate else 3600  # 번역된 경우 2시간, 원본은 1시간
        set_cache(cache_key, recipe_info, timeout=cache_timeout)
        
        # logger.info(f"외부 레시피 조회 성공: ID {recipe_id}, 번역={translate}")
        return recipe_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"외부 레시피 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="레시피 조회 중 오류가 발생했습니다.")

@router.get("/internal/{recipe_id}")
async def get_internal_recipe(recipe_id: str):
    """만개의레시피에서 레시피 상세 정보를 가져옵니다."""
    try:
        # 만개의레시피 크롤러에서 recipe_id로 상세 정보 반환
        recipe = await korean_recipe_crawler_get_recipe_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        # logger.info(f"만개의레시피 레시피 조회 성공: ID {recipe_id}")
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"만개의레시피 레시피 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="레시피 조회 중 오류가 발생했습니다.") 