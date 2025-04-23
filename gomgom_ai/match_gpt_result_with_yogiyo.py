
def match_gpt_result_with_yogiyo(gpt_result, restaurants):
    """
    GPT 결과(gpt_result['store'])와 요기요 가게 리스트 중 가장 유사한 가게를 찾음.
    - store 이름 전처리
    - 키워드 기반 유사도 보완
    - fallback은 없음. 매칭된 것만 반환
    """
    import re

    def clean(s):
        # 괄호, 특수문자 제거 후 공백 제거
        return re.sub(r"[^가-힣a-zA-Z0-9]", "", s).replace(" ", "").lower()

    def keyword_overlap(gpt_keywords, store_name):
        from konlpy.tag import Okt
        okt = Okt()
        name_keywords = [w for w, pos in okt.pos(store_name) if pos == 'Noun' and len(w) > 1]
        return any(k in name_keywords for k in gpt_keywords)

    target = clean(gpt_result['store'])
    keywords = gpt_result.get("keywords", [])

    best_match = None

    for store in restaurants:
        name = store.get("name", "")
        cleaned = clean(name)
        if target in cleaned or cleaned in target:
            return store  # 완전 매칭
        if keyword_overlap(keywords, name):
            best_match = store  # 키워드 유사도 기반 매칭

    return best_match  # 유사한 거 하나라도 있으면 반환, 없으면 None
