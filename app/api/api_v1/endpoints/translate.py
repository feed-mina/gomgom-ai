from fastapi import APIRouter, Body, HTTPException
from app.utils.translator import translator
import logging
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/translate")
async def translate_texts(texts: list[str] = Body(...)):
    """여러 문장을 한 번에 번역"""
    try:
        # 입력 검증
        if not texts:
            raise HTTPException(status_code=400, detail="번역할 텍스트가 없습니다.")
        
        # 각 텍스트의 길이 검증 (Google Translate API 제한: 5000자)
        max_length = 10000  # 여유있게 설정
        for i, text in enumerate(texts):
            if len(text) > max_length:
                logger.warning(f"텍스트 {i}가 너무 깁니다: {len(text)}자 (제한: {max_length}자)")
                texts[i] = text[:max_length] + "..."  # 잘라내기
        
        logger.info(f"번역 요청: {len(texts)}개 텍스트")
        
        # 여러 문장 병렬 번역 (asyncio.gather)
        async def translate_single(text, idx):
            try:
                if not text.strip():
                    return ""
                logger.debug(f"텍스트 {idx+1}/{len(texts)} 번역 시작: {text[:50]}...")
                translated = await asyncio.wait_for(
                    translator.translate_to_korean(text),
                    timeout=30.0
                )
                logger.debug(f"텍스트 {idx+1}/{len(texts)} 번역 완료")
                return translated
            except asyncio.TimeoutError:
                logger.error(f"텍스트 {idx+1} 번역 타임아웃")
                return text
            except Exception as e:
                logger.error(f"텍스트 {idx+1} 번역 실패: {e}")
                return text
        
        tasks = [translate_single(text, i) for i, text in enumerate(texts)]
        results = await asyncio.gather(*tasks)
        
        logger.info(f"번역 완료: {len(results)}개 텍스트")
        return {"translatedTexts": results}
        
    except Exception as e:
        logger.error(f"번역 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"번역 중 오류가 발생했습니다: {str(e)}")
