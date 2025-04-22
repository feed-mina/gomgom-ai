# gomgom_ai/views.py
from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings
import os


print("TEMPLATE DIRS:", settings.TEMPLATES[0]['DIRS'])
print("BASE_DIR/templates:", os.path.join(settings.BASE_DIR, 'templates'))

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
