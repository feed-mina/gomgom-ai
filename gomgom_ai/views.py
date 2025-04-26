import asyncio
import httpx
import json
import os
import random
import re
import requests
from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from konlpy.tag import Okt
from openai import OpenAI
from pathlib import Path
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET
from asgiref.sync import sync_to_async
from django.conf import settings
import jwt
from .classify_user_input import classify_user_input
from .create_yogiyo_prompt_with_options import create_yogiyo_prompt_with_options
from .match_gpt_result_with_yogiyo import match_gpt_result_with_yogiyo

okt = Okt()
print(okt.nouns("짬뽕지존-봉천점"))

cache.set('hello', 'world', timeout=10)
print(cache.get('hello'))  # → 'world' 나오면 OK

# JWT 비밀 키는 justsaying(Spring) 서버에서 사용하는 거랑 똑같이 맞춰야 해!
SECRET_KEY = '햄의-justsaying-서버-시크릿키'

@csrf_exempt  # (테스트용) CSRF검증 무시
def check_login(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return JsonResponse({'error': 'Authorization header missing'}, status=401)

    try:
        token = auth_header.split(' ')[1]  # "Bearer xxxxx" 형식
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = decoded.get('userId')  # 토큰 안에 들어있던 userId 꺼내기

        return JsonResponse({'message': f'로그인 성공! 어서와 햄({user_id})!'})

    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=401)

def login_page(request):
    return render(request, 'gomgom_ai/login.html')

# name문자열을 형태소 분석해서 (단어,품사)로 나눔, pos == 'Noun' 명사인 단어만 고름
# len(w) > 1 너무 짧은 단어 (예 : '의','가')는 빼고 두글자 이상만
def extract_keywords_from_store_name(name):
    # '짬뽕지존-봉천점' → ['짬뽕', '지존', '봉천']
    keywords = [w for w, pos in okt.pos(name) if pos == 'Noun' and len(w) > 1]
    return keywords


def is_related(text, result):
    if not text:
        return True  # ← 이렇게 추가해줘!
    text = text.lower()
    return (
            text in result.get("store", "").lower() or
            text in result.get("category", "").lower() or
            any(text in kw.lower() for kw in result.get("keywords", []))
    )


# 요기요 API 데이터 요청

