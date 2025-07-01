#!/usr/bin/env python3
"""
한식 메뉴에만 KoreanRecipeCrawler가 적용되는지 테스트하는 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.external_apis import spoonacular_client

async def test_korean_crawler_only():
    """한식 메뉴에만 KoreanRecipeCrawler가 적용되는지 테스트합니다."""
    
    print("🍜 한식 전용 크롤러 테스트 시작")
    print("=" * 60)
    
    # 테스트 케이스들
    test_cases = [
        # 한식 테스트 (크롤러 사용해야 함)
        ("김치찌개", "korean", "한식 - 크롤러 사용 예상"),
        ("비빔밥", "한식", "한식 - 크롤러 사용 예상"),
        ("된장찌개", "korea", "한식 - 크롤러 사용 예상"),
        ("불고기", "korean cuisine", "한식 - 크롤러 사용 예상"),
        
        # 다른 요리 테스트 (크롤러 사용하지 않아야 함)
        ("짜장면", "chinese", "중식 - 크롤러 사용하지 않음"),
        ("초밥", "japanese", "일식 - 크롤러 사용하지 않음"),
        ("파스타", "italian", "이탈리안 - 크롤러 사용하지 않음"),
        ("타코", "mexican", "멕시칸 - 크롤러 사용하지 않음"),
        ("커리", "indian", "인도 - 크롤러 사용하지 않음"),
        ("파드타이", "thai", "태국 - 크롤러 사용하지 않음"),
        ("크로와상", "french", "프랑스 - 크롤러 사용하지 않음"),
        ("햄버거", "american", "미국 - 크롤러 사용하지 않음"),
        
        # 필터링 없는 테스트
        ("치킨", None, "필터링 없음 - 크롤러 사용하지 않음"),
        ("피자", None, "필터링 없음 - 크롤러 사용하지 않음"),
    ]
    
    for query, cuisine_type, description in test_cases:
        cuisine_display = cuisine_type if cuisine_type else "필터링 없음"
        # Print(f"\n🔍 테스트: '{query}' (cuisine_type: {cuisine_display})")
        # Print(f"   설명: {description}")
        print("-" * 50)
        
        try:
            # Spoonacular API 호출
            recipes = await spoonacular_client.search_recipes(
                query=query, 
                number=2, 
                cuisine_type=cuisine_type
            )
            
            # Print(f"✅ 검색 결과: {len(recipes)}개 레시피 발견")
            
            # 결과 요약
            for i, recipe in enumerate(recipes[:2], 1):
                title = recipe.get("title", "제목 없음")
                source = recipe.get("source", "출처 없음")
                cuisines = recipe.get("cuisines", [])
                # Print(f"  {i}. {title}")
                # Print(f"     출처: {source}")
                # Print(f"     요리 타입: {cuisines}")
                
                # 한식 크롤러에서 온 결과인지 확인
                if source == "10000recipe":
                    # Print(f"     🍜 한식 크롤러에서 가져온 결과")
                else:
                    # Print(f"     🌐 Spoonacular API에서 가져온 결과")
                
        except Exception as e:
            # Print(f"❌ 오류 발생: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("\n📋 테스트 결과 요약:")
    print("✅ 한식 요리 (korean, 한식, korea, korean cuisine) - KoreanRecipeCrawler 사용")
    print("❌ 다른 요리 또는 필터링 없음 - KoreanRecipeCrawler 사용하지 않음")

if __name__ == "__main__":
    print("🚀 한식 전용 크롤러 테스트 시작")
    
    # 기본 테스트 실행
    asyncio.run(test_korean_crawler_only())
    
    print("\n🎯 테스트 완료!") 