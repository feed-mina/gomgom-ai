import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.utils.translator import translator
from app.utils.error_handler import safe_execute_async, log_api_request
from app.utils.korean_recipe_crawler import korean_recipe_crawler
# from app.utils.korean_recipe_crawler2 import korean_recipe_crawler2
import logging
import re
import time
from app.core.cache import get_cache, set_cache

logger = logging.getLogger(__name__)

class SpoonacularClient:
    """Spoonacular API 클라이언트"""
    
    def __init__(self):
        self.api_key = settings.SPOONACULAR_API_KEY
        self.base_url = "https://api.spoonacular.com/recipes"
        # HTTP 클라이언트 설정 (연결 풀링 및 타임아웃) - 속도 최적화
        self.timeout = httpx.Timeout(15.0, connect=5.0)  # 타임아웃 단축
        self.limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.max_retries = 2  # 재시도 횟수 감소
        self.retry_delay = 0.5  # 재시도 지연 시간 단축
        self.enable_translation = False  # 번역 기능 비활성화로 속도 향상
    
    def _is_korean_cuisine(self, cuisine_type: Optional[str]) -> bool:
        """한식 요리인지 확인합니다."""
        if not cuisine_type:
            return False
        
        korean_keywords = ['korean', '한식', 'korea', 'korean cuisine']
        is_korean = cuisine_type.lower() in korean_keywords
        
        if is_korean:
            # logger.info(f"한식 요리로 식별됨: '{cuisine_type}'")
            pass
        else:
            # logger.info(f"한식이 아닌 요리로 식별됨: '{cuisine_type}' - KoreanRecipeCrawler 사용하지 않음")
            pass
        
        return is_korean
    
    async def _try_korean_crawler(self, query: str, number: int) -> List[Dict[str, Any]]:
        """한식 크롤러를 사용하여 레시피를 검색합니다."""
        try:
            # logger.info(f"🍜 한식 전용 크롤러로 검색 시도: '{query}'")
            
            # logger.info("🔄 KoreanRecipeCrawler로 검색 시도...")
            crawled_recipes = await korean_recipe_crawler.search_recipes(query, number)
            if crawled_recipes:
                # logger.info(f"✅ KoreanRecipeCrawler에서 {len(crawled_recipes)}개 레시피 발견")
                return crawled_recipes
            
            # logger.info("❌ 한식 크롤러에서 결과를 찾을 수 없습니다.")
            return []
            
        except Exception as e:
            logger.error(f"❌ 한식 크롤러 검색 중 오류: {e}")
            return []

    async def search_recipes(self, query: str, number: int = 10, cuisine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """레시피를 검색합니다. 한식인 경우에만 KoreanRecipeCrawler를 사용합니다."""
        # logger.info(f"🔍 레시피 검색 시작: query='{query}', number={number}, cuisine_type='{cuisine_type}'")
        
        # 한식 여부 확인
        is_korean = self._is_korean_cuisine(cuisine_type)
        
        # API 키 검증
        if not self.api_key:
            logger.warning("⚠️ Spoonacular API 키가 설정되지 않았습니다.")
            # 한식인 경우에만 크롤러로 대체
            if is_korean:
                # logger.info("🍜 API 키 없음 - 한식 크롤러로 대체")
                return await self._try_korean_crawler(query, number)
            else:
                logger.warning("❌ API 키 없음 - 한식이 아니므로 크롤러 사용하지 않음")
                return []
        
        # 영어로 번역 (한식이 아닌 경우에만)
        english_query = query
        if not is_korean:
            try:
                english_query = await translator.translate_to_english(query)
                # logger.info(f"🌐 쿼리 번역: '{query}' -> '{english_query}'")
            except Exception as e:
                logger.warning(f"⚠️ 쿼리 번역 실패, 원본 사용: {e}")
        
        url = f"{self.base_url}/complexSearch"
        params = {
            "apiKey": self.api_key,
            "query": english_query,
            "number": number,
            "addRecipeInformation": True,
            "fillIngredients": True,
            "instructionsRequired": True
        }
        
        # 한식 필터링 추가
        if is_korean:
            params["cuisine"] = "Korean"
            # logger.info("🇰🇷 한식 필터링 적용됨")
        
        # 재시도 로직
        for attempt in range(self.max_retries):
            try:
                # logger.info(f"🌐 Spoonacular API 호출 (시도 {attempt + 1}/{self.max_retries}): {url}")
                start_time = time.time()
                
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    limits=self.limits,
                    http2=False
                ) as client:
                    response = await client.get(url, params=params)
                    duration = time.time() - start_time
                    
                    log_api_request("GET", url, response.status_code, duration)
                    
                    if response.status_code == 200:
                        data = response.json()
                        recipes = data.get("results", [])
                        total_results = data.get("totalResults", 0)
                        # logger.info(f"✅ Spoonacular API 응답: totalResults={total_results}, results={len(recipes)}개")
                        
                        if len(recipes) == 0:
                            logger.warning(f"⚠️ 검색 결과가 없습니다. 쿼리: '{english_query}'")
                            
                            # 한식인 경우에만 크롤러 사용
                            if is_korean:
                                # logger.info("🍜 한식 결과가 없어 만개의레시피에서 보완 검색을 시도합니다.")
                                return await self._try_korean_crawler(query, number)
                            else:
                                # logger.info("🌐 한식이 아니므로 크롤러 사용하지 않음")
                                pass
                            
                            # 한식이 아닌 경우 원본 쿼리로 재시도
                            if query != english_query:
                                # logger.info(f"🔄 원본 쿼리로 재시도: '{query}'")
                                params["query"] = query
                                response = await client.get(url, params=params)
                                if response.status_code == 200:
                                    data = response.json()
                                    recipes = data.get("results", [])
                                    total_results = data.get("totalResults", 0)
                                    # logger.info(f"✅ 원본 쿼리 재시도 결과: totalResults={total_results}, results={len(recipes)}개")
                        
                        # 번역 기능이 활성화된 경우에만 번역 수행
                        if self.enable_translation:
                            try:
                                translated_recipes = await self._translate_recipes_parallel(recipes)
                                return translated_recipes
                            except Exception as e:
                                logger.warning(f"⚠️ 번역 중 오류 발생, 원본 데이터 반환: {e}")
                                return recipes
                        else:
                            # 번역 없이 원본 데이터 반환 (속도 향상)
                            return recipes
                    
                    elif response.status_code == 429:  # Rate limit
                        logger.warning(f"⚠️ Rate limit 도달 (시도 {attempt + 1}): {response.status_code}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 지수 백오프
                            continue
                        else:
                            logger.error("❌ 최대 재시도 횟수 초과")
                            # 한식인 경우에만 크롤러로 대체
                            if is_korean:
                                # logger.info("🍜 Rate limit 초과 - 한식 크롤러로 대체")
                                return await self._try_korean_crawler(query, number)
                            else:
                                logger.warning("❌ Rate limit 초과 - 한식이 아니므로 크롤러 사용하지 않음")
                                return []
                    
                    else:
                        logger.error(f"❌ Spoonacular API 오류: {response.status_code} - {response.text}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        else:
                            # 한식인 경우에만 크롤러로 대체
                            if is_korean:
                                # logger.info("🍜 API 오류 - 한식 크롤러로 대체")
                                return await self._try_korean_crawler(query, number)
                            else:
                                logger.warning("❌ API 오류 - 한식이 아니므로 크롤러 사용하지 않음")
                                return []
            
            except httpx.TimeoutException as e:
                logger.error(f"⏰ Spoonacular API 호출 타임아웃 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # 한식인 경우에만 크롤러로 대체
                    if is_korean:
                        # logger.info("🍜 타임아웃 - 한식 크롤러로 대체")
                        return await self._try_korean_crawler(query, number)
                    else:
                        logger.warning("❌ 타임아웃 - 한식이 아니므로 크롤러 사용하지 않음")
                        return []
            
            except httpx.ConnectError as e:
                logger.error(f"🔌 Spoonacular API 연결 오류 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # 한식인 경우에만 크롤러로 대체
                    if is_korean:
                        # logger.info("🍜 연결 오류 - 한식 크롤러로 대체")
                        return await self._try_korean_crawler(query, number)
                    else:
                        logger.warning("❌ 연결 오류 - 한식이 아니므로 크롤러 사용하지 않음")
                        return []
            
            except Exception as e:
                logger.error(f"💥 Spoonacular API 호출 중 예상치 못한 오류 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # 한식인 경우에만 크롤러로 대체
                    if is_korean:
                        # logger.info("🍜 예상치 못한 오류 - 한식 크롤러로 대체")
                        return await self._try_korean_crawler(query, number)
                    else:
                        logger.warning("❌ 예상치 못한 오류 - 한식이 아니므로 크롤러 사용하지 않음")
                        return []
        
        return []
    
    async def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """레시피 ID로 상세 정보를 가져옵니다."""
        # logger.info(f"레시피 상세 정보 조회 시작: ID={recipe_id}")
        
        # 캐시 확인 (동기)
        cache_key = f"recipe_detail:{recipe_id}"
        cached = get_cache(cache_key)
        if cached:
            # logger.info(f"캐시에서 레시피 상세 정보 반환: ID {recipe_id}")
            return cached
        
        # API 키 검증
        if not self.api_key:
            logger.warning("Spoonacular API 키가 설정되지 않았습니다.")
            return None
        
        url = f"{self.base_url}/{recipe_id}/information"
        params = {
            "apiKey": self.api_key
        }
        
        # 재시도 로직
        for attempt in range(self.max_retries):
            try:
                # logger.info(f"Spoonacular API 호출 (시도 {attempt + 1}/{self.max_retries}): {url}")
                start_time = time.time()
                
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    limits=self.limits,
                    http2=False
                ) as client:
                    response = await client.get(url, params=params)
                    duration = time.time() - start_time
                    
                    log_api_request("GET", url, response.status_code, duration)
                    
                    if response.status_code == 200:
                        recipe_data = response.json()
                        # logger.info(f"레시피 상세 정보 조회 성공: ID {recipe_id}")
                        
                        # 번역 기능이 활성화된 경우에만 번역 수행
                        if self.enable_translation:
                            try:
                                translated_recipe = await self._translate_recipe(recipe_data)
                                set_cache(cache_key, translated_recipe, timeout=7200)
                                return translated_recipe
                            except Exception as e:
                                logger.warning(f"번역 중 오류 발생, 원본 데이터 반환: {e}")
                                set_cache(cache_key, recipe_data, timeout=7200)
                                return recipe_data
                        else:
                            # 번역 없이 원본 데이터 반환 (속도 향상)
                            set_cache(cache_key, recipe_data, timeout=7200)
                            return recipe_data
                    
                    elif response.status_code == 404:
                        logger.warning(f"레시피를 찾을 수 없습니다: ID {recipe_id}")
                        return None
                    
                    elif response.status_code == 429:  # Rate limit
                        logger.warning(f"Rate limit 도달 (시도 {attempt + 1}): {response.status_code}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))
                            continue
                        else:
                            logger.error("최대 재시도 횟수 초과")
                            return None
                    
                    else:
                        logger.error(f"Spoonacular API 오류: {response.status_code} - {response.text}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        else:
                            return None
            
            except httpx.TimeoutException as e:
                logger.error(f"Spoonacular API 호출 타임아웃 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return None
            
            except httpx.ConnectError as e:
                logger.error(f"Spoonacular API 연결 오류 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return None
            
            except Exception as e:
                logger.error(f"Spoonacular API 호출 중 예상치 못한 오류 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return None
        
        return None
    
    async def _translate_recipes_parallel(self, recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """레시피들을 병렬로 번역 (오류 처리 개선)"""
        if not recipes:
            return []
        
        # 최대 5개씩 병렬 처리 (API 제한 고려)
        semaphore = asyncio.Semaphore(5)
        
        async def translate_single_recipe(recipe: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    return await self._translate_recipe(recipe)
                except Exception as e:
                    logger.warning(f"레시피 번역 실패: {e}")
                    return recipe  # 원본 반환
        
        # 병렬로 번역 실행
        tasks = [translate_single_recipe(recipe) for recipe in recipes]
        translated_recipes = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 에러가 발생한 경우 원본 레시피 반환
        result = []
        for i, translated_recipe in enumerate(translated_recipes):
            if isinstance(translated_recipe, Exception):
                logger.warning(f"레시피 번역 실패 (인덱스 {i}): {translated_recipe}")
                result.append(recipes[i])
            else:
                result.append(translated_recipe)
        
        return result
    
    async def _translate_recipe(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """레시피 정보를 한글로 번역 (오류 처리 개선)"""
        translated_recipe = recipe.copy()
        
        # 병렬로 번역 작업 실행
        translation_tasks = []
        
        # 제목 번역
        if "title" in recipe:
            translation_tasks.append(self._translate_title(translated_recipe))
        
        # 요약 번역
        if "summary" in recipe:
            translation_tasks.append(self._translate_summary(translated_recipe))
        
        # 재료 번역
        if "extendedIngredients" in recipe:
            translation_tasks.append(self._translate_ingredients(translated_recipe))
        
        # 지시사항 번역
        if "analyzedInstructions" in recipe and recipe["analyzedInstructions"]:
            translation_tasks.append(self._translate_instructions(translated_recipe))
        
        # 모든 번역 작업 완료 대기 (오류 무시)
        if translation_tasks:
            await asyncio.gather(*translation_tasks, return_exceptions=True)
        
        return translated_recipe
    
    async def _translate_title(self, recipe: Dict[str, Any]) -> None:
        """제목 번역"""
        try:
            translated_title = await translator.translate_to_korean(recipe["title"])
            recipe["title"] = translated_title
        except Exception as e:
            logger.warning(f"제목 번역 실패: {e}")
    
    async def _translate_summary(self, recipe: Dict[str, Any]) -> None:
        """요약 번역"""
        try:
            clean_summary = re.sub(r'<[^>]+>', '', recipe["summary"])
            translated_summary = await translator.translate_to_korean(clean_summary)
            recipe["summary"] = translated_summary
        except Exception as e:
            logger.warning(f"요약 번역 실패: {e}")
    
    async def _translate_ingredients(self, recipe: Dict[str, Any]) -> None:
        """재료 번역"""
        try:
            for ingredient in recipe["extendedIngredients"]:
                if "name" in ingredient:
                    translated_name = await translator.translate_to_korean(ingredient["name"])
                    ingredient["name"] = translated_name
        except Exception as e:
            logger.warning(f"재료 번역 실패: {e}")
    
    async def _translate_instructions(self, recipe: Dict[str, Any]) -> None:
        """지시사항 번역"""
        try:
            for instruction in recipe["analyzedInstructions"][0].get("steps", []):
                if "step" in instruction:
                    translated_step = await translator.translate_to_korean(instruction["step"])
                    instruction["step"] = translated_step
        except Exception as e:
            logger.warning(f"지시사항 번역 실패: {e}")

# 전역 클라이언트 인스턴스
spoonacular_client = SpoonacularClient() 