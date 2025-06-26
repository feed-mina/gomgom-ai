import httpx
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings
import logging
import os
import json

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
            logger.info("Google Cloud Translation API 클라이언트(API 키)로 초기화 성공")
        except Exception as e:
            logger.warning(f"Google Cloud Translation API 초기화 실패: {e}. 번역 기능이 비활성화됩니다.")
            self.translate_client = None
    
    async def translate_to_english(self, korean_text: str) -> str:
        """한글을 영어로 번역 (실패시 원본 반환)"""
        if not self.api_key:
            logger.debug("번역 기능이 비활성화되어 원본 텍스트를 반환합니다.")
            return korean_text
        
        try:
            logger.debug(f"한글->영어 번역 시작: '{korean_text}'")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    params={"key": self.api_key},
                    json={
                        "q": korean_text,
                        "source": "ko",
                        "target": "en",
                        "format": "text"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    translated_text = data["data"]["translations"][0]["translatedText"]
                    logger.debug(f"번역 완료: '{korean_text}' -> '{translated_text}'")
                    return translated_text
                else:
                    logger.warning(f"번역 API 오류: {response.status_code} - {response.text}")
                    return korean_text
                    
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return korean_text
    
    async def translate_to_korean(self, english_text: str) -> str:
        """영어를 한글로 번역 (실패시 원본 반환)"""
        if not self.api_key:
            logger.debug("번역 기능이 비활성화되어 원본 텍스트를 반환합니다.")
            return english_text
        
        try:
            logger.debug(f"영어->한글 번역 시작: '{english_text}'")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    params={"key": self.api_key},
                    json={
                        "q": english_text,
                        "source": "en",
                        "target": "ko",
                        "format": "text"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    translated_text = data["data"]["translations"][0]["translatedText"]
                    logger.debug(f"번역 완료: '{english_text}' -> '{translated_text}'")
                    return translated_text
                else:
                    logger.warning(f"번역 API 오류: {response.status_code} - {response.text}")
                    return english_text
                    
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return english_text

# 전역 번역 서비스 인스턴스
translator = TranslationService() 