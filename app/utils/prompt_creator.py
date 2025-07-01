from typing import List, Dict, Optional
import openai
import json

def create_yogiyo_prompt_with_testoptions(
    user_text: Optional[str],
    store_keywords_list: List[str],
    score: Optional[Dict[str, int]] = None
) -> str:
    """테스트 결과를 반영한 GPT 프롬프트 생성"""
    if not user_text:
        base_text = "사용자가 특별히 원하는 음식이 없습니다."
    else:
        base_text = f"사용자가 먹고 싶은 음식은 \"{user_text}\"입니다."
    
    score_text = f"\n기분 태그는 {', '.join(score.keys())}입니다." if score else ""

    # 음식점 리스트를 7개로 제한
    limited_store_list = store_keywords_list[:7]

    prompt = f"""
당신은 사용자의 요구사항과 기분 태그를 종합적으로 분석하여 최적의 음식점을 추천하는 전문가입니다.

**사용자 요청**: {base_text}
**기분 태그**: {score_text if score else "없음"}
**사용자 입력 키워드**: "{user_text or '무작위'}"

**음식점 목록** (상위 7개):
{chr(10).join(limited_store_list)}

**추천 조건**:
1. 사용자 요청("{user_text or '무작위'}")과 가장 관련성 높은 음식점 1곳 선택
2. 기분 태그가 있는 경우 이를 고려하여 추천
3. 추천 이유는 감성적이되 구체적인 이유 포함
4. 사용자가 요청한 음식과 직접적으로 연관된 곳 우선

**출력 형식** (반드시 JSON):
{{
    "store": "음식점명",
    "description": "사용자 요청과 연관된 구체적인 추천 이유",
    "category": "주요 카테고리",
    "keywords": ["키워드1", "키워드2", "키워드3"]
}}

**예시**:
사용자: "치킨", 기분: "피곤해"
추천: {{
    "store": "교촌치킨",
    "description": "피곤한 하루 끝에 바삭한 치킨으로 기운을 내세요. 간편하면서도 든든한 선택입니다.",
    "category": "치킨",
    "keywords": ["치킨", "후라이드", "양념치킨", "간편식"]
}}

**중요**: 사용자 요청과 무관한 음식점은 절대 추천하지 마세요.
"""
    return prompt 

def classify_input_prompt(user_input: str) -> str:
    return f"""
다음 사용자 입력을 읽고, 아래 4가지 중 하나로 분류하세요:

1. 음식 (예: 버거, 마라탕, 초밥, 치킨)
2. 기분 (예: 피곤해, 우울해, 기분이 좋아)
3. 상황 (예: 공부 중, 야근 중, 헬스하고 나서)
4. 기타 (명확히 알 수 없는 경우)

사용자 입력: "{user_input}"

아래 형식으로 답변하세요:
{{
    "type": "음식" 또는 "기분" 또는 "상황" 또는 "기타"
}}
예시:
입력: "피곤해"
분류 결과:
{{
  "type": "기분"
}}
"""

async def classify_user_input_via_gpt(user_input: str) -> str:
    prompt = classify_input_prompt(user_input)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "당신은 사용자 입력을 정확히 분류하는 전문가입니다. 항상 JSON 형식으로 응답하고, 입력의 의미를 정확히 파악하여 분류합니다."},
            {"role": "user", "content": prompt}
        ]
    )
    gpt_content = response.choices[0].message.content
    try:
        result = json.loads(gpt_content)
        return result.get("type", "기타")
    except Exception:
        return "기타"

def make_store_info_line(store: dict) -> str:
    name = store.get('name', '')
    categories = ', '.join(store.get('categories', []))
    keywords = ', '.join(store.get('keywords', [])) if store.get('keywords') else ''
    menus = store.get('representative_menus', '')
    tags = ', '.join(store.get('tags', [])) if store.get('tags') else ''
    return f"{name} | 카테고리: {categories} | 대표메뉴: {menus} | 키워드: {keywords} | 태그: {tags}"

def create_yogiyo_prompt_with_options(user_text: str, store_info_list: List[str], score: Optional[Dict] = None, input_type: str = "음식") -> str:
    # 사용자 입력에 따른 구체적인 지시사항 생성
    user_instruction = ""
    if input_type == "음식":
        if user_text:
            user_instruction = f"사용자가 '{user_text}'를 원합니다. 이 음식과 직접적으로 관련된 메뉴나 카테고리를 가진 음식점을 우선적으로 추천하세요."
        else:
            user_instruction = "사용자가 특별한 음식을 요청하지 않았습니다. 다양한 옵션을 제공하세요."
    elif input_type == "기분":
        if "피곤" in user_text or "힘들" in user_text:
            user_instruction = "피곤한 상태이므로 간편하고 든든한 음식을 추천하세요."
        elif "기분 좋" in user_text or "행복" in user_text:
            user_instruction = "기분이 좋은 상태이므로 특별하고 맛있는 음식을 추천하세요."
        elif "우울" in user_text or "슬픈" in user_text:
            user_instruction = "우울한 상태이므로 위로가 되는 편안한 음식을 추천하세요."
        else:
            user_instruction = "사용자의 기분에 맞는 적절한 음식을 추천하세요."
    elif input_type == "상황":
        if "공부" in user_text or "업무" in user_text:
            user_instruction = "집중력이 필요한 상황이므로 가볍고 간편한 음식을 추천하세요."
        elif "야근" in user_text or "늦" in user_text:
            user_instruction = "늦은 시간이므로 배달이 빠르고 간편한 음식을 추천하세요."
        else:
            user_instruction = "상황에 맞는 적절한 음식을 추천하세요."
    else:
        user_instruction = "다양한 옵션을 제공하세요."

    # 음식점 리스트를 7개로 제한
    limited_store_list = store_info_list[:7]
    
    prompt = f"""
당신은 사용자의 요구사항을 정확히 파악하여 최적의 음식점을 추천하는 전문가입니다.

**사용자 요청**: "{user_text}"
**요청 유형**: {input_type}
**추가 지시**: {user_instruction}

**음식점 목록** (상위 7개):
{chr(10).join(limited_store_list)}

**추천 조건**:
1. 사용자 요청("{user_text}")과 가장 관련성 높은 음식점 3곳 선택
2. 각 추천은 구체적이고 현실적인 이유 포함
3. 사용자가 요청한 음식/기분/상황과 직접적으로 연관된 곳 우선

**출력 형식** (반드시 JSON 배열):
[
  {{
    "store": "음식점명",
    "description": "사용자 요청과 연관된 구체적인 추천 이유",
    "category": "주요 카테고리",
    "keywords": ["키워드1", "키워드2", "키워드3"]
  }}
]

**예시**:
사용자: "치킨"
추천: [
  {{
    "store": "교촌치킨",
    "description": "바삭한 후라이드와 매콤달콤한 양념치킨으로 치킨의 진수를 맛볼 수 있어요.",
    "category": "치킨",
    "keywords": ["치킨", "후라이드", "양념치킨", "바삭함"]
  }}
]

사용자: "분식"
추천: [
  {{
    "store": "떡볶이천국",
    "description": "쫄깃한 떡볶이와 바삭한 튀김으로 학교 앞 분식의 향수를 느낄 수 있어요.",
    "category": "분식",
    "keywords": ["떡볶이", "분식", "튀김", "쫄깃함"]
  }}
]

**중요**: 사용자 요청과 무관한 음식점은 절대 추천하지 마세요.
"""
    return prompt