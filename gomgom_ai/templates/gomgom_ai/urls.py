# gomgom-ai/gomgom_ai/urls.py
from django.urls import path
from ... import views

urlpatterns = [
    path('', views.main, name='main'),
    path('start_test/', views.start_test, name='start_test'),
    path('recommend_random/', views.recommend_random, name='recommend_random'),
]
