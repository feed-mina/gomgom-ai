
# classify_user_input.py
from openai import OpenAI
import json
import os
from django.conf import settings  # 환경 변수 가져오기

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY") or settings.OPENAI_API_KEY)

def classify_user_input(user_text):
    # GPT한테 물어보기
    classification_prompt = f"""
    사용자가 "{user_text}"라고 입력했어요. 이건 어떤 종류에 해당하나요?

    가능한 분류:
    - 기분 (예: 졸려, 우울해, 기분 좋아)
    - 상황 (예: 친구랑 먹을 거, 혼자 있는 날)
    - 기능 (예: 비타민, 피로회복, 속 편한 음식)
    - 음식 (예: 커리, 김치찌개, 매운음식)

    딱 하나의 분류만 고르고 결과는 JSON으로 주세요:
    {{ "category": "기분" }}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": classification_prompt}]
    )
    result = json.loads(response.choices[0].message.content.strip())
    return result.get("category", "음식")  # 기본값은 음식으로 처리
