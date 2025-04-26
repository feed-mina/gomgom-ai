from django.contrib import admin
from .models import Recommendation

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'input_text', 'recommended_store', 'created_at')
    search_fields = ('input_text', 'recommended_store')
    list_filter = ('created_at',)
