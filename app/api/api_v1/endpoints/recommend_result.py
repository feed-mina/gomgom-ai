from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict
import httpx
import json
import os
import random
import openai
from konlpy.tag import Okt
from app.core.cache import get_cache, set_cache
from app.schemas.recommendation import RecommendationResponse
import logging
from app.core.config import settings
import traceback

router = APIRouter()
okt = Okt()
logger = logging.getLogger("uvicorn.error")

# API 키 설정
openai.api_key = settings.OPENAI_API_KEY
logger.info(f"OPENAI_API_KEY: {settings.OPENAI_API_KEY}")

def extract_keywords_from_store_name(name: str) -> List[str]:
    keywords = [w for w, pos in okt.pos(name) if pos == 'Noun' and len(w) > 1]
    return keywords

def create_yogiyo_prompt_with_options(user_text: str, store_keywords_list: List[str], score: Optional[Dict] = None, input_type: str = "음식") -> str:
    if input_type == "기분":
        context = f'사용자의 현재 기분은 "{user_text}"입니다.'
        relevance = f'"{user_text}"일 때 먹으면 위로가 되거나 잘 어울리는 음식을 추천해주세요.'
    elif input_type == "상황":
        context = f'사용자의 상황은 "{user_text}"입니다.'
        relevance = f'"{user_text}"에 어울리는 음식 또는 분위기의 가게를 골라주세요.'
    else:
        context = f'사용자가 먹고 싶은 음식은 "{user_text}"입니다.'
        relevance = f'"{user_text}"와 가장 비슷하거나 관련 있는 음식을 추천해주세요.'

    prompt = f"""
    {context}
    사용자 입력 키워드: "{user_text}"

    아래는 현재 배달 가능한 음식점 리스트입니다. 각 줄은 "가게명: 키워드들" 형식입니다.
    ---
    {chr(10).join(store_keywords_list[:10])}
    ---

    조건:
    - {relevance}
    - 추천 이유를 감성적으로 한 줄로 써주세요.
    - 결과는 반드시 JSON 형식으로 아래처럼 주세요:
        {{
            "store": 음식점 이름,
            "description": 감성적 설명,
            "category": 대표 카테고리,
            "keywords": [관련 키워드1, 관련 키워드2, ...]
        }}
    """
    return prompt

def match_gpt_result_with_yogiyo(gpt_result: Dict, restaurants: List[Dict]) -> Optional[Dict]:
    import re
    def clean(s: str) -> str:
        return re.sub(r"[^가-힣a-zA-Z0-9]", "", s).replace(" ", "").lower()
    
    target = clean(gpt_result['store'])
    keywords = gpt_result.get("keywords", [])
    best_match = None
    
    for store in restaurants:
        name = store.get("name", "")
        cleaned = clean(name)
        if target in cleaned or cleaned in target:
            return store
        store_keywords = extract_keywords_from_store_name(name)
        if any(k in store_keywords for k in keywords):
            best_match = store
    return best_match

