#!/usr/bin/env python3
"""
Redis와 PostgreSQL 동기화 기능 테스트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 디렉토리 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.cache import (
    set_cache_with_db, 
    get_cache_with_db_fallback,
    save_recommendation_with_cache,
    save_recipe_with_cache
)
import json
import time

def test_basic_cache_sync():
    """기본 캐시 동기화 테스트"""
    print("🧪 기본 캐시 동기화 테스트")
    print("-" * 40)
    
    # 테스트 데이터
    test_key = "test:basic:sync"
    test_data = {
        "message": "Hello Redis + PostgreSQL!",
        "timestamp": time.time(),
        "numbers": [1, 2, 3, 4, 5]
    }
    
    # 1. Redis + PostgreSQL에 동시 저장
    print("1. Redis + PostgreSQL에 동시 저장...")
    success = set_cache_with_db(test_key, test_data, timeout=300, data_type="test_data")
    
    if success:
        print("✅ 저장 성공")
    else:
        print("❌ 저장 실패")
        return False
    
    # 2. Redis에서 조회
    print("2. Redis에서 조회...")
    redis_data = get_cache_with_db_fallback(test_key)
    
    if redis_data:
        print("✅ Redis 조회 성공")
        # Print(f"   데이터: {json.dumps(redis_data, indent=2, ensure_ascii=False)}")
    else:
        print("❌ Redis 조회 실패")
        return False
    
    # 3. Redis 키 삭제 후 PostgreSQL에서 복구 테스트
    print("3. Redis 키 삭제 후 PostgreSQL 복구 테스트...")
    from app.core.cache import delete_cache
    delete_cache(test_key)
    
    # PostgreSQL에서 복구
    recovered_data = get_cache_with_db_fallback(test_key)
    
    if recovered_data:
        print("✅ PostgreSQL 복구 성공")
        # Print(f"   복구된 데이터: {json.dumps(recovered_data, indent=2, ensure_ascii=False)}")
    else:
        print("❌ PostgreSQL 복구 실패")
        return False
    
    return True

def test_recommendation_sync():
    """추천 결과 동기화 테스트"""
    print("\n🧪 추천 결과 동기화 테스트")
    print("-" * 40)
    
    # 테스트 데이터
    user_id = 999  # 테스트용 사용자 ID
    recipe_id = 888  # 테스트용 레시피 ID
    score = 0.95
    recommendation_data = {
        "store": "테스트 레스토랑",
        "description": "맛있는 테스트 음식",
        "category": "한식",
        "keywords": ["테스트", "맛있는", "추천"],
        "logo_url": "https://example.com/logo.png"
    }
    
    # 추천 결과 저장
    print("추천 결과를 Redis + PostgreSQL에 저장...")
    success = save_recommendation_with_cache(
        user_id=user_id,
        recipe_id=recipe_id,
        score=score,
        recommendation_data=recommendation_data
    )
    
    if success:
        print("✅ 추천 결과 저장 성공")
    else:
        print("❌ 추천 결과 저장 실패")
        return False
    
    return True

def test_recipe_sync():
    """레시피 동기화 테스트"""
    print("\n🧪 레시피 동기화 테스트")
    print("-" * 40)
    
    # 테스트 레시피 데이터
    recipe_data = {
        "name": "테스트 레시피",
        "description": "테스트용 레시피 설명",
        "instructions": "1. 테스트 단계 1\n2. 테스트 단계 2\n3. 완성!",
        "cooking_time": 30,
        "difficulty": "easy"
    }
    
    # 레시피 저장
    print("레시피를 Redis + PostgreSQL에 저장...")
    recipe_id = save_recipe_with_cache(recipe_data)
    
    if recipe_id:
        # Print(f"✅ 레시피 저장 성공 (ID: {recipe_id})")
    else:
        print("❌ 레시피 저장 실패")
        return False
    
    return True

def test_performance():
    """성능 테스트"""
    print("\n🧪 성능 테스트")
    print("-" * 40)
    
    # 100개의 테스트 데이터 생성
    test_data_list = []
    for i in range(100):
        test_data_list.append({
            "key": f"perf_test:{i}",
            "data": {
                "id": i,
                "message": f"Performance test data {i}",
                "timestamp": time.time(),
                "random_value": i * 1.5
            }
        })
    
    # Redis + PostgreSQL 동시 저장 성능 측정
    print("100개 데이터 Redis + PostgreSQL 동시 저장...")
    start_time = time.time()
    
    success_count = 0
    for test_item in test_data_list:
        success = set_cache_with_db(
            test_item["key"], 
            test_item["data"], 
            timeout=600, 
            data_type="performance_test"
        )
        if success:
            success_count += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print(f"✅ 성능 테스트 완료")
    # Print(f"   성공: {success_count}/100")
    # Print(f"   소요시간: {duration:.2f}초")
    # Print(f"   평균: {duration/100:.4f}초/개")
    
    return success_count == 100

def cleanup_test_data():
    """테스트 데이터 정리"""
    print("\n🧹 테스트 데이터 정리")
    print("-" * 40)
    
    from app.core.cache import get_cache_instance
    cache_instance = get_cache_instance()
    
    # 테스트 패턴으로 생성된 키들 삭제
    test_patterns = ["test:*", "perf_test:*"]
    
    for pattern in test_patterns:
        try:
            success = cache_instance.clear_sync(pattern)
            if success:
                # Print(f"✅ {pattern} 패턴 데이터 정리 완료")
            else:
                # Print(f"⚠️ {pattern} 패턴 데이터 정리 실패")
        except Exception as e:
            # Print(f"❌ {pattern} 패턴 데이터 정리 중 오류: {e}")

def main():
    """메인 테스트 함수"""
    print("🚀 Redis + PostgreSQL 동기화 기능 테스트 시작")
    print("=" * 60)
    
    test_results = []
    
    # 1. 기본 캐시 동기화 테스트
    test_results.append(("기본 캐시 동기화", test_basic_cache_sync()))
    
    # 2. 추천 결과 동기화 테스트
    test_results.append(("추천 결과 동기화", test_recommendation_sync()))
    
    # 3. 레시피 동기화 테스트
    test_results.append(("레시피 동기화", test_recipe_sync()))
    
    # 4. 성능 테스트
    test_results.append(("성능 테스트", test_performance()))
    
    # 5. 테스트 데이터 정리
    cleanup_test_data()
    
    # 결과 요약
    print("\n📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 통과" if result else "❌ 실패"
        # Print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    # Print(f"\n전체: {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 성공했습니다!")
        print("\n💡 Redis + PostgreSQL 동기화 기능이 정상적으로 작동합니다.")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 