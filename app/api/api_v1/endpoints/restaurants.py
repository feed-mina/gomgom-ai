from typing import Optional, List, Dict
from fastapi import APIRouter, HTTPException, Query
import httpx
import os
from app.schemas.restaurant import Restaurant, RestaurantListResponse, DeliveryFeeDisplay
from app.core.cache import get_cache, set_cache, set_cache_with_db
import logging
import psycopg2
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger("restaurant_api")

KAKAO_API_URL = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
YOGIYO_API_URL = "https://www.yogiyo.co.kr/api/v1/restaurants/"
CACHE_ENABLED = settings.CACHE_ENABLED

async def get_address_from_coords(lat: float, lng: float) -> str:
    print(f"KAKAO_REST_API loaded: {settings.KAKAO_REST_API}")

    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API}"}

    params = {"x": lng, "y": lat}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(KAKAO_API_URL, headers=headers, params=params)
            logger.info(f"[주소 변환] 요청 lat={lat}, lng={lng}, status={response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if result['documents']:
                    return result['documents'][0]['address']['address_name']
            return "주소 정보를 가져올 수 없습니다."
        except Exception as e:
            logger.error(f"[주소 변환] 오류: {e}")
            return "주소 정보를 가져올 수 없습니다."

async def fetch_yogiyo_data(lat: float, lng: float):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    params = {"lat": lat, "lng": lng, "page": 0, "serving_type": "delivery"}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(YOGIYO_API_URL, params=params, headers=headers)
            logger.info(f"[요기요] 요청 lat={lat}, lng={lng}, status={response.status_code}")
            logger.info(f"[요기요] 응답 일부: {response.text[:100]}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"[요기요] 오류: {e}")
            return []

def parse_restaurant(r: dict) -> Restaurant:
    return Restaurant(
        id=int(r.get("id", 0)),
        name=r.get("name", ""),
        logo_url=r.get("logo_url", ""),
        categories=r.get("categories", []),
        review_avg=float(r.get("review_avg", 0.0)),
        review_count=r.get("review_count", 0),
        delivery_fee_to_display=DeliveryFeeDisplay(
            basic=(r.get("delivery_fee_to_display", {}) or {}).get("basic", "정보 없음")
        ),
        address=r.get("address") or "",
        keywords=[]
    )

@router.get("/restaurants")
async def get_restaurants(
        lat: float = Query(...),
        lng: float = Query(...),
        radius: int = Query(1000)
):
    try:
        lat, lng = float(lat), float(lng)
    except (TypeError, ValueError):
        logger.error(f"Invalid latitude or longitude: lat={lat}, lng={lng}")
        raise HTTPException(status_code=400, detail="Invalid latitude or longitude")

    cache_key = f"restaurants_{lat}_{lng}_{radius}"
    cached_data = get_cache(cache_key)
    if CACHE_ENABLED and cached_data is not None and isinstance(cached_data, dict):
        logger.info(f"[CACHE HIT] {cache_key}")
        return RestaurantListResponse(**cached_data)
    else:
        logger.info(f"[CACHE MISS] {cache_key}")

    try:
        timeout = httpx.Timeout(5.0, read=5.0)
        async with httpx.AsyncClient(follow_redirects=True,timeout=timeout) as client:
            response = await client.get(
                YOGIYO_API_URL,
                params={"lat": lat, "lng": lng, "radius": radius},
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            )

        logger.info(f"[YOGIYO API] status={response.status_code}")
        logger.info(f"[YOGIYO API] 응답 일부: {response.text[:200]}")
        logger.debug(f"요청 URL: {response.request.url}")
        logger.debug(f"응답 상태코드: {response.status_code}")
        logger.debug(f"응답 헤더: {response.headers}")
        response.raise_for_status()

        MAX_RESULTS = 100

        data = response.json()
        restaurants = data if isinstance(data, list) else data.get("restaurants", [])
        restaurants = restaurants[:MAX_RESULTS]
        address = await get_address_from_coords(lat, lng)

        if not restaurants:
            logger.warning("[YOGIYO API] 응답에 restaurants 없음 또는 빈 리스트")
            return RestaurantListResponse(restaurants=[], address="요기요 응답 없음")

        parsed = []
        for r in restaurants:
            try:
                parsed.append(parse_restaurant(r))
            except Exception as e:
                logger.warning(f"[PARSE FAIL] 가게 파싱 실패: {e}, 원본: {r}")

        result = RestaurantListResponse(restaurants=parsed[:100], address=address)

        if CACHE_ENABLED:
            set_cache_with_db(cache_key, result.model_dump(), timeout=900, data_type="restaurant_data")

        return result

    except httpx.ReadTimeout:
        logger.error("요기요 응답 시간 초과")
        return RestaurantListResponse(restaurants=[], address="요기요 응답 시간 초과")

    except psycopg2.OperationalError as e:
        logger.error(f"DB 연결 실패: {e}")
        raise HTTPException(status_code=500, detail="DB 연결 실패")

    except Exception as e:
        logger.error(f"Unknown error: {e}", exc_info=True)
        return RestaurantListResponse(restaurants=[], address="서버 내부 오류 발생")

@router.get("/recommend_result", tags=["recommend_result"])
async def recommend_result(
        text: Optional[str] = Query(None),
        lat: float = Query(...),
        lng: float = Query(...)
):
    data = await fetch_yogiyo_data(lat, lng)
    restaurants = data if isinstance(data, list) else data.get("restaurants", [])

    if not restaurants:
        raise HTTPException(status_code=404, detail="주변에 음식점이 없습니다.")

    best = restaurants[0]

    return {
        "store": best.get("name", ""),
        "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
        "category": ", ".join(best.get("categories", [])),
        "keywords": best.get("categories", []),
        "latitude": best.get("lat", lat),
        "longitude": best.get("lng", lng),
        "review_avg": best.get("review_avg", 0.0),
        "review_count": best.get("review_count", 0),
        "logo_url": best.get("logo_url", ""),
        "address": best.get("address", "")
    }