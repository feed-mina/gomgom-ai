def create_yogiyo_prompt_with_testoptions(user_text, store_keywords_list, score=None):
    """
    사용자의 입력(user_text)과 요기요 가게 리스트(상호명 + 키워드), 그리고 기분 태그(score)를 기반으로
    GPT가 적절한 가게를 고를 수 있도록 조건을 강화한 프롬프트
    """
    base_text = f"사용자가 먹고 싶은 음식은 \"{user_text or '무작위'}\"입니다."
    score_text = f"\n기분 태그는 {', '.join(score.keys())}입니다." if score else ""

    prompt = f"""
    {base_text}{score_text}
    사용자 입력 키워드: "{user_text}"
    이 키워드는 사용자가 **먹고 싶은 음식**을 의미합니다. 예를 들어 "매운음식"이라면 매콤한 음식, 매운맛 위주 메뉴가 포함된 가게를 추천해야 합니다.

    아래는 현재 배달 가능한 음식점 리스트입니다. 각 줄은 "가게명: 키워드들" 형식입니다.
 
    ---
    {chr(10).join(store_keywords_list[:10])}
    ---
    당신의 역할:
    - 위 리스트에서 "{user_text}"와 **맛·카테고리·유형적으로 가장 잘 맞는** 가게를 1개 고르세요.
    - 추천 이유는 감성적으로 쓰되, **사용자 입력과의 관련성**을 포함하세요.

    조건:
    - 사용자 요청({user_text}) 또는 기분 태그와 의미적으로 가장 가까운 음식점을 골라주세요.
    - 추천 이유를 감성적으로 한 줄로 써주세요.
    - 가게 이름에 \"{user_text}\"가 직접 없더라도, 의미가 통하거나 비슷한 음식이면 괜찮습니다.
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
