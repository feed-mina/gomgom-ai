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

    prompt = f"""
    {base_text}{score_text}
    사용자 입력 키워드: "{user_text or '무작위'}"
    이 키워드는 사용자가 **먹고 싶은 음식**을 의미합니다. 예를 들어 "매운음식"이라면 매콤한 음식, 매운맛 위주 메뉴가 포함된 가게를 추천해야 합니다.

    아래는 현재 배달 가능한 음식점 리스트입니다. 각 줄은 "가게명: 키워드들" 형식입니다.
 
    ---
    {chr(10).join(store_keywords_list[:10])}
    ---
    당신의 역할:
    - 위 리스트에서 "{user_text or '무작위'}"와 **맛·카테고리·유형적으로 가장 잘 맞는** 가게를 1개 고르세요.
    - 추천 이유는 감성적으로 쓰되, **사용자 입력과의 관련성**을 포함하세요.
    - 사용자 입력이 없는 경우, 기분 태그를 기반으로 추천해주세요.

    조건:
    - 사용자 요청({user_text or '무작위'}) 또는 기분 태그와 의미적으로 가장 가까운 음식점을 골라주세요.
    - 추천 이유를 감성적으로 한 줄로 써주세요.
    - 가게 이름에 \"{user_text or '무작위'}\"가 직접 없더라도, 의미가 통하거나 비슷한 음식이면 괜찮습니다.
    - 결과는 반드시 JSON 형식으로 아래처럼 주세요:
        {{
            "store": 음식점 이름,
            "description": 감성적 설명,
            "category": 대표 카테고리,
            "keywords": [관련 키워드1, 관련 키워드2, ...]
        }}

    주의:
    - 입력값 또는 기분 태그와 연관 없는 가게는 절대 추천하지 마세요.
    - 꼭 의미적으로 유사한 가게를 골라야 합니다.
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
        messages=[{"role": "user", "content": prompt}]
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
    prompt = f"""
너는 사용자 입력을 기반으로 딱 맞는 음식점을 고르는 추천 전문가야.
사용자 입력은 \"기분\", \"상황\", 또는 \"음식\"일 수 있어.
입력: \"{user_text}\"
이 입력은 \"{input_type}\"에 해당해.

조건:
- 입력과 가장 잘 맞는 음식점 3곳을 골라줘.
- 음식점은 아래 리스트 중에서만 선택해.
- 설명은 감성적이되 현실적인 이유로, 한 문장으로 써줘.
- 결과는 반드시 아래 JSON 배열 형식으로만 출력해.
- 연관 없는 음식점은 추천하지 마세요.

음식점 리스트:
{chr(10).join(store_info_list[:10])}

출력 예시:
[
  {{
    "store": "버거킹",
    "description": "피곤한 하루 끝에 빠르게 즐기기 좋은 든든한 선택이에요.",
    "category": "패스트푸드",
    "keywords": ["버거", "패스트푸드", "간편식"]
  }},
  {{
    "store": "맘스터치",
    "description": "든든한 치킨버거로 에너지를 충전할 수 있어요.",
    "category": "치킨, 패스트푸드",
    "keywords": ["치킨", "버거", "패스트푸드"]
  }},
  {{
    "store": "롯데리아",
    "description": "가볍게 즐기기 좋은 다양한 버거 메뉴가 있어요.",
    "category": "패스트푸드",
    "keywords": ["버거", "패스트푸드"]
  }}
]
"""
    return prompt