# gomgom-ai/gomgom_ai/urls.py
from django.urls import path
from gomgom_ai import views

urlpatterns = [
    path('', views.main, name='main'),
    path('home/', views.home_view, name='home'),
    # 입맛 테스트
    path('start/', views.start_view, name='start'),
    path('test/', views.test_view, name='test'),
    path('test_result/', views.test_result_view, name='test_result'),
    path('recommend_input/', views.recommend_input, name='recommend_input'),
    path('restaurant_list/', views.restaurant_list_view, name='restaurant_list'),
]
