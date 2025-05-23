# gomgom-ai/gomgom_ai/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from gomgom_ai import views
from django.http import HttpResponseNotFound
from django.contrib import admin

def skip_wordpress(request):
    return HttpResponseNotFound("")
urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', skip_wordpress),
    path('', views.main, name='main'),
    path('home/', views.home_view, name='home'),
    path('start/', views.start_view, name='start'),  # 입맛 테스트
    path('test/', views.test_view, name='test'),
    path('test_result/', views.test_result_view, name='test_result'),
    path('recommend_result/', views.recommend_result, name='recommend_result'),
    path('restaurant_list/', views.restaurant_list_view, name='restaurant_list'),
    path('async-test/', views.async_test_view),
    path('api/ip-location/', views.get_ip_location),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
