# gomgom_ai/views.py
from django.shortcuts import render
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings
import os
openai.api_key = settings.OPENAI_API_KEY


# print("TEMPLATE DIRS:", settings.TEMPLATES[0]['DIRS'])
# print("BASE_DIR/templates:", os.path.join(settings.BASE_DIR, 'templates'))


@csrf_exempt
def recommend_food(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        user_text = body.get('text', '')

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 음식 추천 전문가입니다."},
                {"role": "user", "content": f"{user_text} 조건에 맞는 음식을 추천해줘. 간단한 설명도 함께 부탁해."}
            ]
        )

        result = response['choices'][0]['message']['content']
        return JsonResponse({'recommendation': result})

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


def test_result_view(request):
    return render(request, 'gomgom_ai/test_result.html')



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

    return render(request, 'recommend_result.html', {"result": dummy_result})
