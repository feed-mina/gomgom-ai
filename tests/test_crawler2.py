import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.utils.korean_recipe_crawler import korean_recipe_crawler
from app.utils.external_apis import spoonacular_client

async def test_korean_crawler():
    print("🍜 만개의레시피 크롤링 테스트 시작")
    print("=" * 50)
    test_queries = [
        "비빔밥",
        "된장찌개",
        "짬뽕",
        "짜장면",
        "김치찌개",
        "불고기"
    ]
    for query in test_queries:
        print(f"\n🍜 크롤링 테스트: '{query}'")
        print("-" * 40)
        try:
            recipes = await korean_recipe_crawler.search_recipes(query, 3)
            print(f"✅ 크롤링 결과: {len(recipes)}개 레시피 발견")
            for i, recipe in enumerate(recipes[:2], 1):
                title = recipe.get('title', '제목 없음')
                source = recipe.get('source', '')
                source_url = recipe.get('source_url', '')
                ingredients_count = len(recipe.get('ingredients', []))
                instructions_count = len(recipe.get('instructions', []))
                print(f"  {i}. {title}")
                print(f"     출처: {source}")
                print(f"     URL: {source_url}")
                print(f"     재료: {ingredients_count}개, 조리법: {instructions_count}단계")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    print("\n" + "=" * 50)
    print("🎉 크롤링 테스트 완료!")

async def test_integrated_search():
    print("\n🌐 통합 검색 테스트 (Spoonacular + 크롤링)")
    print("=" * 50)
    test_queries = [
        ("김치", "korean"),
        ("비빔밥", "korean"),
        ("치킨", None),
    ]
    for query, cuisine_type in test_queries:
        cuisine_display = cuisine_type if cuisine_type else "모든 요리"
        print(f"\n🌐 통합 검색 테스트: '{query}' (cuisine_type: {cuisine_display})")
        print("-" * 40)
        try:
            recipes = await spoonacular_client.search_recipes(
                query=query,
                number=3,
                cuisine_type=cuisine_type
            )
            print(f"✅ 통합 검색 결과: {len(recipes)}개 레시피 발견")
            for i, recipe in enumerate(recipes[:2], 1):
                title = recipe.get('title', '제목 없음')
                source = recipe.get('source', 'Spoonacular')
                cuisines = recipe.get('cuisines', [])
                print(f"  {i}. {title}")
                print(f"     출처: {source}")
                print(f"     요리 타입: {cuisines}")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
    print("\n" + "=" * 50)
    print("🎉 통합 검색 테스트 완료!")

if __name__ == "__main__":
    print("🚀 만개의레시피 크롤링 테스트 시작")
    asyncio.run(test_korean_crawler())
    asyncio.run(test_integrated_search())
    print("\n✨ 모든 테스트 완료!")