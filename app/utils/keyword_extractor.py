from typing import List
import re

def extract_keywords_from_store_name(name: str) -> List[str]:
    """가게 이름에서 키워드 추출"""
    # 한글/영문 2글자 이상 단어만 추출
    keywords = [w for w in re.findall(r"[가-힣a-zA-Z]{2,}", name)]
    return keywords if keywords else [] 