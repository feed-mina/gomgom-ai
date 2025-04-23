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
from konlpy.tag import Okt # 한국어 문장 분석기를 준비하는 코드
okt = Okt()
# print(okt.nouns("짬뽕지존-봉천점"))

# name문자열을 형태소 분석해서 (단어,품사)로 나눔, pos == 'Noun' 명사인 단어만 고름
# len(w) > 1 너무 짧은 단어 (예 : '의','가')는 빼고 두글자 이상만
def extract_keywords_from_store_name(name):
    # '짬뽕지존-봉천점' → ['짬뽕', '지존', '봉천']
    keywords = [w for w, pos in okt.pos(name) if pos == 'Noun' and len(w) > 1]
    return keywords

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


    # 1. 요기요 가게 리스트 먼저 불러오기
    restaurants_data = get_yogiyo_restaurants(lat, lng)
    raw_restaurants = restaurants_data.get("restaurants", []) if isinstance(restaurants_data, dict) else restaurants_data
    # 2. NLP 키워드 추출 (상호명 기반)
    store_keywords_list = []
    for r in raw_restaurants:
        name = r.get("name", "")
        keywords = extract_keywords_from_store_name(name)
        # ex: "짬뽕지존 - 짬뽕, 지존, 봉천"
        store_keywords_list.append(f"{name}: {', '.join(keywords)}")

    # 3. GPT 프롬프트 구성
    random.shuffle(store_keywords_list)  # 다양성 확보

    # GPT 프롬프트
    prompt = f"""
    사용자의 상태는 "{text}" 입니다.
    이 단어는 먹고 싶은 음식일 가능성이 높습니다.
    
    아래는 오늘 배달 가능한 음식점들과, 각 가게 이름에서 추출한 주요 키워드입니다:
    {chr(10).join(store_keywords_list[:10])}
    # 10개만 추려서 보냄
  
    목표:
    - 위 음식점 중 사용자가 원하는 "{text}"와 가장 관련 있는 가게를 한 곳 추천해주세요.
    - 추천 이유는 감성적 한 문장으로 설명해주세요.
    - 가게의 대표 카테고리도 함께 알려주세요.
    - 반드시 {text}와 의미적으로 가까운 키워드를 포함한 가게만 고르세요.
    
    조건:
    - 입력한 단어와 관련 없는 가게는 추천하지 마세요.
    - 반드시 입력 키워드와 연관된 키워드를 포함한 가게 중에서 골라주세요.

    결과는 JSON 형식으로 다음처럼 주세요:
    {{ "store": 음식점 이름, "description": 설명, "category": 카테고리, "keywords": [키워드1, 키워드2, ...] }}


    주의:
    - 반드시 유사한 음식군에서만 추천하세요.
    """


    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        gpt_text = response.choices[0].message.content.strip()

        print("✅ GPT 응답:", gpt_text)

        result = json.loads(gpt_text)
        print('result: ',result)

        if not is_related(text, result):
            print("⚠️ 결과가 입력값과 연관성이 낮음. fallback 작동")
            fallback = random.choice(raw_restaurants)
            result = {
                "store": fallback.get("name", "추천 없음"),
                "description": f"'{text}'와 관련된 가게를 찾지 못했어요. 근처 인기 가게를 추천할게요!",
                "category": ", ".join(fallback.get("categories", [])),
                "keywords": extract_keywords_from_store_name(fallback.get("name", ""))
            }

    # fallback: 상호명에서 키워드 추출해서 넣어주기!
        if "keywords" not in result:
            result["keywords"] = extract_keywords_from_store_name(result.get("store", ""))

    except json.JSONDecodeError:
        print("⚠️ GPT 응답 파싱 실패. 응답 원문:")
        print(gpt_text)

        fallback = random.choice(raw_restaurants)
        result = {
            "store": fallback.get("name", "추천 없음"),
            "description": "기분을 달래줄 음식점을 대신 골랐어요!",
            "category": "기타"
        }

    except Exception as e:
        print("❌ GPT 호출 오류:", e)
        fallback = random.choice(raw_restaurants)
        result = {
            "store": fallback.get("name", "추천 없음"),
            "description": "맛있는 음식으로 위로받길 바랄게요!",
            "category": "기타"
        }


    # 4. 결과 가게만 필터링해서 다시 매칭
    matched_restaurants = [
        {
            "name": r.get("name"),
            "review_avg": r.get("review_avg"),
            "address": "카테고리: " + ", ".join(r.get("categories", []))  # 임시 대체
        }
        for r in raw_restaurants
        if result.get("store") in r.get("name", "")
    ]


    print('matched_restaurants: ',matched_restaurants)
    return render(request, 'gomgom_ai/recommend_result.html', {
        "result": result,
        "restaurants": matched_restaurants,
        "keyword": [result.get("store")]
    })