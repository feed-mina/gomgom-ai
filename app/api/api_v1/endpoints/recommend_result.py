from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict
import httpx
import json
import os
import random
import openai
from konlpy.tag import Okt
from app.core.cache import get_cache, set_cache, set_cache_with_db, save_recommendation_with_cache
from app.schemas.recommendation import RecommendationResponse
import logging
from app.core.config import settings
import traceback
from app.utils.prompt_creator import create_yogiyo_prompt_with_options, make_store_info_line, classify_user_input_via_gpt
from app.db.session import SessionLocal
from app.models.models import RecommendationHistory  # 새 모델 생성 필요
from sqlalchemy.orm import Session
from app.db.crud import save_recommendation_history

router = APIRouter()
okt = Okt()
logger = logging.getLogger("uvicorn.error")

# API 키 설정
openai.api_key = settings.OPENAI_API_KEY
# logger.info(f"OPENAI_API_KEY: {settings.OPENAI_API_KEY}")

def extract_keywords_from_store_name(name: str) -> List[str]:
    keywords = [w for w, pos in okt.pos(name) if pos == 'Noun' and len(w) > 1]
    return keywords

def create_yogiyo_prompt_with_options(user_text: str, store_keywords_list: List[str], score: Optional[Dict] = None, input_type: str = "음식") -> str:
    if input_type == "기분":
        context = f'사용자의 현재 기분은 "{user_text}"입니다.'
        relevance = f'"{user_text}"일 때 위로가 되거나 잘 어울리는 음식을 추천해주세요.'
    elif input_type == "상황":
        context = f'사용자의 상황은 "{user_text}"입니다.'
        relevance = f'"{user_text}"에 어울리는 음식 또는 분위기의 가게를 골라주세요.'
    elif input_type == "음식":
        context = f'사용자가 먹고 싶은 음식은 "{user_text}"입니다.'
        relevance = f'"{user_text}"와 가장 비슷하거나 관련 있는 음식을 추천해주세요.'
    else:
        context = f'사용자의 입력은 "{user_text}"입니다.'
        relevance = f'"{user_text}"라는 키워드를 듣고 어울리는 음식을 추천해주세요.'

    prompt = f"""
    {context}
    사용자 입력 키워드: "{user_text}"

    아래는 현재 배달 가능한 음식점 리스트입니다. 각 줄은 "가게명: 키워드, 카테고리, 대표메뉴" 형식입니다.
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
            # logger.info(f"[YOGIYO API] 첫 번째 레스토랑 데이터: {first_restaurant}")
            # logger.info(f"[YOGIYO API] logo_url 필드: {first_restaurant.get('logo_url', 'NOT_FOUND')}")
            # logger.info(f"[YOGIYO API] 사용 가능한 필드들: {list(first_restaurant.keys())}")
        
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
    type6: Optional[str] = None,
    dummy: Optional[str] = Query(None)
):
    if text == 'none':
        text = None
    print("==== recommend_result 진입 ====")
    logger.error("==== recommend_result 진입 ====")
    try:
        print("1. 캐시 확인")
        cache_key = f"recommend_{mode}_{text}_{lat}_{lng}_{dummy}"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        print("2. 요기요 데이터 가져오기")
        data = await fetch_yogiyo_data(lat, lng)
        restaurants = data.get("restaurants", [])
        if not restaurants:
            return {
                "result": None,
                "restaurants": [],
                "error": "주변에 음식점이 없습니다."
            }

        print("3. 가게 정보 리스트 만들기")
        store_info_list = [make_store_info_line(r) for r in restaurants]
        random.shuffle(store_info_list)
        store_info_list = store_info_list[:10]

        print("4. 입력 분류 GPT 호출")
        input_type = await classify_user_input_via_gpt(text or "")

        print("5. GPT 프롬프트 생성")
        score = None
        if mode == "test":
            types = [t for t in [type1, type2, type3, type4, type5, type6] if t]
            score = {t: types.count(t) for t in types}
        prompt = create_yogiyo_prompt_with_options(text or "", store_info_list, score=score, input_type=input_type) + f"\n#dummy={dummy or random.random()}"

        print("6. GPT 호출")
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 사용자의 요구사항을 정확히 파악하여 최적의 음식점을 추천하는 전문가입니다. 항상 JSON 형식으로 정확하게 응답하고, 사용자 요청과 직접적으로 관련된 음식점만 추천합니다."},
                    {"role": "user", "content": prompt}
                ]
            )
            gpt_content = response.choices[0].message.content
            gpt_results = json.loads(gpt_content)  # 배열로 파싱
            if not isinstance(gpt_results, list):
                gpt_results = [gpt_results]
        except Exception as e:
            logger.error("GPT 호출 실패: %s", traceback.format_exc())
            print("GPT 호출 실패:", traceback.format_exc())
            if len(restaurants) > 1:
                random.shuffle(restaurants)
            gpt_results = []
            for best_match in random.sample(restaurants, min(3, len(restaurants))):
                gpt_results.append({
                    "store": best_match.get("name", "추천 없음"),
                    "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                    "category": ", ".join(best_match.get("categories", [])),
                    "keywords": best_match.get("keywords", [])
                })
        else:
            print("7. GPT 호출 성공")
            # backward compatibility: best_match는 첫 번째 결과로
            best_match = None
            for r in gpt_results:
                best_match = next((store for store in restaurants if store.get("name") == r.get("store")), None)
                if best_match:
                    break
            if not best_match and restaurants:
                best_match = restaurants[0]

        print("8. 응답 데이터 구성")
        response_data = {
            "results": gpt_results,  # 3개 배열 전체
            "result": gpt_results[0] if gpt_results else {},  # 첫 번째 결과(기존 호환)
            "restaurants": [
                {
                    "name": r.get("name", ""),
                    "review_avg": str(r.get("review_avg", "5점")),
                    "address": r.get("address", "주소 정보 없음"),
                    "id": str(r.get("id", "ID 없음")),
                    "categories": ", ".join(r.get("categories", [])),
                    "logo_url": r.get("logo_url", "")
                } for r in restaurants
            ]
        }
        if mode == "test":
            response_data.update({
                "text": text,
                "lat": lat,
                "lng": lng,
                "types": [t for t in [type1, type2, type3, type4, type5, type6] if t],
                "score": score
            })
        set_cache_with_db(cache_key, response_data, timeout=1800, data_type="recommendation_result")
        if mode == "test" and response_data.get("result"):
            try:
                user_id = 1
                recipe_id = 1
                score = 0.8
                save_recommendation_with_cache(
                    user_id=user_id,
                    recipe_id=recipe_id,
                    score=score,
                    recommendation_data=response_data
                )
            except Exception as e:
                logger.error(f"추천 결과 PostgreSQL 저장 실패: {e}")

        # 엔드포인트 내부에서
        db = SessionLocal()
        save_recommendation_history(
            db=db,
            user_id=None,
            request_type="recommend_result",
            input_data={"text": text, "lat": lat, "lng": lng, "mode": mode, "type1": type1, "type2": type2, "type3": type3, "type4": type4, "type5": type5, "type6": type6, "dummy": dummy},
            result_data=response_data
        )

        return response_data
    except Exception as e:
        logger.error(f"recommend_result 예외: {e}")
        # 예외 발생 시에도 result, restaurants 필드 포함
        return {
            "result": {},
            "restaurants": [],
            "error": str(e)
        }

def save_recommendation_history(
    db: Session,
    user_id: int,
    request_type: str,
    input_data: dict,
    result_data: dict
):
    history = RecommendationHistory(
        user_id=user_id,
        request_type=request_type,
        input_data=input_data,
        result_data=result_data
    )
    db.add(history)
    db.commit()