def get_yogiyo_restaurants(lat, lng):
    url = f"https://www.yogiyo.co.kr/api/v1/restaurants"
    params = {
        "lat": lat,
        "lng": lng,
        "page": 0,
        "serving_type": "delivery",
    }

    headers = {
        "User-Agent": "Mozilla/5.0",  # 중요! 요기요는 UA 없으면 차단됨
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        # print("요기요 응답 상태코드:", response.status_code)
        #print("요기요 응답 내용:", response.text[:500])
        # 너무 길면 앞부분만 출력
        # print("요기요 API data:", data)
        return data
    except Exception as e:
        # print("요기요 API 오류:", e)
        return []


# 음식 리스트 로드
def load_food_list():
    path = Path(__file__).resolve().parent / 'food_list.json'
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def generate_emotional_description(food_name, tags):
    # 태그 기반 기본 감성 문장
    tag_descriptions = {
        "spicy": "매콤한 맛이 기분 전환에 딱이에요!",
        "mild": "부드럽고 편안한 한 끼를 원한다면 좋아요!",
        "safe": "누구나 좋아하는 익숙한 맛으로 오늘을 위로해줘요!",
        "adventurous": "새로운 맛이 오늘 하루에 활력을 줄 거예요!",
        "korean": "한국적인 정갈한 맛이 마음을 따뜻하게 해줘요.",
        "foreign": "이국적인 향신료의 매력이 느껴지는 특별한 메뉴예요!",
        "chinese": "중화풍의 진한 풍미가 인상적이에요!",
        "japanese": "섬세하고 담백한 맛으로 입맛을 사로잡아요!",
        "western": "크리미하고 고소한 유럽식 요리를 느껴보세요.",
        "thai": "달콤하고 매콤한 열대의 맛이 어우러져요.",
        "mexican": "톡 쏘는 매콤함과 풍부한 향신료의 조화가 일품이에요!",
        "snack": "간단하면서도 든든한 간식으로 제격이에요!",
        "fusion": "여러 나라 맛이 어우러진 창의적인 요리예요!"
    }

    matched = [tag_descriptions.get(tag) for tag in tags if tag in tag_descriptions]
    if matched:
        return f"{food_name}은(는) " + matched[0]
    else:
        return f"{food_name}은(는) 오늘을 특별하게 만들어줄 음식이에요!"


def test_view(request):
    return render(request, 'gomgom_ai/test.html')


def home_view(request):
    return render(request, 'gomgom_ai/home.html')


def main(request):
    return render(request, 'gomgom_ai/main.html')


def index(request):
    return render(request, 'index.html')  # 또는 HttpResponse("Hello 햄!")


# 입맛 테스트
def start_view(request):
    text = request.GET.get("text")
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    return render(request, 'gomgom_ai/start.html', {
        "text": text,
        "lat": lat,
        "lng": lng
    })



def my_cached_view(request):
    result = cache.get("my_custom_key")
    if not result:
        # 데이터 처리 또는 API 호출
        result = "비싼 작업 결과"
        cache.set("my_custom_key", result, timeout=60 * 5)  # 5분 캐시

    return JsonResponse({"result": result})


async def async_cached_view(request):
    data = cache.get("async_test_key")
    if not data:
        # 느린 작업
        await asyncio.sleep(1)
        data = "async 처리 완료 결과"
        cache.set("async_test_key", data, timeout=60)

    return JsonResponse({"data": data})


async def async_test_view(request):
    await asyncio.sleep(1)
    return JsonResponse({'message': 'Async works!'})


def cache_test_view(request):
    cache.set('hello', 'world', timeout=60)
    value = cache.get('hello')
    return JsonResponse({'cached_value': value})


def is_similar_store_name(store1, store2):
    def clean(s):
        return re.sub(r"[^가-힣a-zA-Z0-9]", "", s).replace(" ", "").lower()

    return clean(store1) in clean(store2) or clean(store2) in clean(store1)


def is_related_by_keywords(gpt_keywords, store_name):
    store_keywords = extract_keywords_from_store_name(store_name)
    return any(k in store_keywords for k in gpt_keywords)


def keyword_overlap(gpt_keywords, store_name):
    keywords_in_name = extract_keywords_from_store_name(store_name)
    return any(k in keywords_in_name for k in gpt_keywords)


def get_address_from_coords(lat, lng):
    url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
    headers = {
        "Authorization": f"KakaoAK {os.getenv('KAKAO_REST_API')}"  # .env에서 읽어온 키
    }
    params = {
        "x": lng,
        "y": lat
    }
    # print(f"주소 변환 요청 보내는 중... x={lng}, y={lat}")

    response = requests.get(url, headers=headers, params=params)
    # print("카카오 API 응답코드:", response.status_code)
    # print("카카오 API 응답내용:", response.text)
    if response.status_code == 200:
        result = response.json()
        if result['documents']:
            address = result['documents'][0]['address']['address_name']
            # print("주소 가져옴:", address)
            return address
        else:
            # print("⚠️ 카카오 API 요청 실패")
            return "주소 정보를 가져올 수 없습니다."

async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.yogiyo.co.kr/api/v1/restaurants")
        return response.json()


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


async def fetch_yogiyo_data(lat, lng):
    url = "http://www.yogiyo.co.kr/api/v1/restaurants"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    params = {
        "lat": lat,
        "lng": lng,
        "page": 0,
        "serving_type": "delivery",
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            # print("🛰 상태코드:", response.status_code)
            # print("📦 응답 내용 일부:", response.text[:300])  # 응답 내용 앞부분만 확인
            data = response.json()  # 문제 생길 수 있음
            return data
        except Exception as e:
            # print("❗요기요 API 오류:", e)
            return {"restaurants": []}

@require_GET
@csrf_exempt
async def restaurant_list_view(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    cache_key = f"restaurants:{lat}:{lng}"
    cached_data = cache.get(cache_key)
    # 주소 받아오기!
    # address = get_address_from_coords(lat, lng) if lat and lng else None

    if cached_data:
        # print("✅ Redis 캐시에서 가져옴")
        return render(request, "gomgom_ai/restaurant_list.html", {
            "restaurants": cached_data,
            "lat": lat,
            "lng": lng
        })

    # print("🌀 캐시에 없어서 새로 요청 중...")
    data = await fetch_yogiyo_data(lat, lng)
    restaurants = data.get("restaurants", []) if isinstance(data, dict) else data

    cache.set(cache_key, restaurants, timeout=60 * 5)  # 5분 캐시

    if not lat or not lng:
        return render(request, "gomgom_ai/restaurant_list.html", {
            "restaurants": [],
            "lat": None,
            "lng": None,
        })

    return render(request, "gomgom_ai/restaurant_list.html", {
        "restaurants": restaurants,
        "lat": lat,
        "lng": lng,
    })


@csrf_exempt
def ask_gpt_to_choose(score,food_list, food_data_dict=None):
    # print("score:", score)
    # print("food_list:", food_list)
    # print("food_data_dict:", food_data_dict)
    content = ""  # content 미리 정의
    prompt = f"""
    다음 사용자 기분 태그 목록에 맞는 배달 음식점 하나만 골라줘:
    {', '.join(score.keys())}
    
    - 이 기분은 사용자가 먹고 싶어할 맛의 방향성을 의미해
    - 아래는 배달 가능한 음식점 리스트와 주요 키워드야:
    {chr(10).join(store_keywords_list[:10])}
    
    조건:
    - 추천 결과는 JSON으로:
    {{
      "store": 음식점 이름,
      "description": 추천 이유 (감성 한 줄),
      "category": 대표 카테고리,
      "keywords": [키워드1, 키워드2, ...]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        # content = response['choices'][0]['message']['content']
        return json.loads(content)

    except json.JSONDecodeError:
       print("⚠️ GPT 응답 JSON 파싱 실패! 응답 내용:", content)
        # print(content)

    except Exception as e:
        # print("GPT 호출 실패:", e)

        fallback_food = random.choice(food_list)
        fallback_tags = food_data_dict.get(fallback_food, [])
        fallback_desc = generate_emotional_description(fallback_food, fallback_tags)

        # print("fallback_food:", fallback_food)
        # print("fallback_tags:", fallback_tags)
        # print("fallback_desc:", fallback_desc)
        try:
            match = re.search(
                r'"food"\s*:\s*"([^"]+)"\s*,\s*"description"\s*:\s*"([^"]+)"',
                content, re.DOTALL
            )
            if match:
                return {
                    "food": match.group(1),
                    "description": match.group(2)
                }
        except:
            pass
        return {"food": fallback_food, "description": fallback_desc}


@cache_page(60 * 5)  # 5분 동안 캐싱
@csrf_exempt
def test_result_view(request):
    text = request.GET.get("text")
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")

    if not lat or not lng:
        lat = "37.484934"
        lng = "126.981321"

    types = [request.GET.get(f"type{i + 1}") for i in range(6)]
    # print("types:", types)
    # print("text:", text)

    # 기분 태그 개수 세기
    score = {}
    for t in types:
        if t:
            score[t] = score.get(t, 0) + 1

    # === 병렬 실행용 함수들 정의 ===
    def fetch_yogiyo():
        return get_yogiyo_restaurants(lat, lng)

    def ask_gpt(prompt):
        return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

    with ThreadPoolExecutor() as executor:
        # 요기요 먼저 실행
        future_yogiyo = executor.submit(fetch_yogiyo)
        restaurants_data = future_yogiyo.result()

        raw_restaurants = restaurants_data.get("restaurants", []) if isinstance(restaurants_data,
                                                                                dict) else restaurants_data

        # 가게 키워드 리스트 준비
        store_keywords_list = [
            f"{r.get('name')}: {', '.join(extract_keywords_from_store_name(r.get('name', '')))}"
            for r in raw_restaurants
        ]
        random.shuffle(store_keywords_list)
        store_keywords_list = store_keywords_list[:10]  # GPT 입력은 짧게

        # print("score:", score)
        # 프롬프트 생성
        prompt = create_yogiyo_prompt_with_options(text, store_keywords_list, score=score)

        # GPT 실행
        future_gpt = executor.submit(ask_gpt, prompt)

        try:
            gpt_response = future_gpt.result()
            result = json.loads(gpt_response.choices[0].message.content)

            if "keywords" not in result:
                result["keywords"] = extract_keywords_from_store_name(result.get("store", ""))

            is_valid_result = is_related(text, result)

            best_match = match_gpt_result_with_yogiyo(result, raw_restaurants)
            matched_restaurants = [{
                "name": best_match.get("name"),
                "review_avg": best_match.get("review_avg", "5점"),
                "address": "카테고리: " + ", ".join(best_match.get("categories", [])),
                "logo": best_match.get("logo_url", ""),
            }] if best_match else []

            # print("gpt_response:", gpt_response)

            # print("GPT 호출 성공 result:", result)
            # print("GPT 호출 성공 best_match:", best_match)
            # print("GPT 호출 성공 matched_restaurants:", matched_restaurants)
        except Exception as e:
            # print("GPT 호출 실패:", e)
            fallback = random.choice(raw_restaurants) if raw_restaurants else {}
            result = {
                "store": fallback.get("name", "추천 없음"),
                "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                "category": ", ".join(fallback.get("categories", [])),
                "keywords": extract_keywords_from_store_name(fallback.get("name", ""))
            }
            matched_restaurants = [{
                "name": fallback.get("name", "추천 없음"),
                "review_avg": fallback.get("review_avg", "5점"),
                "address": fallback.get("address", "주소 없음"),
                "id": fallback.get("id", "없음"),
                "categories": ", ".join(fallback.get("categories", [])),
                "logo": fallback.get("logo_url", "")
            }]
            # print("GPT 호출 성공 fallback:", result)
            # print("GPT 호출 성공 fallback:", matched_restaurants)
    return render(request, 'gomgom_ai/test_result.html', {
        "result": result,
        "restaurants": mark_safe(json.dumps(matched_restaurants, ensure_ascii=False)),
        "text": text,
        "lat": lat,
        "lng": lng,
        "types": types,
        "score": score,
        "DEBUG": settings.DEBUG,  #  이거 추가!
    })


@cache_page(60 * 5)  # 5분 동안 캐싱
@csrf_exempt
def recommend_result(request):
    text = request.GET.get("text")
    lat = request.GET.get("lat", "37.484934")
    lng = request.GET.get("lng", "126.981321")
    user_input_category = classify_user_input(text)

    if not lat or not lng:
        lat = "37.484934"
        lng = "126.981321"

    # === 병렬로 작업하기 위한 함수들 정의 ===
    def fetch_yogiyo():
        return get_yogiyo_restaurants(lat, lng)

    def ask_gpt(prompt):
        return client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

    with ThreadPoolExecutor() as executor:
        future_yogiyo = executor.submit(fetch_yogiyo)
        restaurants_data = future_yogiyo.result()

        raw_restaurants = restaurants_data.get("restaurants", []) if isinstance(restaurants_data,
                                                                                dict) else restaurants_data

        store_keywords_list = [
            f"{r.get('name')}: {', '.join(extract_keywords_from_store_name(r.get('name', '')))}"
            for r in raw_restaurants
        ]
        random.shuffle(store_keywords_list)
        store_keywords_list = store_keywords_list[:10]  #  너무 많으면 GPT 느려져서 자르기
        # print("store_keywords_list:", store_keywords_list)

        prompt = create_yogiyo_prompt_with_options(text, store_keywords_list, score=None,
                                                   input_type=user_input_category)

        # GPT 호출 병렬 실행
        future_gpt = executor.submit(ask_gpt, prompt)
        try:
            gpt_response = future_gpt.result()
            result = json.loads(gpt_response.choices[0].message.content)

            if "keywords" not in result:
                result["keywords"] = extract_keywords_from_store_name(result.get("store", ""))

            is_valid_result = is_related(text, result)

            best_match = match_gpt_result_with_yogiyo(result, raw_restaurants)
            result["logo_url"] = best_match.get("logo_url", "")

            matched_restaurants = []
            # print("gpt_response:", gpt_response)

            # print("GPT 호출 성공 result:", result)
            # print("GPT 호출 성공 best_match:", best_match)
            # print("GPT 호출 성공 matched_restaurants:", matched_restaurants)
            if best_match:
                matched_restaurants = [{
                    "name": best_match.get("name"),
                    "review_avg": best_match.get("review_avg", "5점"),
                    "address": best_match.get("address", "주소 정보 없음"),
                    "id": best_match.get("id", "ID 없음"),
                    "categories": ", ".join(best_match.get("categories", [])),
                    "logo": best_match.get("logo_url", ""),
                    "logo_url" : best_match.get("logo_url", "")
                }]
        except Exception as e:
            # print("GPT 호출 실패:", e)
            fallback = random.choice(raw_restaurants) if raw_restaurants else {}
            result = {
                "store": fallback.get("name", "추천 없음"),
                "description": f"'{text or '무작위'}'와 어울리는 인기 메뉴를 추천해요!",
                "category": ", ".join(fallback.get("categories", [])),
                "keywords": extract_keywords_from_store_name(fallback.get("name", ""))
            }
            matched_restaurants = [{
                "name": fallback.get("name", "추천 없음"),
                "review_avg": fallback.get("review_avg", "5점"),
                "address": fallback.get("address", "주소 없음"),
                "id": fallback.get("id", "없음"),
                "categories": ", ".join(fallback.get("categories", [])),
                "logo": fallback.get("logo_url", "")
            }]

    return render(request, 'gomgom_ai/recommend_result.html', {
        "result": result,
        "restaurants": matched_restaurants,
        "keyword": [result.get("store")],
        "DEBUG": settings.DEBUG,
    })
