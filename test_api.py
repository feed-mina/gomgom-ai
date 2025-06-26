import asyncio
import httpx
import json
from typing import Dict, Any

# API 기본 URL
BASE_URL = "http://localhost:8000"

async def test_health_check():
    """헬스체크 API 테스트"""
    print("🔍 헬스체크 API 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ 헬스체크 성공: {response.status_code}")
            print(f"📄 응답: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ 헬스체크 실패: {e}")
            return False

async def test_recipe_search():
    """레시피 검색 API 테스트"""
    print("\n🍳 레시피 검색 API 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            # 올바른 엔드포인트 사용
            params = {"query": "김치찌개", "number": 3}
            response = await client.get(f"{BASE_URL}/api/v1/recommendations/search", params=params)
            print(f"✅ 레시피 검색 성공: {response.status_code}")
            
            data = response.json()
            if "recipes" in data:
                print(f"📄 검색된 레시피 수: {len(data['recipes'])}")
                for i, recipe in enumerate(data['recipes'][:2], 1):
                    print(f"  {i}. {recipe.get('title', '제목 없음')}")
            else:
                print(f"📄 응답: {data}")
            return True
        except Exception as e:
            print(f"❌ 레시피 검색 실패: {e}")
            return False

async def test_recipe_recommendations():
    """레시피 추천 API 테스트"""
    print("\n🎯 레시피 추천 API 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            # 추천 요청 데이터
            request_data = {
                "query": "돼지고기 김치 두부",
                "number": 5,
                "include_price": True,
                "max_cooking_time": 30,
                "cuisine_type": "Korean"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/recommendations/search",
                json=request_data
            )
            print(f"✅ 레시피 추천 성공: {response.status_code}")
            
            data = response.json()
            if "recipes" in data:
                print(f"📄 추천된 레시피 수: {len(data['recipes'])}")
                for i, recipe in enumerate(data['recipes'][:2], 1):
                    print(f"  {i}. {recipe.get('title', '제목 없음')}")
            else:
                print(f"📄 응답: {data}")
            return True
        except Exception as e:
            print(f"❌ 레시피 추천 실패: {e}")
            return False

async def test_restaurant_search():
    """음식점 검색 API 테스트"""
    print("\n🏪 음식점 검색 API 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "lat": 37.5665,
                "lng": 126.9780,
                "text": "한식"
            }
            response = await client.get(f"{BASE_URL}/api/v1/recommendations/recommend_result/", params=params)
            print(f"✅ 음식점 검색 성공: {response.status_code}")
            
            data = response.json()
            print(f"📄 응답: {data}")
            return True
        except Exception as e:
            print(f"❌ 음식점 검색 실패: {e}")
            return False

async def test_translation():
    """번역 기능 테스트 (직접 번역 서비스 테스트)"""
    print("\n🌐 번역 기능 테스트...")
    try:
        from app.utils.translator import translator
        
        # 한글 -> 영어 번역 테스트
        korean_text = "김치찌개는 한국의 대표적인 음식입니다."
        english_result = await translator.translate_to_english(korean_text)
        print(f"✅ 한글 -> 영어 번역: {english_result}")
        
        # 영어 -> 한글 번역 테스트
        english_text = "Kimchi stew is a representative Korean dish."
        korean_result = await translator.translate_to_korean(english_text)
        print(f"✅ 영어 -> 한글 번역: {korean_result}")
        
        return True
    except Exception as e:
        print(f"❌ 번역 기능 테스트 실패: {e}")
        return False

async def test_ingredients_search():
    """재료 검색 API 테스트"""
    print("\n🥕 재료 검색 API 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            params = {"query": "돼지고기", "limit": 5}
            response = await client.get(f"{BASE_URL}/api/v1/ingredients/search", params=params)
            print(f"✅ 재료 검색 성공: {response.status_code}")
            
            data = response.json()
            if "ingredients" in data:
                print(f"📄 검색된 재료 수: {len(data['ingredients'])}")
                for i, ingredient in enumerate(data['ingredients'][:3], 1):
                    print(f"  {i}. {ingredient.get('name', '이름 없음')}")
            else:
                print(f"📄 응답: {data}")
            return True
        except Exception as e:
            print(f"❌ 재료 검색 실패: {e}")
            return False

async def test_recommendations_health():
    """추천 서비스 헬스체크 테스트"""
    print("\n🏥 추천 서비스 헬스체크 테스트...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/v1/recommendations/health")
            print(f"✅ 추천 서비스 헬스체크 성공: {response.status_code}")
            print(f"📄 응답: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ 추천 서비스 헬스체크 실패: {e}")
            return False

async def main():
    """모든 API 테스트 실행"""
    print("🚀 GomGom AI API 테스트 시작")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_recommendations_health,
        test_recipe_search,
        test_recipe_recommendations,
        test_restaurant_search,
        test_translation,
        test_ingredients_search
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    test_names = [
        "헬스체크",
        "추천 서비스 헬스체크",
        "레시피 검색",
        "레시피 추천",
        "음식점 검색",
        "번역 기능",
        "재료 검색"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{i}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    print(f"\n🎯 전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main()) 