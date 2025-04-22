# gomgom-ai/gomgom_ai/urls.py
from django.urls import path
from gomgom_ai import views

urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.home_view, name='home'),

    # 랜덤메뉴 추천
    path('situation/', views.situation_view, name='situation'),
    path('situation2/', views.situation2_view, name='situation2'),
    path('situation3/', views.situation3_view, name='situation3'),
    path('situation4/', views.situation4_view, name='situation4'),
    path('result/', views.result_view, name='result'),

    # 입맛 테스트
    path('start/', views.start_view, name='start'),
    path('question/', views.question_view, name='question'),
    path('question2/', views.question2_view, name='question2'),
    path('question3/', views.question3_view, name='question3'),
    path('question4/', views.question4_view, name='question4'),
    path('question5/', views.question5_view, name='question5'),
    path('question6/', views.question6_view, name='question6'),
    path('test_result/', views.test_result_view, name='test_result'),
    path('recommend_input/', views.recommend_input, name='recommend_input'),
    path('api/recommend/', views.recommend_food),
]
