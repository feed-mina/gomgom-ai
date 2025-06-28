import asyncio
import httpx
import json

async def test_translate():
    """번역 API 간단 테스트"""
    url = "http://localhost:8000/api/v1/translate"
    
    # 사용자가 제공한 실제 데이터로 테스트
    test_texts = [
        "avarakkai paruppu curry recipe",
        "Avarakkai paruppu curry might be a good recipe to expand your hor d'oeuvre repertoire. This recipe serves 3. One portion of this dish contains roughly <b>6g of protein</b>, <b>12g of fat</b>, and a total of <b>215 calories</b>. For <b>$1.42 per serving</b>, this recipe <b>covers 10%</b> of your daily requirements of vitamins and minerals. If you have turmeric powder tsp, salt, mustard, and a few other ingredients on hand, you can make it. This recipe is typical of Indian cuisine. From preparation to the plate, this recipe takes around <b>30 minutes</b>. It is a good option if you're following a <b>gluten free, dairy free, lacto ovo vegetarian, and vegan</b> diet. It is brought to you by spoonacular user <a href=\"/profile/ranjaniskitchen\">ranjaniskitchen</a>. Similar recipes are <a href=\"https://spoonacular.com/recipes/avarakkai-paruppu-curry-recipe-1235287\">avarakkai paruppu curry recipe</a>, <a href=\"https://spoonacular.com/recipes/how-to-make-avarakkai-poriyal-494841\">How to make Avarakkai Poriyal</a>, and <a href=\"https://spoonacular.com/recipes/tempeh-curry-recipe-77722\">Tempeh Curry Recipe</a>.",
        "어려움",
        "avarakkai / broad beans",
        "chillies nos)",
        "coriander seeds",
        "cumin seeds",
        "jaggery",
        "tamarind - lemon size",
        "mustard",
        "oil",
        "oil",
        "pepper corns tsp",
        "salt",
        "tomatoes nos)",
        "toor dal cup",
        "turmeric powder tsp"
    ]
    
    print(f"테스트할 텍스트 개수: {len(test_texts)}")
    print(f"첫 번째 텍스트 길이: {len(test_texts[0])}자")
    print(f"두 번째 텍스트 길이: {len(test_texts[1])}자")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("\n번역 요청 전송 중...")
            response = await client.post(
                url,
                json=test_texts,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"응답 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n번역 성공! 결과 개수: {len(data['translatedTexts'])}")
                
                # 처음 몇 개 결과만 출력
                for i, text in enumerate(data['translatedTexts'][:5]):
                    print(f"\n텍스트 {i+1}:")
                    print(f"  원본: {test_texts[i][:100]}...")
                    print(f"  번역: {text[:100]}...")
                    
                if len(data['translatedTexts']) > 5:
                    print(f"\n... 그리고 {len(data['translatedTexts']) - 5}개 더")
                    
            else:
                print(f"오류 발생: {response.status_code}")
                print(f"응답 내용: {response.text}")
                
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_translate()) 