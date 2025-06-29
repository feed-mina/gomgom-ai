from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
import httpx
import json
import openai
from app.core.config import settings
from app.utils.keyword_extractor import extract_keywords_from_store_name
from app.utils.prompt_creator import create_yogiyo_prompt_with_testoptions
from app.utils.store_matcher import match_gpt_result_with_yogiyo
from app.core.cache import cache
from app.schemas.test_result import TestResultResponse, TestResult
import random

router = APIRouter()

@router.get("/test_result/", response_model=TestResult)
async def get_test_result(
    text: Optional[str] = Query(None),
    lat: float = Query(...),
    lng: float = Query(...),
    types: str = Query(...),
    dummy: Optional[str] = Query(None)
):
    # text가 'none'이면 입력 없는 것으로 간주
    if text == 'none':
        text = None
    # 1. 캐시 확인 (dummy 포함)
    cache_key = f"test_result_{text}_{lat}_{lng}_{types}_{dummy}"
    cached_data = await cache.get(cache_key)
    if cached_data:
        return cached_data

    try:
        # 2. 요기요 API에서 가게 리스트 받아오기
        data = await fetch_yogiyo_data(lat, lng)
        restaurants = data if isinstance(data, list) else data.get("restaurants", [])
        if not restaurants:
            raise HTTPException(status_code=404, detail="주변에 음식점이 없습니다.")

        # 3. 가게명+키워드 리스트 만들기
        store_keywords_list = [
            f"{r.get('name')}: {', '.join(extract_keywords_from_store_name(r.get('name', '')))}"
            for r in restaurants
        ]
        if len(restaurants) > 1:
            random.shuffle(restaurants)

        # 4. 테스트 결과 점수 계산
        score = {}
        for t in types.split(','):
            if t:
                score[t] = score.get(t, 0) + 1

        # 5. GPT 프롬프트 생성 (테스트 결과 반영, dummy 값 추가)
        prompt = create_yogiyo_prompt_with_testoptions(text, store_keywords_list, score) + f"\n#dummy={dummy or random.random()}"

        # 6. GPT 호출
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            gpt_content = response.choices[0].message.content
            gpt_result = json.loads(gpt_content)
        except Exception as e:
            # GPT 실패 시 랜덤 추천 fallback
            if len(restaurants) > 1:
                random.shuffle(restaurants)
            best_match = random.choice(restaurants)
            gpt_result = {
                "store": best_match.get("name", "추천 없음"),
                "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                "category": ", ".join(best_match.get("categories", [])),
                "keywords": extract_keywords_from_store_name(best_match.get("name", ""))
            }
        else:
            # 7. 요기요 가게 리스트에서 best match 찾기
            best_match = match_gpt_result_with_yogiyo(gpt_result, restaurants)
            if not best_match:
                # Fallback: 랜덤 선택
                if len(restaurants) > 1:
                    random.shuffle(restaurants)
                best_match = random.choice(restaurants)
                gpt_result = {
                    "store": best_match.get("name", "추천 없음"),
                    "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                    "category": ", ".join(best_match.get("categories", [])),
                    "keywords": extract_keywords_from_store_name(best_match.get("name", ""))
                }

        # 8. 주소 가져오기
        address = await get_address_from_coords(lat, lng)

        # 9. 응답 데이터 구성
        result = {
            "result": {
                "store": best_match.get("name", ""),
                "description": gpt_result.get("description", ""),
                "category": ", ".join(best_match.get("categories", [])),
                "keywords": gpt_result.get("keywords", []),
                "logo_url": best_match.get("logo_url", "")
            },
            "address": address
        }

        # 10. 결과 캐싱 (30분)
        await cache.set(cache_key, result, timeout=1800)

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