from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.db.session import get_db
from app.models.models import Recommendation, Recipe
from app.schemas.recommendation import RecommendationCreate, RecommendationResponse
from app.schemas.recipe import (
    RecipeResponse, RecipeSearchRequest, RecipeSearchResponse, 
    RecipeRecommendation, RecipeIngredient, RecipeInstruction
)
from app.utils.external_apis import spoonacular_client
from app.core.cache import get_cache, set_cache
import logging
import hashlib

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """
    API 상태를 확인합니다.
    """
    try:
        health_info = {
            "status": "healthy",
            "service": "recommendations",
            "message": "추천 서비스가 정상적으로 작동 중입니다."
        }
        logger.info("추천 서비스 헬스체크 완료")
        return health_info
    except Exception as e:
        logger.error(f"헬스체크 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="서비스 상태 확인 중 오류가 발생했습니다.")

@router.get("/search", response_model=RecipeSearchResponse)
async def search_recipes_get(
    query: str = Query(..., description="검색할 레시피 이름"),
    number: int = Query(10, ge=1, le=50, description="반환할 레시피 개수"),
    include_price: Optional[str] = Query("false", description="가격 정보 포함 여부"),
    max_cooking_time: Optional[int] = Query(None, ge=1, description="최대 조리 시간 (분)"),
    cuisine_type: Optional[str] = Query(None, description="요리 타입")
):
    """
    GET 요청으로 레시피를 검색합니다.
    """
    try:
        # include_price를 boolean으로 변환
        include_price_bool = include_price.lower() in ['true', '1', 'yes', 'on']
        
        # 캐시 키 생성
        cache_key = f"recipe_search:{hashlib.md5(f'{query}_{number}_{include_price_bool}_{max_cooking_time}_{cuisine_type}'.encode()).hexdigest()}"
        
        # 캐시에서 결과 확인
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info(f"캐시에서 검색 결과 반환: {query}")
            return cached_result
        
        # 캐시에 없으면 API 호출
        result = await _search_recipes_impl(query, number, include_price_bool, max_cooking_time, cuisine_type)
        
        # 결과를 캐시에 저장 (1시간으로 연장)
        set_cache(cache_key, result, timeout=3600)
        
        logger.info(f"레시피 검색 성공: {query}, {len(result.recipes)}개 결과")
        return result
    except ValueError as e:
        logger.error(f"매개변수 검증 오류: {e}")
        raise HTTPException(status_code=422, detail=f"매개변수 검증 오류: {str(e)}")
    except Exception as e:
        logger.error(f"레시피 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"레시피 검색 중 오류가 발생했습니다: {str(e)}")

@router.post("/search", response_model=RecipeSearchResponse)
async def search_recipes_post(
    request: RecipeSearchRequest
):
    """
    POST 요청으로 레시피를 검색합니다.
    """
    try:
        # 캐시 키 생성
        cache_key = f"recipe_search_post:{hashlib.md5(f'{request.query}_{request.number}_{request.include_price}_{request.max_cooking_time}_{request.cuisine_type}'.encode()).hexdigest()}"
        
        # 캐시에서 결과 확인
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.info(f"캐시에서 POST 검색 결과 반환: {request.query}")
            return cached_result
        
        # 캐시에 없으면 API 호출
        result = await _search_recipes_impl(
            request.query, 
            request.number, 
            request.include_price, 
            request.max_cooking_time, 
            request.cuisine_type
        )
        
        # 결과를 캐시에 저장 (1시간으로 연장)
        set_cache(cache_key, result, timeout=3600)
        
        logger.info(f"POST 레시피 검색 성공: {request.query}, {len(result.recipes)}개 결과")
        return result
    except Exception as e:
        logger.error(f"POST 레시피 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"레시피 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/recommend_result/", response_model=RecommendationResponse)
async def recommend_result(
    text: Optional[str] = Query(None),
    lat: float = Query(...),
    lng: float = Query(...)
):
    """
    추천 결과를 반환합니다.
    """
    try:
        # 위치 정보 검증
        if not lat or not lng:
            raise HTTPException(status_code=400, detail="위치 정보가 필요합니다.")
        
        # 좌표 범위 검증
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise HTTPException(status_code=400, detail="유효하지 않은 좌표입니다.")

        # RecommendationResponse 스키마에 맞는 구조로 반환
        result = {
            "result": {
                "store": "예시치킨",
                "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                "category": "치킨",
                "keywords": ["치킨", "프라이드"],
                "logo_url": "https://example.com/logo.png"
            },
            "restaurants": [
                {
                    "name": "예시치킨",
                    "review_avg": "4.8",
                    "address": "서울시 강남구",
                    "id": "1",
                    "categories": "치킨,양식",
                    "logo_url": "https://example.com/logo.png"
                },
                {
                    "name": "맛있는치킨",
                    "review_avg": "4.5",
                    "address": "서울시 서초구",
                    "id": "2",
                    "categories": "치킨,한식",
                    "logo_url": "https://example.com/logo2.png"
                }
            ],
            "text": text,
            "lat": lat,
            "lng": lng,
            "types": ["restaurant", "food"],
            "score": {"치킨": 5, "양식": 3}
        }
        
        logger.info(f"추천 결과 생성 성공: lat={lat}, lng={lng}, text={text}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"추천 결과 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="추천 결과 생성 중 오류가 발생했습니다.")

@router.get("/", response_model=List[RecommendationResponse])
def read_recommendations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None
):
    """
    추천 목록을 조회합니다.
    """
    try:
        cache_key = f"recommendations:list:{skip}:{limit}:{user_id}"
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.debug("캐시에서 추천 목록 반환")
            return cached_result

        query = db.query(Recommendation)
        if user_id:
            query = query.filter(Recommendation.user_id == user_id)
        
        recommendations = query.offset(skip).limit(limit).all()
        set_cache(cache_key, recommendations, timeout=300)  # 5분 캐시
        
        logger.info(f"추천 목록 조회 성공: {len(recommendations)}개")
        return recommendations
    
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (추천 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (추천 목록 조회): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def read_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 추천을 조회합니다.
    """
    try:
        cache_key = f"recommendation:{recommendation_id}"
        cached_result = get_cache(cache_key)
        if cached_result:
            logger.debug(f"캐시에서 추천 반환: ID {recommendation_id}")
            return cached_result

        recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if recommendation is None:
            raise HTTPException(status_code=404, detail="추천을 찾을 수 없습니다.")
        
        set_cache(cache_key, recommendation, timeout=600)  # 10분 캐시
        
        logger.info(f"추천 조회 성공: ID {recommendation_id}")
        return recommendation
    
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (추천 조회): {e}")
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (추천 조회): {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.post("/", response_model=RecommendationResponse)
def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 추천을 생성합니다.
    """
    try:
        # 레시피 존재 여부 확인
        recipe = db.query(Recipe).filter(Recipe.id == recommendation.recipe_id).first()
        if recipe is None:
            raise HTTPException(status_code=404, detail="레시피를 찾을 수 없습니다.")
        
        db_recommendation = Recommendation(**recommendation.dict())
        db.add(db_recommendation)
        db.commit()
        db.refresh(db_recommendation)
        
        # 관련 캐시 삭제
        # delete_cache("recommendations:list:*")
        
        logger.info(f"추천 생성 성공: ID {db_recommendation.id}")
        return db_recommendation
    
    except HTTPException:
        raise
    except IntegrityError as e:
        logger.error(f"데이터 무결성 오류 (추천 생성): {e}")
        db.rollback()
        raise HTTPException(status_code=400, detail="잘못된 데이터입니다.")
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 오류 (추천 생성): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="데이터베이스 오류가 발생했습니다.")
    except Exception as e:
        logger.error(f"예상치 못한 오류 (추천 생성): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="서버 내부 오류가 발생했습니다.")

@router.delete("/{recommendation_id}")
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    추천을 삭제합니다.
    """
    db_recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if db_recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    db.delete(db_recommendation)
    db.commit()
    
    # 관련 캐시 삭제
    from app.core.cache import delete_cache, clear_cache
    delete_cache(f"recommendation:{recommendation_id}")
    clear_cache("recommendations:list:*")
    
    return {"message": "Recommendation deleted successfully"}

async def _search_recipes_impl(
    query: str,
    number: int = 10,
    include_price: bool = False,
    max_cooking_time: Optional[int] = None,
    cuisine_type: Optional[str] = None
) -> RecipeSearchResponse:
    """
    레시피 검색 구현부
    """
    try:
        # Spoonacular API 호출 (한식 필터링 포함)
        recipes = await spoonacular_client.search_recipes(query, number, cuisine_type)
        
        # 프론트엔드가 기대하는 형식으로 변환
        recipe_list = []
        total_cost = 0.0
        
        for recipe in recipes:
            # 조리 시간 필터링
            cooking_time = recipe.get("readyInMinutes", 0)
            if max_cooking_time and cooking_time > max_cooking_time:
                continue
                
            # 재료 정보 변환
            ingredients = []
            for ingredient in recipe.get("extendedIngredients", []):
                ingredient_data = RecipeIngredient(
                    name=ingredient.get("name", ""),
                    amount=ingredient.get("amount", 0),
                    unit=ingredient.get("unit", "")
                )
                ingredients.append(ingredient_data)
            
            # 조리법 정보 변환
            instructions = []
            analyzed_instructions = recipe.get("analyzedInstructions", [])
            if analyzed_instructions and analyzed_instructions[0].get("steps"):
                for i, step in enumerate(analyzed_instructions[0]["steps"]):
                    instruction = RecipeInstruction(
                        step=step.get("step", ""),
                        number=step.get("number", i + 1)
                    )
                    instructions.append(instruction)
            
            # 레시피 추천 객체 생성
            recipe_recommendation = RecipeRecommendation(
                id=recipe.get("id", 0),
                title=recipe.get("title", ""),
                summary=recipe.get("summary", ""),
                image_url=recipe.get("image", ""),
                ingredients=ingredients,
                instructions=instructions,
                cooking_time=cooking_time,
                servings=recipe.get("servings", 1),
                difficulty=_calculate_difficulty(cooking_time, len(ingredients)),
                source="Spoonacular",
                currency="KRW"
            )
            
            recipe_list.append(recipe_recommendation)
        
        return RecipeSearchResponse(
            query=query,
            total_results=len(recipe_list),
            recipes=recipe_list,
            estimated_total_cost=total_cost if include_price else None,
            currency="KRW"
        )
        
    except Exception as e:
        logger.error(f"레시피 검색 중 오류 발생: {e}")
        logger.info("더미 데이터를 반환합니다.")
        
        # 더미 데이터 반환
        dummy_recipes = [
            RecipeRecommendation(
                id=1,
                title=f"{query} 레시피",
                summary=f"맛있는 {query} 만드는 방법입니다.",
                image_url="https://example.com/recipe1.jpg",
                ingredients=[
                    RecipeIngredient(name="주재료", amount=1, unit="개"),
                    RecipeIngredient(name="양념", amount=2, unit="큰술")
                ],
                instructions=[
                    RecipeInstruction(step="재료를 준비합니다.", number=1),
                    RecipeInstruction(step="양념을 만듭니다.", number=2),
                    RecipeInstruction(step="조리합니다.", number=3)
                ],
                cooking_time=30,
                servings=2,
                difficulty="보통",
                source="Dummy",
                currency="KRW"
            ),
            RecipeRecommendation(
                id=2,
                title=f"간단한 {query}",
                summary=f"누구나 쉽게 만들 수 있는 {query}입니다.",
                image_url="https://example.com/recipe2.jpg",
                ingredients=[
                    RecipeIngredient(name="기본재료", amount=3, unit="개"),
                    RecipeIngredient(name="소스", amount=1, unit="큰술")
                ],
                instructions=[
                    RecipeInstruction(step="재료를 씻습니다.", number=1),
                    RecipeInstruction(step="조리합니다.", number=2)
                ],
                cooking_time=20,
                servings=1,
                difficulty="쉬움",
                source="Dummy",
                currency="KRW"
            )
        ]
        
        return RecipeSearchResponse(
            query=query,
            total_results=len(dummy_recipes),
            recipes=dummy_recipes,
            estimated_total_cost=None,
            currency="KRW"
        )

def _calculate_difficulty(cooking_time: int, ingredient_count: int) -> str:
    """
    조리 시간과 재료 개수를 기반으로 난이도를 계산합니다.
    """
    if cooking_time <= 15 and ingredient_count <= 5:
        return "쉬움"
    elif cooking_time <= 45 and ingredient_count <= 10:
        return "보통"
    else:
        return "어려움" 