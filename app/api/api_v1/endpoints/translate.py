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
        
        # 여러 문장 한 번에 번역 (타임아웃 설정)
        results = []
        for i, text in enumerate(texts):
            try:
                if not text.strip():
                    results.append("")
                    continue
                    
                logger.debug(f"텍스트 {i+1}/{len(texts)} 번역 시작: {text[:50]}...")
                
                # 타임아웃 설정 (30초)
                translated = await asyncio.wait_for(
                    translator.translate_to_korean(text),
                    timeout=30.0
                )
                results.append(translated)
                logger.debug(f"텍스트 {i+1}/{len(texts)} 번역 완료")
                
            except asyncio.TimeoutError:
                logger.error(f"텍스트 {i+1} 번역 타임아웃")
                results.append(text)  # 타임아웃 시 원본 반환
            except Exception as e:
                logger.error(f"텍스트 {i+1} 번역 실패: {e}")
                results.append(text)  # 실패시 원본 반환
        
        logger.info(f"번역 완료: {len(results)}개 텍스트")
        return {"translatedTexts": results}
        
    except Exception as e:
        logger.error(f"번역 API 오류: {e}")
        raise HTTPException(status_code=500, detail=f"번역 중 오류가 발생했습니다: {str(e)}")
