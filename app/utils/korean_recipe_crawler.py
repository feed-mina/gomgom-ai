import requests
import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import List, Dict, Any, Optional
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class KoreanRecipeCrawler:
    """만개의레시피 사이트에서 한식 레시피를 크롤링하는 클래스"""
    
    def __init__(self):
        self.base_url = "https://www.10000recipe.com"
        self.search_url = f"{self.base_url}/recipe/list.html"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
        self.max_retries = 2
    
    async def search_recipes(self, query: str, number: int = 5) -> List[Dict[str, Any]]:
        """검색어로 레시피를 검색합니다."""
        logger.info(f"만개의레시피 검색 시작: query={query}, number={number}")
        
        try:
            async with aiohttp.ClientSession(headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                # 검색 결과 페이지 가져오기
                search_url = f"{self.search_url}?q={quote(query)}&order=reco&page=1"
                async with session.get(search_url) as response:
                    if response.status != 200:
                        logger.error(f"검색 페이지 요청 실패: {response.status}")
                        return []
                    
                    html = await response.text()
                
                # 검색 결과 파싱
                soup = BeautifulSoup(html, 'html.parser')
                recipe_links = soup.find_all('a', class_='common_sp_link')
                
                if not recipe_links:
                    logger.warning(f"'{query}'에 대한 검색 결과가 없습니다.")
                    return []
                
                # 상위 N개 레시피 상세 정보 가져오기
                recipes = []
                for i, link in enumerate(recipe_links[:number]):
                    try:
                        recipe_id = link.get('href', '').split('/')[-1]
                        if recipe_id:
                            recipe_detail = await self._get_recipe_detail(session, recipe_id)
                            if recipe_detail:
                                recipes.append(recipe_detail)
                        
                        # 요청 간격 조절
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"레시피 {i+1} 처리 중 오류: {e}")
                        continue
                
                logger.info(f"만개의레시피 검색 완료: {len(recipes)}개 레시피 발견")
                return recipes
                
        except Exception as e:
            logger.error(f"만개의레시피 검색 중 오류: {e}")
            return []
    
    async def _get_recipe_detail(self, session: aiohttp.ClientSession, recipe_id: str) -> Optional[Dict[str, Any]]:
        """레시피 상세 정보를 가져옵니다."""
        try:
            recipe_url = f"{self.base_url}/recipe/{recipe_id}"
            
            async with session.get(recipe_url) as response:
                if response.status != 200:
                    logger.error(f"레시피 상세 페이지 요청 실패: {response.status}")
                    return None
                
                html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # JSON-LD 스크립트 태그에서 레시피 정보 추출
            json_script = soup.find('script', type='application/ld+json')
            if json_script:
                recipe_data = json.loads(json_script.text)
                return self._parse_recipe_json(recipe_data, recipe_id)
            
            # JSON-LD가 없는 경우 HTML에서 직접 파싱
            return self._parse_recipe_html(soup, recipe_id)
            
        except Exception as e:
            logger.error(f"레시피 상세 정보 파싱 중 오류 (ID: {recipe_id}): {e}")
            return None
    
    def _parse_recipe_json(self, recipe_data: Dict[str, Any], recipe_id: str) -> Dict[str, Any]:
        """JSON-LD 데이터를 파싱합니다."""
        try:
            # 재료 정보
            ingredients = []
            for ingredient in recipe_data.get('recipeIngredient', []):
                if isinstance(ingredient, str):
                    ingredients.append({
                        'name': ingredient.strip(),
                        'amount': '',
                        'unit': ''
                    })
            
            # 조리법 정보
            instructions = []
            for i, step in enumerate(recipe_data.get('recipeInstructions', []), 1):
                if isinstance(step, dict) and 'text' in step:
                    instructions.append({
                        'step': step['text'],
                        'number': i
                    })
                elif isinstance(step, str):
                    instructions.append({
                        'step': step,
                        'number': i
                    })
            
            # 이미지 URL
            image_url = ""
            if 'image' in recipe_data:
                if isinstance(recipe_data['image'], list) and recipe_data['image']:
                    image_url = recipe_data['image'][0]
                elif isinstance(recipe_data['image'], str):
                    image_url = recipe_data['image']
            
            return {
                'id': f"10000recipe_{recipe_id}",
                'title': recipe_data.get('name', ''),
                'summary': recipe_data.get('description', ''),
                'image_url': image_url,
                'ingredients': ingredients,
                'instructions': instructions,
                'cooking_time': self._extract_cooking_time(recipe_data),
                'servings': recipe_data.get('recipeYield', 1),
                'source': '10000recipe',
                'source_url': f"https://www.10000recipe.com/recipe/{recipe_id}",
                'cuisines': ['Korean', 'Asian'],
                'readyInMinutes': self._extract_cooking_time(recipe_data),
                'extendedIngredients': [
                    {
                        'name': ing['name'],
                        'amount': ing['amount'],
                        'unit': ing['unit']
                    } for ing in ingredients
                ],
                'analyzedInstructions': [{
                    'steps': [
                        {
                            'step': inst['step'],
                            'number': inst['number']
                        } for inst in instructions
                    ]
                }] if instructions else []
            }
            
        except Exception as e:
            logger.error(f"JSON 파싱 중 오류: {e}")
            return None
    
    def _parse_recipe_html(self, soup: BeautifulSoup, recipe_id: str) -> Optional[Dict[str, Any]]:
        """HTML에서 직접 레시피 정보를 파싱합니다."""
        try:
            # 제목
            title = ""
            title_tag = soup.find('h3', class_='view2_summary')
            if title_tag:
                title = title_tag.get_text(strip=True)
            
            # 재료
            ingredients = []
            ingredient_section = soup.find('div', class_='view2_summary_info')
            if ingredient_section:
                ingredient_items = ingredient_section.find_all('li')
                for item in ingredient_items:
                    ingredient_text = item.get_text(strip=True)
                    if ingredient_text:
                        ingredients.append({
                            'name': ingredient_text,
                            'amount': '',
                            'unit': ''
                        })
            
            # 조리법
            instructions = []
            instruction_section = soup.find('div', class_='view_step')
            if instruction_section:
                step_items = instruction_section.find_all('div', class_='view_step_cont')
                for i, step in enumerate(step_items, 1):
                    step_text = step.get_text(strip=True)
                    if step_text:
                        instructions.append({
                            'step': step_text,
                            'number': i
                        })
            
            # 이미지
            image_url = ""
            img_tag = soup.find('img', class_='centeredcrop')
            if img_tag and img_tag.get('src'):
                image_url = img_tag['src']
                if not image_url.startswith('http'):
                    image_url = f"https:{image_url}"
            
            return {
                'id': f"10000recipe_{recipe_id}",
                'title': title,
                'summary': f"{title} 레시피입니다.",
                'image_url': image_url,
                'ingredients': ingredients,
                'instructions': instructions,
                'cooking_time': 30,  # 기본값
                'servings': 2,  # 기본값
                'source': '10000recipe',
                'source_url': f"https://www.10000recipe.com/recipe/{recipe_id}",
                'cuisines': ['Korean', 'Asian'],
                'readyInMinutes': 30,
                'extendedIngredients': [
                    {
                        'name': ing['name'],
                        'amount': ing['amount'],
                        'unit': ing['unit']
                    } for ing in ingredients
                ],
                'analyzedInstructions': [{
                    'steps': [
                        {
                            'step': inst['step'],
                            'number': inst['number']
                        } for inst in instructions
                    ]
                }] if instructions else []
            }
            
        except Exception as e:
            logger.error(f"HTML 파싱 중 오류: {e}")
            return None
    
    def _extract_cooking_time(self, recipe_data: Dict[str, Any]) -> int:
        """조리 시간을 추출합니다."""
        try:
            # prepTime 또는 cookTime에서 시간 추출
            prep_time = recipe_data.get('prepTime', '')
            cook_time = recipe_data.get('cookTime', '')
            
            total_minutes = 0
            
            # ISO 8601 형식 (PT30M) 파싱
            for time_str in [prep_time, cook_time]:
                if time_str:
                    # PT30M -> 30분
                    match = re.search(r'PT(\d+)M', time_str)
                    if match:
                        total_minutes += int(match.group(1))
            
            return total_minutes if total_minutes > 0 else 30  # 기본값 30분
            
        except Exception as e:
            logger.error(f"조리 시간 추출 중 오류: {e}")
            return 30  # 기본값

# 전역 크롤러 인스턴스
korean_recipe_crawler = KoreanRecipeCrawler()