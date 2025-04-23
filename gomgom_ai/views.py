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

        content = response['choices'][0]['message']['content']
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
    candidates = []

    for food in food_list:
        for tag in food['tags']:
            if score.get(tag, 0) >= 2:
                candidates.append(food['name'])
                break

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
        'description': description
    })


# print("TEMPLATE DIRS:", settings.TEMPLATES[0]['DIRS'])
# print("BASE_DIR/templates:", os.path.join(settings.BASE_DIR, 'templates'))

def home_view(request):
    return render(request, 'gomgom_ai/home.html')
def main(request):
    return render(request, 'gomgom_ai/main.html')

# 랜덤 추천
def situation_view(request):
    return render(request, 'gomgom_ai/situation.html')

def situation2_view(request):
    return render(request, 'gomgom_ai/situation2.html')

def situation3_view(request):
    return render(request, 'gomgom_ai/situation3.html')
def situation4_view(request):
    return render(request, 'gomgom_ai/situation4.html')

def result_view(request):
    return render(request, 'gomgom_ai/result.html')
# 입맛 테스트
def start_view(request):
    print("넘어온 text:", request.GET.get('text'))
    print("넘어온 lat:", request.GET.get('lat'))
    print("넘어온 lng:", request.GET.get('lng'))

    return render(request, 'gomgom_ai/start.html')

def question_view(request):
    return render(request, 'gomgom_ai/question.html')

def question2_view(request):
    return render(request, 'gomgom_ai/question2.html')

def question3_view(request):
    return render(request, 'gomgom_ai/question3.html')

def question4_view(request):
    return render(request, 'gomgom_ai/question4.html')

def question5_view(request):
    return render(request, 'gomgom_ai/question5.html')

def question6_view(request):
    return render(request, 'gomgom_ai/question6.html')


# def test_result_view(request):
#     return render(request, 'gomgom_ai/test_result.html')
def test_view(request):
    return render(request, 'gomgom_ai/test.html')


def recommend_input(request):
    text = request.GET.get('text')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    print("입력값:", text)
    print("위치:", lat, lng)

    # 여기에 요기요 API나 LLM 처리 넣을 예정!
    dummy_result = {
        "recommendation": "떡볶이",
        "confidence": "높음"
    }

    return render(request, 'gomgom_ai/recommend_result.html', {"result": dummy_result})
