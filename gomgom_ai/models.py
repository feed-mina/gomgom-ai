from django.db import models

class Recommendation(models.Model):
    input_text = models.TextField()
    selected_types = models.JSONField()
    recommended_store = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255)
    keywords = models.JSONField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)  # 사용자 IP
    is_success = models.BooleanField(default=True)                 # 추천 성공 여부
    gpt_raw_response = models.JSONField(null=True, blank=True)     # GPT 원본 응답
    matched_restaurant_id = models.IntegerField(null=True, blank=True)  # 매칭된 가게 ID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.input_text} → {self.recommended_store}"