async def fetch_yogiyo_data(lat: float, lng: float) -> Dict:
    cache_key = f"restaurants_{lat}_{lng}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    url = "https://www.yogiyo.co.kr/api/v1/restaurants"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.yogiyo.co.kr/"
    }
    params = {
        "lat": lat,
        "lng": lng,
        "page": 0,
        "serving_type": "delivery"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 요기요 API 응답 데이터 구조 확인
        if isinstance(data, list) and len(data) > 0:
            first_restaurant = data[0]
            logger.info(f"[YOGIYO API] 첫 번째 레스토랑 데이터: {first_restaurant}")
            logger.info(f"[YOGIYO API] logo_url 필드: {first_restaurant.get('logo_url', 'NOT_FOUND')}")
            logger.info(f"[YOGIYO API] 사용 가능한 필드들: {list(first_restaurant.keys())}")
        
        if not isinstance(data, list):
            return {"restaurants": []}
            
        result = {"restaurants": data}
        set_cache(cache_key, result, timeout=900)  # 15분 캐시
        return result

@router.get("/", response_model=RecommendationResponse, tags=["recommend_result"])
async def recommend_result(
    text: Optional[str] = Query(None),
    lat: float = Query(...),
    lng: float = Query(...),
    mode: str = Query("recommend"),
    type1: Optional[str] = None,
    type2: Optional[str] = None,
    type3: Optional[str] = None,
    type4: Optional[str] = None,
    type5: Optional[str] = None,
    type6: Optional[str] = None
):
    print("==== recommend_result 진입 ====")
    logger.error("==== recommend_result 진입 ====")
    # 1. 캐시 확인
    print("1. 캐시 확인")
    cache_key = f"recommend_{mode}_{text}_{lat}_{lng}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    # 2. 요기요 데이터 가져오기
    print("2. 요기요 데이터 가져오기")
    data = await fetch_yogiyo_data(lat, lng)
    restaurants = data.get("restaurants", [])
    if not restaurants:
        raise HTTPException(status_code=404, detail="주변에 음식점이 없습니다.")

    # 3. 가게명+키워드 리스트 만들기
    print("3. 가게명+키워드 리스트 만들기")
    store_keywords_list = [
        f"{r.get('name')}: {', '.join(extract_keywords_from_store_name(r.get('name', '')))}"
        for r in restaurants
    ]
    random.shuffle(store_keywords_list)
    store_keywords_list = store_keywords_list[:10]

    # 4. GPT 프롬프트 생성
    print("4. GPT 프롬프트 생성")
    score = None
    if mode == "test":
        types = [t for t in [type1, type2, type3, type4, type5, type6] if t]
        score = {t: types.count(t) for t in types}
    
    prompt = create_yogiyo_prompt_with_options(text or "", store_keywords_list, score=score)

    # 5. GPT 호출 직전
    print("5. GPT 호출 직전")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        gpt_content = response.choices[0].message.content
        gpt_result = json.loads(gpt_content)
    except Exception as e:
        logger.error("GPT 호출 실패: %s", traceback.format_exc())
        print("GPT 호출 실패:", traceback.format_exc())  # 콘솔에도 강제 출력
        raise HTTPException(status_code=500, detail=f"GPT 호출 실패: {str(e)}")

    # 6. GPT 호출 성공
    print("6. GPT 호출 성공")
    # 6. 요기요 가게 리스트에서 best match 찾기
    best_match = match_gpt_result_with_yogiyo(gpt_result, restaurants)
    if not best_match:
        # Fallback: 랜덤 선택
        best_match = random.choice(restaurants)
        gpt_result = {
            "store": best_match.get("name", "추천 없음"),
            "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
            "category": ", ".join(best_match.get("categories", [])),
            "keywords": extract_keywords_from_store_name(best_match.get("name", ""))
        }

    # 7. 응답 데이터 구성
    print("7. 응답 데이터 구성")
    response_data = {
        "result": {
            "store": best_match.get("name", ""),
            "description": gpt_result.get("description", ""),
            "category": ", ".join(best_match.get("categories", [])),
            "keywords": gpt_result.get("keywords", []),
            "logo_url": best_match.get("logo_url", "")
        },
        "restaurants": [{
            "name": best_match.get("name", ""),
            "review_avg": str(best_match.get("review_avg", "5점")),
            "address": best_match.get("address", "주소 정보 없음"),
            "id": str(best_match.get("id", "ID 없음")),
            "categories": ", ".join(best_match.get("categories", [])),
            "logo_url": best_match.get("logo_url", "")
        }]
    }

    # 8. 모드별 추가 데이터
    if mode == "test":
        response_data.update({
            "text": text,
            "lat": lat,
            "lng": lng,
            "types": [t for t in [type1, type2, type3, type4, type5, type6] if t],
            "score": score
        })

    # 9. 캐시 저장
    set_cache(cache_key, response_data, timeout=1800)  # 30분 캐시

    return response_data
