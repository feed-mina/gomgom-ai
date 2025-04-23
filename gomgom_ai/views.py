# gomgom_ai/views.py
from django.shortcuts import render
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings
import os
from .data import all_dishes
import json
from pathlib import Path
import random
import re

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
    prompt = f"""
    이 음식 중 오늘 사용자에게 가장 어울리는 음식을 골라줘:
    {', '.join(food_list)}

    조건:
    - 사용자 기분을 좋게 할 만한 음식
    - 추천 이유를 감성적으로 한 줄로 설명해줘
    - 결과는 JSON 형식으로 줘
    예: {{"food": "김치찌개", "description": "익숙한 매콤함이 오늘 하루를 위로해줄 거예요."}}
    주의: JSON 키와 문자열에는 반드시 "쌍따옴표"를 사용해주세요.
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
        print(" GPT 응답 JSON 파싱 실패! 응답 내용:")
        print(content)

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

    types = [request.GET.get(f'type{i + 1}') for i in range(6)]
    score = {}

    for t in types:
        if t:
            score[t] = score.get(t, 0) + 1

    food_list = load_food_list()
    food_data_dict = {item['name']: item['tags'] for item in food_list}
    tag_to_category = {
        "spicy": ["분식", "중식", "치킨"],
        "mild": ["도시락죽", "한식"],
        "adventurous": ["아시안", "일식돈까스", "회초밥", "카페디저트"],
        "safe": ["한식", "프랜차이즈", "분식"],
        "foreign": ["아시안", "중식", "일식돈까스"],
        "japanese": ["일식돈까스", "회초밥"],
        "korean": ["한식", "도시락죽"],
        "chinese": ["중식"],
        "western": ["피자양식"],
        "thai": ["아시안"],
        "mexican": ["아시안", "샌드위치"],
        "snack": ["분식", "테이크아웃"],
        "fusion": ["프랜차이즈"]
    }
    candidates = []

    for food in food_list:
        for tag in food['tags']:
            if score.get(tag, 0) >= 2:
                candidates.append(food['name'])
                break


    # 요기요 카테고리 추출
    recommended_categories = set()
    for tag in score:
        if score[tag] >= 2 and tag in tag_to_category:
            recommended_categories.update(tag_to_category[tag])

    if not candidates:
        candidates = [
            '김치찌개', '된장찌개', '계란말이', '토스트', '라면',
            '오므라이스', '카레라이스', '떡국', '소고기무국', '잡채밥'
        ]

    gpt_result = ask_gpt_to_choose(candidates, food_data_dict)

    food = gpt_result["food"]
    description = gpt_result["description"]

    return render(request, 'gomgom_ai/test_result.html', {
        'food': food,
        'description': description,
        'categories': list(recommended_categories)  # 요기요 API 연동용
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
def recommend_input(request):
    text = request.GET.get('text')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    print("입력값:", text)
    print("위치:", lat, lng)



    # GPT에게 추천 요청
    food_list = load_food_list()
    food_names = [food['name'] for food in food_list]
    food_tags = {food['name']: food['tags'] for food in food_list}

    gpt_result = ask_gpt_to_choose(food_names, food_tags)


    # GPT에게 사용자 입력 반영한 프롬프트 구성
    prompt = f"""
    아래는 사용자의 상태입니다:
    "{text}"

    이 상태에 맞는 음식을 다음 중 하나에서 골라줘:
    {', '.join(food_names)}

    조건:
    - 감성적이고 따뜻한 문장으로 이유를 설명해줘
    - 결과는 반드시 JSON 형식으로 줘
    예: {{"food": "김치찌개", "description": "익숙한 매콤함이 오늘 하루를 위로해줄 거예요."}}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = json.loads(response.choices[0].message.content)
    except Exception as e:
        print("GPT 오류:", e)
        # 예외 시 랜덤 처리
        fallback = random.choice(food_names)
        result = {
            "food": fallback,
            "description": generate_emotional_description(fallback, food_tags.get(fallback, []))
        }

    return render(request, 'gomgom_ai/recommend_result.html', {"result": result})