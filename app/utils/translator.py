import httpx
import asyncio
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging
import os
import json
import re

from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

class TranslationService:
    """번역 서비스 - Google Cloud Translation API 사용 (API 키 방식)"""
    
    def __init__(self):
        # API 키 확인
        self.api_key = settings.GOOGLE_TRANSLATE_API_KEY
        if not self.api_key:
            logger.warning("GOOGLE_TRANSLATE_API_KEY 환경변수가 설정되지 않았습니다. 번역 기능이 비활성화됩니다.")
            self.translate_client = None
            return
        
        try:
            # API 키로 Google Translate API 클라이언트 초기화
            self.base_url = "https://translation.googleapis.com/language/translate/v2"
            # Google Translate API 글자수 제한 (5000자)
            self.max_chunk_size = 4000  # 안전하게 4000자로 설정
            logger.info("Google Cloud Translation API 클라이언트(API 키)로 초기화 성공")
        except Exception as e:
            logger.warning(f"Google Cloud Translation API 초기화 실패: {e}. 번역 기능이 비활성화됩니다.")
            self.translate_client = None
    
    def _split_text_into_chunks(self, text: str, max_size: int = None) -> List[str]:
        """텍스트를 청크로 나누기 (문장 단위로 분할)"""
        if max_size is None:
            max_size = self.max_chunk_size
        
        if len(text) <= max_size:
            return [text]
        
        # 문장 단위로 분할 (마침표, 느낌표, 물음표 기준)
        sentences = re.split(r'([.!?]+)', text)
        chunks = []
        current_chunk = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            punctuation = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + punctuation
            
            # 현재 청크에 문장을 추가했을 때 제한을 초과하는지 확인
            if len(current_chunk + full_sentence) > max_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = full_sentence
                else:
                    # 단일 문장이 제한을 초과하는 경우 강제로 분할
                    chunks.append(full_sentence[:max_size])
                    current_chunk = full_sentence[max_size:]
            else:
                current_chunk += full_sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _translate_chunk(self, text: str, source: str, target: str) -> str:
        """단일 청크 번역"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    params={"key": self.api_key},
                    json={
                        "q": text,
                        "source": source,
                        "target": target,
                        "format": "text"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    translated_text = data["data"]["translations"][0]["translatedText"]
                    return translated_text
                else:
                    logger.warning(f"번역 API 오류: {response.status_code} - {response.text}")
                    return text
                    
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return text
    
    async def translate_to_english(self, korean_text: str) -> str:
        """한글을 영어로 번역 (실패시 원본 반환)"""
        if not self.api_key:
            logger.debug("번역 기능이 비활성화되어 원본 텍스트를 반환합니다.")
            return korean_text
        
        try:
            logger.debug(f"한글->영어 번역 시작: '{korean_text[:50]}...'")
            
            # 텍스트를 청크로 분할
            chunks = self._split_text_into_chunks(korean_text)
            logger.debug(f"텍스트를 {len(chunks)}개 청크로 분할")
            
            # 각 청크를 병렬로 번역
            tasks = [
                self._translate_chunk(chunk, "ko", "en") 
                for chunk in chunks
            ]
            
            translated_chunks = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 번역 결과 결합
            result = " ".join([
                chunk if isinstance(chunk, str) else str(chunk) 
                for chunk in translated_chunks
            ])
            
            logger.debug(f"번역 완료: '{korean_text[:50]}...' -> '{result[:50]}...'")
            return result
                    
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return korean_text
    
    async def translate_to_korean(self, english_text: str) -> str:
        """영어를 한글로 번역 (실패시 원본 반환)"""
        if not self.api_key:
            logger.debug("번역 기능이 비활성화되어 원본 텍스트를 반환합니다.")
            return english_text
        
        try:
            logger.debug(f"영어->한글 번역 시작: '{english_text[:50]}...'")
            
            # 텍스트를 청크로 분할
            chunks = self._split_text_into_chunks(english_text)
            logger.debug(f"텍스트를 {len(chunks)}개 청크로 분할")
            
            # 각 청크를 병렬로 번역
            tasks = [
                self._translate_chunk(chunk, "en", "ko") 
                for chunk in chunks
            ]
            
            translated_chunks = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 번역 결과 결합
            result = " ".join([
                chunk if isinstance(chunk, str) else str(chunk) 
                for chunk in translated_chunks
            ])
            
            logger.debug(f"번역 완료: '{english_text[:50]}...' -> '{result[:50]}...'")
            return result
                    
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return english_text

# 전역 번역 서비스 인스턴스
translator = TranslationService() 