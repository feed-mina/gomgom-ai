from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
import httpx
import json
import openai
from app.core.config import settings
from app.utils.keyword_extractor import extract_keywords_from_store_name
from app.utils.prompt_creator import create_yogiyo_prompt_with_options, make_store_info_line, classify_user_input_via_gpt
from app.utils.store_matcher import match_gpt_result_with_yogiyo
from app.core.cache import cache
from app.schemas.test_result import TestResult
import random
from app.db.session import SessionLocal
from app.db.crud import save_recommendation_history
import logging

router = APIRouter()

@router.get("/test_result/", response_model=TestResult)
async def get_test_result(
    text: Optional[str] = Query(None),
    lat: float = Query(...),
    lng: float = Query(...),
    types: str = Query(...),
    dummy: Optional[str] = Query(None)
):
    if text == 'none':
        text = None
    cache_key = f"test_result_{text}_{lat}_{lng}_{types}_{dummy}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        # 반드시 식당 정보만 반환
        return {
            "results": cached_data.get("results", []),
            "result": cached_data.get("result", {}),
            "address": cached_data.get("address", "")
        }

    try:
        data = await fetch_yogiyo_data(lat, lng)
        restaurants = data if isinstance(data, list) else data.get("restaurants", [])
        if not restaurants:
            return {
                "results": [],
                "result": {},
                "address": ""
            }

        if restaurants:
            logger = logging.getLogger("uvicorn.error")
            # # logger.info(f"[YOGIYO API] 첫 번째 레스토랑 데이터: {restaurants[0]}")
            # logger.info(f"[YOGIYO API] logo_url 필드: {restaurants[0].get('logo_url', 'NOT_FOUND')}")
            # logger.info(f"[YOGIYO API] review_avg 필드: {restaurants[0].get('review_avg', 'NOT_FOUND')}")

        store_info_list = [make_store_info_line(r) for r in restaurants]
        if len(restaurants) > 1:
            random.shuffle(store_info_list)
        store_info_list = store_info_list[:10]

        input_type = await classify_user_input_via_gpt(text or "")
        score = {}
        for t in types.split(','):
            if t:
                score[t] = score.get(t, 0) + 1
        prompt = create_yogiyo_prompt_with_options(text, store_info_list, score, input_type) + f"\n#dummy={dummy or random.random()}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            gpt_content = response.choices[0].message.content
            gpt_results = json.loads(gpt_content)
            if not isinstance(gpt_results, list):
                gpt_results = [gpt_results]
        except Exception as e:
            if len(restaurants) > 1:
                random.shuffle(restaurants)
            gpt_results = []
            for best_match in random.sample(restaurants, min(3, len(restaurants))):
                gpt_results.append({
                    "store": best_match.get("name", "추천 없음"),
                    "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                    "category": ", ".join(best_match.get("categories", [])),
                    "keywords": best_match.get("keywords", []),
                    "logo_url": best_match.get("logo_url", ""),
                    "address": best_match.get("address", "")
                })
        else:
            best_match = None
            for r in gpt_results:
                best_match = next((store for store in restaurants if store.get("name") == r.get("store")), None)
                if best_match:
                    break
            if not best_match and restaurants:
                best_match = restaurants[0]

        address = await get_address_from_coords(lat, lng)
        def enrich_gpt_result_with_yogiyo(gpt_result, restaurants):
            match = next((r for r in restaurants if r.get("name") == gpt_result.get("store")), None)
            if match:
                gpt_result["logo_url"] = match.get("logo_url", "")
                gpt_result["review_avg"] = match.get("review_avg", 0.0)
                gpt_result["address"] = match.get("address", "")
                gpt_result["categories"] = ", ".join(match.get("categories", [])) if isinstance(match.get("categories"), list) else match.get("categories", "")
            else:
                gpt_result.setdefault("logo_url", "")
                gpt_result.setdefault("review_avg", 0.0)
                gpt_result.setdefault("address", "")
                gpt_result.setdefault("categories", "")
            return gpt_result
        enriched_results = [enrich_gpt_result_with_yogiyo(r, restaurants) for r in gpt_results]
        def to_result(store):
            return {
                "store": store.get("store", ""),
                "description": store.get("description", ""),
                "category": store.get("category", ""),
                "keywords": store.get("keywords", []),
                "logo_url": store.get("logo_url", ""),
                "review_avg": store.get("review_avg", 0.0),
                "address": store.get("address", ""),
                "categories": store.get("categories", "")
            }
        result = {
            "results": [to_result(s) for s in enriched_results] if enriched_results is not None else [],
            "result": to_result(enriched_results[0]) if enriched_results and len(enriched_results) > 0 else {},
            "address": address
        }
        await cache.set(cache_key, result, timeout=1800)
        db = SessionLocal()
        save_recommendation_history(
            db=db,
            user_id=None,
            request_type="test_result",
            input_data={"text": text, "lat": lat, "lng": lng, "types": types, "dummy": dummy},
            result_data=result
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_yogiyo_data(lat: float, lng: float):
    """요기요 API에서 가게 데이터 가져오기"""
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
        "serving_type": "delivery",
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

async def get_address_from_coords(lat: float, lng: float) -> str:
    """카카오 API를 사용하여 좌표로부터 주소 가져오기"""
    cache_key = f"address_{lat}_{lng}"
    cached_address = await cache.get(cache_key)
    if cached_address:
        return cached_address

    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    headers = {
        "Authorization": f"KakaoAK {settings.KAKAO_REST_API}"
    }
    params = {
        "x": lng,
        "y": lat
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            result = response.json()
            if result['documents']:
                address = result['documents'][0]['address']['address_name']
                await cache.set(cache_key, address, timeout=3600)
                return address
    return "주소 정보를 가져올 수 없습니다." 