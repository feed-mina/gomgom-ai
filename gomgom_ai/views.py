# gomgom_ai/views.py
from django.shortcuts import render # HTML 화면을 보여줄때 사용하는 함수
from openai import OpenAI #chatGPT 도구
from django.http import JsonResponse # json형식으로 데이터를 응답할수있게한다.
from django.views.decorators.csrf import csrf_exempt #  Django 기본 보안 기능 중 하나인 CSRP 를 임시로 꺼주는 장치
import json # json데이터를 {'이름':'값'} 형태로 주고 받을때 사용
import requests # 다른 웹사이트 api로부터 데이터를 가져올때 사용 (-요기요)
from django.conf import settings # .env나 Django설정에서 저장된 값을 꺼낼때 사용
import os
from .data import all_dishes
from pathlib import Path # 파일경로를 쉽게 찾게 해줌
import random # 무작위 음식 고를때 사용
import re #정규표현식(문자에서 특정 패턴 찾을때 사용)
from .match_gpt_result_with_yogiyo import match_gpt_result_with_yogiyo # gpt가 추천한 가게와 요기요 api 중 가장 비슷한 리스트
from .create_yogiyo_prompt_with_options import create_yogiyo_prompt_with_options #gpt에게 요기요 api 가게리스트를 보여주고 직접 선택하게 하기
from .classify_user_input import classify_user_input # 사용자가 적는 텍스트별 분기

from konlpy.tag import Okt # 한국어 문장 분석기를 준비하는 코드
okt = Okt()
# print(okt.nouns("짬뽕지존-봉천점"))


def is_related(text, result):
    if not text:
        return True  # ← 이렇게 추가해줘!
    text = text.lower()
    return (
            text in result.get("store", "").lower() or
            text in result.get("category", "").lower() or
            any(text in kw.lower() for kw in result.get("keywords", []))
    )


def is_similar_store_name(store1, store2):
    def clean(s):
        return re.sub(r"[^가-힣a-zA-Z0-9]", "", s).replace(" ", "").lower()
    return clean(store1) in clean(store2) or clean(store2) in clean(store1)


# name문자열을 형태소 분석해서 (단어,품사)로 나눔, pos == 'Noun' 명사인 단어만 고름
# len(w) > 1 너무 짧은 단어 (예 : '의','가')는 빼고 두글자 이상만
def extract_keywords_from_store_name(name):
    # '짬뽕지존-봉천점' → ['짬뽕', '지존', '봉천']
    keywords = [w for w, pos in okt.pos(name) if pos == 'Noun' and len(w) > 1]
    return keywords

def is_related_by_keywords(gpt_keywords, store_name):
    store_keywords = extract_keywords_from_store_name(store_name)
    return any(k in store_keywords for k in gpt_keywords)


def keyword_overlap(gpt_keywords, store_name):
    keywords_in_name = extract_keywords_from_store_name(store_name)
    return any(k in keywords_in_name for k in gpt_keywords)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY)

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
        # print("요기요 API data:", data)
        return data
    except Exception as e:
        print("요기요 API 오류:", e)
        return []

def restaurant_list_view(request):
    lat = request.GET.get("lat", "37.484934")  # 기본값 사당역 근처
    lng = request.GET.get("lng", "126.981321")

    data = get_yogiyo_restaurants(lat, lng)
    restaurants = data if isinstance(data, list) else data.get("restaurants", [])

    return render(request, "gomgom_ai/restaurant_list.html", {
        "restaurants": restaurants,
        "lat": lat,
        "lng": lng,
    })

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


@csrf_exempt
def ask_gpt_to_choose(food_list, food_data_dict=None):
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
        print("GPT 호출 실패:", e)

        fallback_food = random.choice(food_list)
        fallback_tags = food_data_dict.get(fallback_food, [])
        fallback_desc = generate_emotional_description(fallback_food, fallback_tags)

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


