from typing import List, Dict, Any
import re
from .keyword_extractor import extract_keywords_from_store_name

def match_gpt_result_with_yogiyo(gpt_result: Dict[str, Any], restaurants: List[Dict[str, Any]]) -> Dict[str, Any]:
    """GPT 결과와 요기요 가게 리스트를 매칭"""
    def clean(s: str) -> str:
        return re.sub(r"[^가-힣a-zA-Z0-9]", "", s).replace(" ", "").lower()

    target = clean(gpt_result['store'])
    keywords = gpt_result.get("keywords", [])
    best_match = None

    for store in restaurants:
        name = store.get("name", "")
        cleaned = clean(name)
        
        # 정확한 이름 매칭
        if target in cleaned or cleaned in target:
            return store
            
        # 키워드 기반 매칭
        store_keywords = extract_keywords_from_store_name(name)
        if any(k in store_keywords for k in keywords):
            best_match = store

    return best_match 