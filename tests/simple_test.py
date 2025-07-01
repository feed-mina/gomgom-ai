import requests
import json

def test_health():
    """간단한 헬스체크 테스트"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        # Print(f"✅ 헬스체크 성공: {response.status_code}")
        # Print(f"📄 응답: {response.json()}")
        return True
    except Exception as e:
        # Print(f"❌ 헬스체크 실패: {e}")
        return False

def test_recommendations_health():
    """추천 서비스 헬스체크 테스트"""
    try:
        response = requests.get("http://localhost:8000/api/v1/recommendations/health", timeout=5)
        # Print(f"✅ 추천 서비스 헬스체크 성공: {response.status_code}")
        # Print(f"📄 응답: {response.json()}")
        return True
    except Exception as e:
        # Print(f"❌ 추천 서비스 헬스체크 실패: {e}")
        return False

def test_recipe_search():
    """레시피 검색 테스트"""
    try:
        params = {"query": "김치찌개", "number": 3}
        response = requests.get("http://localhost:8000/api/v1/recommendations/search", params=params, timeout=10)
        # Print(f"✅ 레시피 검색 성공: {response.status_code}")
        
        data = response.json()
        if "recipes" in data:
            # Print(f"📄 검색된 레시피 수: {len(data['recipes'])}")
        else:
            # Print(f"📄 응답: {data}")
        return True
    except Exception as e:
        # Print(f"❌ 레시피 검색 실패: {e}")
        return False

def main():
    print("🚀 간단한 API 테스트 시작")
    print("=" * 40)
    
    tests = [
        test_health,
        test_recommendations_health,
        test_recipe_search
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            # Print(f"❌ 테스트 실행 중 오류: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 테스트 결과 요약")
    print("=" * 40)
    
    test_names = ["헬스체크", "추천 서비스 헬스체크", "레시피 검색"]
    
    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ 성공" if result else "❌ 실패"
        # Print(f"{i}. {name}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    # Print(f"\n🎯 전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")

if __name__ == "__main__":
    main() 