def test_result_view(request):
    text = request.GET.get("text")
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    types = [request.GET.get(f"type{i + 1}") for i in range(6)]
    score = {}

    for t in types:
        if t:
            score[t] = score.get(t, 0) + 1

    restaurants_data = get_yogiyo_restaurants(lat, lng)
    raw_restaurants = restaurants_data.get("restaurants", []) if isinstance(restaurants_data, dict) else restaurants_data

    store_keywords_list = [
        f"{r.get('name')}: {', '.join(extract_keywords_from_store_name(r.get('name', '')))}"
        for r in raw_restaurants
    ]

    random.shuffle(store_keywords_list)

    # 프롬프트 생성 (text, score 둘 다 고려)
    prompt = create_yogiyo_prompt_with_options(text, store_keywords_list, score=score)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = json.loads(response.choices[0].message.content)

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

    except Exception as e:
        print("GPT 호출 실패:", e)
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

    return render(request, 'gomgom_ai/test_result.html', {
        "result": result,
        "restaurants": matched_restaurants,
        "keyword": [result.get("store")]
    })


def home_view(request):
    return render(request, 'gomgom_ai/home.html')
def main(request):
    return render(request, 'gomgom_ai/main.html')

# 입맛 테스트
def start_view(request):
    print("넘어온 text:", request.GET.get('text'))
    print("넘어온 lat:", request.GET.get('lat'))
    print("넘어온 lng:", request.GET.get('lng'))

    return render(request, 'gomgom_ai/start.html')

def test_view(request):
    return render(request, 'gomgom_ai/test.html')
@csrf_exempt
def recommend_result(request):
    text = request.GET.get('text')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    print("입력값:", text)
    print("위치:", lat, lng)
    restaurants_data = get_yogiyo_restaurants(lat, lng)
    raw_restaurants = restaurants_data.get("restaurants", []) if isinstance(restaurants_data, dict) else restaurants_data


    # 1. 요기요 가게 리스트 먼저 불러오기
    # 키워드 포함된 문자열 리스트 만들기 (GPT에게 줄용)
    store_keywords_list = [
        f"{r.get('name')}: {', '.join(extract_keywords_from_store_name(r.get('name', '')))}"
        for r in raw_restaurants
    ]
    random.shuffle(store_keywords_list)
    # 사용자 입력이 음식인지, 기분인지, 상황인지, 기능인지 구분
    user_input_category = classify_user_input(text)

    # 사용자 입력 유형에 따라 프롬프트 생성
    prompt = create_yogiyo_prompt_with_options(text, store_keywords_list, score=None, input_type=user_input_category)



    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = json.loads(response.choices[0].message.content)


        is_valid_result = is_related(text, result)
        if "keywords" not in result:
            result["keywords"] = extract_keywords_from_store_name(result.get("store", ""))

        # 여기가 핵심! GPT 결과와 가장 비슷한 요기요 가게 찾기
        best_match = match_gpt_result_with_yogiyo(result, raw_restaurants)

        if best_match:
            matched_restaurants = [{
                "name": best_match.get("name"),
                "review_avg": best_match.get("review_avg", "5점"),
                "address": "카테고리: " + ", ".join(best_match.get("categories", []))
            }]
        else:
            matched_restaurants = []


    except Exception as e:
        print("GPT 호출 실패:", e)
        result = {
            "store": "GPT 추천 실패",
            "description": "AI 추천이 실패했습니다. 임의 추천으로 대체됩니다.",
            "category": "기타",
            "keywords": []
        }
        is_valid_result = False

    matched_restaurants = []

    description_templates = [
        f"'{text}'가 생각나는 날이에요. 이 메뉴라면 만족스러운 한 끼가 될 거예요!",
        f"기분전환이 필요한 날엔 '{text}'! 이 메뉴 어때요?",
        f"오늘 같은 날엔 '{text}'가 딱이죠! 이 가게 추천해요!",
    ]
    result["description"] = random.choice(description_templates)


    if not is_valid_result and not matched_restaurants:
        fallback = random.choice(raw_restaurants)
        result = {
            "store": fallback.get("name", "추천 없음"),
            "description": result["description"],
            "category": ", ".join(fallback.get("categories", [])),
            "keywords": extract_keywords_from_store_name(fallback.get("name", ""))
        }

        matched_restaurants = [{
            "name": fallback.get("name", "추천 없음"),
            "review_avg": fallback.get("review_avg", "5점"),
            "address": fallback.get("address", "주소 없음"),
            "id": fallback.get("id", "없음"),
            "categories": ", ".join(fallback.get("categories", [])),
            "logo": fallback.get("logo_url", ""),
        }]


        print("✅ matched_restaurants 응답:", matched_restaurants)
        print("✅ fallback 응답:", fallback)

    return render(request, 'gomgom_ai/recommend_result.html', {
        "result": result,
        "restaurants": matched_restaurants,
        "keyword": [result.get("store")]
    })