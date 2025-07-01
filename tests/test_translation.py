import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.translator import translator

async def test_translation():
    """번역 기능 테스트"""
    print("Google Cloud Translation API 테스트 시작...")
    
    # 한글 -> 영어 번역 테스트
    korean_text = "안녕하세요, 맛있는 음식을 추천해주세요!"
    # Print(f"\n한글 텍스트: {korean_text}")
    
    english_result = await translator.translate_to_english(korean_text)
    if english_result:
        # Print(f"영어 번역: {english_result}")
    else:
        print("번역 실패")
    
    # 영어 -> 한글 번역 테스트
    english_text = "Hello, please recommend delicious food!"
    # Print(f"\n영어 텍스트: {english_text}")
    
    korean_result = await translator.translate_to_korean(english_text)
    if korean_result:
        # Print(f"한글 번역: {korean_result}")
    else:
        print("번역 실패")

if __name__ == "__main__":
    asyncio.run(test_translation()) 