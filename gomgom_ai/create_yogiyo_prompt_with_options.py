def create_yogiyo_prompt_with_options(user_text, store_keywords_list, score=None, input_type="음식"):
    if input_type == "기분":
        context = f'사용자의 현재 기분은 "{user_text}"입니다.'
        relevance = f'"{user_text}"일 때 먹으면 위로가 되거나 잘 어울리는 음식을 추천해주세요.'
    elif input_type == "상황":
        context = f'사용자의 상황은 "{user_text}"입니다.'
        relevance = f'"{user_text}"에 어울리는 음식 또는 분위기의 가게를 골라주세요.'
    elif input_type == "기능":
        context = f'사용자의 건강 목적 또는 기능적 요구는 "{user_text}"입니다.'
        relevance = f'"{user_text}"에 맞는 음식 효능을 고려해 추천해주세요.'
    else:
        context = f'사용자가 먹고 싶은 음식은 "{user_text}"입니다.'
        relevance = f'"{user_text}"와 가장 비슷하거나 관련 있는 음식을 추천해주세요.'

    prompt = f"""
    {context}
    사용자 입력 키워드: "{user_text}"

    아래는 현재 배달 가능한 음식점 리스트입니다. 각 줄은 "가게명: 키워드들" 형식입니다.
    ---
    {chr(10).join(store_keywords_list[:10])}
    ---

    조건:
    - {relevance}
    - 추천 이유를 감성적으로 한 줄로 써주세요.
    - 결과는 반드시 JSON 형식으로 아래처럼 주세요:
        {{
            "store": 음식점 이름,
            "description": 감성적 설명,
            "category": 대표 카테고리,
            "keywords": [관련 키워드1, 관련 키워드2, ...]
        }}
    """
    return prompt
