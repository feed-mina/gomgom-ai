# gomgom_ai/views.py
from django.shortcuts import render

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