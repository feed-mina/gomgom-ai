import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.utils.translator import translator
from app.utils.error_handler import safe_execute_async, log_api_request
import logging
import re
import time

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
    
    async def search_recipes(self, query: str, number: int = 10, cuisine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """레시피 검색 (재시도 로직 포함)"""
        logger.info(f"레시피 검색 시작: query={query}, number={number}, cuisine_type={cuisine_type}")
        
        # API 키 검증
        if not self.api_key:
            logger.warning("Spoonacular API 키가 설정되지 않았습니다.")
            return []
        
        # 한글 쿼리를 영어로 번역 (실패해도 계속 진행)
        english_query = await translator.translate_to_english(query)
        logger.info(f"번역된 쿼리: '{query}' -> '{english_query}'")
        
        url = f"{self.base_url}/complexSearch"
        params = {
            "apiKey": self.api_key,
            "query": english_query,
            "number": number,
            "addRecipeInformation": True,
            "fillIngredients": True,
            "instructionsRequired": False  # 지시사항 필수 여부 비활성화로 속도 향상
        }
        
        # 한식 필터링 추가
        if cuisine_type and cuisine_type.lower() in ['korean', '한식', 'korea']:
            params["cuisine"] = "korean"
            params["tags"] = "korean"
            logger.info("한식 필터링 적용됨")
        
        logger.info(f"API 요청 파라미터: {params}")
        
        # 재시도 로직
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Spoonacular API 호출 (시도 {attempt + 1}/{self.max_retries}): {url}")
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
                        logger.info(f"Spoonacular API 응답: totalResults={total_results}, results={len(recipes)}개")
                        
                        if len(recipes) == 0:
                            logger.warning(f"검색 결과가 없습니다. 쿼리: '{english_query}'")
                            # 원본 쿼리로 다시 시도
                            if query != english_query:
                                logger.info(f"원본 쿼리로 재시도: '{query}'")
                                params["query"] = query
                                response = await client.get(url, params=params)
                                if response.status_code == 200:
                                    data = response.json()
                                    recipes = data.get("results", [])
                                    total_results = data.get("totalResults", 0)
                                    logger.info(f"원본 쿼리 재시도 결과: totalResults={total_results}, results={len(recipes)}개")
                        
                        # 번역 기능이 활성화된 경우에만 번역 수행
                        if self.enable_translation:
                            try:
                                translated_recipes = await self._translate_recipes_parallel(recipes)
                                return translated_recipes
                            except Exception as e:
                                logger.warning(f"번역 중 오류 발생, 원본 데이터 반환: {e}")
                                return recipes
                        else:
                            # 번역 없이 원본 데이터 반환 (속도 향상)
                            return recipes
                    
                    elif response.status_code == 429:  # Rate limit
                        logger.warning(f"Rate limit 도달 (시도 {attempt + 1}): {response.status_code}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 지수 백오프
                            continue
                        else:
                            logger.error("최대 재시도 횟수 초과")
                            return []
                    
                    else:
                        logger.error(f"Spoonacular API 오류: {response.status_code} - {response.text}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay)
                            continue
                        else:
                            return []
            
            except httpx.TimeoutException as e:
                logger.error(f"Spoonacular API 호출 타임아웃 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return []
            
            except httpx.ConnectError as e:
                logger.error(f"Spoonacular API 연결 오류 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return []
            
            except Exception as e:
                logger.error(f"Spoonacular API 호출 중 예상치 못한 오류 (시도 {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    return []
        
        return []
    
    async def get_recipe_by_id(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """레시피 ID로 상세 정보를 가져옵니다."""
        logger.info(f"레시피 상세 정보 조회 시작: ID={recipe_id}")
        
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
                logger.info(f"Spoonacular API 호출 (시도 {attempt + 1}/{self.max_retries}): {url}")
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
                        logger.info(f"레시피 상세 정보 조회 성공: ID {recipe_id}")
                        
                        # 번역 기능이 활성화된 경우에만 번역 수행
                        if self.enable_translation:
                            try:
                                translated_recipe = await self._translate_recipe(recipe_data)
                                return translated_recipe
                            except Exception as e:
                                logger.warning(f"번역 중 오류 발생, 원본 데이터 반환: {e}")
                                return recipe_data
                        else:
                            # 번역 없이 원본 데이터 반환 (속도 향상)
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