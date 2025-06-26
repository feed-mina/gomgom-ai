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
        # HTTP 클라이언트 설정 (연결 풀링 및 타임아웃)
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def search_recipes(self, query: str, number: int = 10) -> List[Dict[str, Any]]:
        """레시피 검색 (재시도 로직 포함)"""
        logger.info(f"레시피 검색 시작: query={query}, number={number}")
        
        # API 키 검증
        if not self.api_key:
            logger.warning("Spoonacular API 키가 설정되지 않았습니다.")
            return []
        
        # 한글 쿼리를 영어로 번역 (실패해도 계속 진행)
        english_query = await translator.translate_to_english(query)
        # 번역이 실패하면 원본 쿼리 사용 (translator가 이미 원본을 반환하므로 추가 처리 불필요)
        
        url = f"{self.base_url}/complexSearch"
        params = {
            "apiKey": self.api_key,
            "query": english_query,
            "number": number,
            "addRecipeInformation": True,
            "fillIngredients": True,
            "instructionsRequired": True
        }
        
        # 재시도 로직
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Spoonacular API 호출 (시도 {attempt + 1}/{self.max_retries}): {url}")
                start_time = time.time()
                
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    limits=self.limits,
                    http2=True
                ) as client:
                    response = await client.get(url, params=params)
                    duration = time.time() - start_time
                    
                    log_api_request("GET", url, response.status_code, duration)
                    
                    if response.status_code == 200:
                        data = response.json()
                        recipes = data.get("results", [])
                        logger.info(f"Spoonacular API에서 {len(recipes)}개의 레시피를 가져왔습니다.")
                        
                        # 번역이 실패해도 원본 데이터 반환
                        try:
                            translated_recipes = await self._translate_recipes_parallel(recipes)
                            return translated_recipes
                        except Exception as e:
                            logger.warning(f"번역 중 오류 발생, 원본 데이터 반환: {e}")
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