import httpx
import asyncio
from typing import Optional, Dict, Any
from app.core.config import settings
import logging
import os
from google.cloud import translate_v2 as translate
from google.oauth2 import service_account

from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

class TranslationService:
    """번역 서비스 - Google Cloud Translation API 사용 (선택적)"""
    
    def __init__(self):
        # 서비스 계정 키 파일 경로 확인
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다. 번역 기능이 비활성화됩니다.")
            self.translate_client = None
            return
        
        try:
            # 서비스 계정 키 파일로 인증
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.translate_client = translate.Client(credentials=credentials)
            logger.info("Google Cloud Translation API 클라이언트(서비스 계정)로 초기화 성공")
        except Exception as e:
            logger.warning(f"Google Cloud Translation API 초기화 실패: {e}. 번역 기능이 비활성화됩니다.")
            self.translate_client = None
    
    async def translate_to_english(self, korean_text: str) -> str:
        """한글을 영어로 번역 (실패시 원본 반환)"""
        if not self.translate_client:
            logger.debug("번역 기능이 비활성화되어 원본 텍스트를 반환합니다.")
            return korean_text
        
        try:
            result = self.translate_client.translate(
                korean_text,
                source_language="ko",
                target_language="en"
            )
            return result["translatedText"]
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return korean_text
    
    async def translate_to_korean(self, english_text: str) -> str:
        """영어를 한글로 번역 (실패시 원본 반환)"""
        if not self.translate_client:
            logger.debug("번역 기능이 비활성화되어 원본 텍스트를 반환합니다.")
            return english_text
        
        try:
            result = self.translate_client.translate(
                english_text,
                source_language="en",
                target_language="ko"
            )
            return result["translatedText"]
        except Exception as e:
            logger.warning(f"번역 중 오류 발생: {e}. 원본 텍스트를 반환합니다.")
            return english_text

# 전역 번역 서비스 인스턴스
translator = TranslationService() 