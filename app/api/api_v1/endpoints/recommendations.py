from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Recommendation, Recipe
from app.schemas.recommendation import RecommendationCreate, RecommendationResponse
# from app.core.cache import get_cache, set_cache, delete_cache

router = APIRouter()

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
    # cache_key = f"recommendations:list:{skip}:{limit}:{user_id}"
    # cached_result = get_cache(cache_key)
    # if cached_result:
    #     return cached_result

    query = db.query(Recommendation)
    if user_id:
        query = query.filter(Recommendation.user_id == user_id)
    
    recommendations = query.offset(skip).limit(limit).all()
    # set_cache(cache_key, recommendations)
    return recommendations

@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def read_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 추천을 조회합니다.
    """
    # cache_key = f"recommendation:{recommendation_id}"
    # cached_result = get_cache(cache_key)
    # if cached_result:
    #     return cached_result

    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if recommendation is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # set_cache(cache_key, recommendation)
    return recommendation

@router.post("/", response_model=RecommendationResponse)
def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 추천을 생성합니다.
    """
    # 레시피 존재 여부 확인
    recipe = db.query(Recipe).filter(Recipe.id == recommendation.recipe_id).first()
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db_recommendation = Recommendation(**recommendation.dict())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    # delete_cache("recommendations:list:*")
    return db_recommendation

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
    # delete_cache(f"recommendation:{recommendation_id}")
    # delete_cache("recommendations:list:*")
    return {"message": "Recommendation deleted successfully"}

@router.get("/recommend_result/", response_model=RecommendationResponse)
async def recommend_result(
    text: Optional[str] = Query(None),
    lat: float = Query(...),
    lng: float = Query(...)
):
    # 여기에 추천 로직 구현 (예: GPT 호출, 요기요 API, DB 등)
    # 아래는 예시 더미 데이터
    if not lat or not lng:
        raise HTTPException(status_code=400, detail="위치 정보가 필요합니다.")

    # 실제 추천 결과를 반환해야 함
    return {
        "store": "예시치킨",
        "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
        "category": "치킨",
        "keywords": ["치킨", "프라이드"],
        "latitude": lat,
        "longitude": lng,
        "review_avg": 4.8,
        "review_count": 1234,
        "logo_url": "https://example.com/logo.png"
    } 