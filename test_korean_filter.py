#!/usr/bin/env python3
"""
한식 필터링 기능 테스트 스크립트
"""

import asyncio
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.external_apis import spoonacular_client
from app.core.config import settings

async def test_korean_filtering():
    """한식 필터링 기능을 테스트합니다."""
    
    print("🍜 한식 필터링 기능 테스트 시작")
    print("=" * 50)
    
    # 테스트 쿼리들
    test_queries = [
        ("김치", "한식"),
        ("비빔밥", "korean"),
        ("된장찌개", "korea"),
        ("치킨", None),  # 일반 검색 (한식 필터링 없음)
    ]
    
    for query, cuisine_type in test_queries:
        print(f"\n🔍 검색 테스트: '{query}' (cuisine_type: {cuisine_type})")
        print("-" * 40)
        
        try:
            # Spoonacular API 호출
            recipes = await spoonacular_client.search_recipes(
                query=query, 
                number=5, 
                cuisine_type=cuisine_type
            )
            
            print(f"✅ 검색 결과: {len(recipes)}개 레시피 발견")
            
            # 결과 요약
            for i, recipe in enumerate(recipes[:3], 1):  # 상위 3개만 표시
                title = recipe.get("title", "제목 없음")
                cuisines = recipe.get("cuisines", [])
                print(f"  {i}. {title}")
                print(f"     요리 타입: {cuisines}")
                
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 테스트 완료!")

async def test_api_endpoint():
    """API 엔드포인트를 통한 한식 필터링 테스트"""
    
    print("\n🌐 API 엔드포인트 테스트")
    print("=" * 50)
    
    # FastAPI 서버가 실행 중인지 확인
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            # 한식 필터링 테스트
            response = await client.get(
                "http://localhost:8000/api/v1/recommendations/search",
                params={
                    "query": "김치",
                    "number": 3,
                    "cuisine_type": "korean"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 응답 성공: {data['total_results']}개 레시피")
                
                for i, recipe in enumerate(data['recipes'][:2], 1):
                    print(f"  {i}. {recipe['title']}")
            else:
                print(f"❌ API 오류: {response.status_code}")
                
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")
        print("💡 FastAPI 서버가 실행 중인지 확인해주세요.")

if __name__ == "__main__":
    print("🚀 한식 필터링 테스트 시작")
    
    # 기본 테스트 실행
    asyncio.run(test_korean_filtering())
    
    # API 엔드포인트 테스트 (선택사항)
    try:
        asyncio.run(test_api_endpoint())
    except Exception as e:
        print(f"API 엔드포인트 테스트 건너뜀: {e}")
    
    print("\n✨ 모든 테스트 완료!") 