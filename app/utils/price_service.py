import httpx
import asyncio
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.utils.translator import translator
import logging
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

class PriceService:
    """가격 정보 서비스 - 쿠팡, 마켓컬리 크롤링"""
    
    def __init__(self):
        self.crawling_delay = settings.CRAWLING_DELAY
        self.max_retries = settings.MAX_CRAWLING_RETRIES
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def get_ingredient_prices(self, ingredient_names: List[str]) -> Dict[str, Dict[str, Any]]:
        """재료들의 가격 정보를 수집"""
        prices = {}
        
        for ingredient_name in ingredient_names:
            try:
                # 재료명을 영어로 번역 (검색용)
                english_name = await translator.translate_to_english(ingredient_name)
                # 번역이 실패하면 원본 이름 사용 (translator가 이미 원본을 반환하므로 추가 처리 불필요)
                
                # 여러 플랫폼에서 가격 정보 수집
                price_info = await self._collect_price_info(ingredient_name, english_name)
                if price_info:
                    prices[ingredient_name] = price_info
                
                # 크롤링 간격
                await asyncio.sleep(self.crawling_delay)
                
            except Exception as e:
                logger.error(f"재료 가격 수집 중 오류 ({ingredient_name}): {e}")
                continue
        
        return prices
    
    async def _collect_price_info(self, korean_name: str, english_name: str) -> Optional[Dict[str, Any]]:
        """여러 플랫폼에서 가격 정보 수집"""
        price_info = {
            "korean_name": korean_name,
            "english_name": english_name,
            "prices": {},
            "average_price": 0,
            "currency": "KRW"
        }
        
        # 쿠팡 검색
        coupang_prices = await self._search_coupang(korean_name)
        if coupang_prices:
            price_info["prices"]["coupang"] = coupang_prices
        
        # 마켓컬리 검색
        marketkurly_prices = await self._search_marketkurly(korean_name)
        if marketkurly_prices:
            price_info["prices"]["marketkurly"] = marketkurly_prices
        
        # 평균 가격 계산
        all_prices = []
        for platform_prices in price_info["prices"].values():
            all_prices.extend(platform_prices)
        
        if all_prices:
            price_info["average_price"] = sum(all_prices) / len(all_prices)
        
        return price_info if all_prices else None
    
    async def _search_coupang(self, query: str) -> List[float]:
        """쿠팡에서 상품 검색 및 가격 추출"""
        prices = []
        
        try:
            # 쿠팡 검색 URL (실제 구현시에는 쿠팡 파트너스 API 사용 권장)
            search_url = f"https://www.coupang.com/np/search?component=&q={query}&channel=user"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 가격 정보 추출 (실제 쿠팡 HTML 구조에 맞게 수정 필요)
                    price_elements = soup.find_all('span', class_='price')
                    
                    for element in price_elements[:5]:  # 상위 5개 상품만
                        price_text = element.get_text().strip()
                        price = self._extract_price(price_text)
                        if price:
                            prices.append(price)
                
        except Exception as e:
            logger.error(f"쿠팡 검색 중 오류: {e}")
        
        return prices
    
    async def _search_marketkurly(self, query: str) -> List[float]:
        """마켓컬리에서 상품 검색 및 가격 추출"""
        prices = []
        
        try:
            # 마켓컬리 검색 URL
            search_url = f"https://www.kurly.com/search?sword={query}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(search_url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # 가격 정보 추출 (실제 마켓컬리 HTML 구조에 맞게 수정 필요)
                    price_elements = soup.find_all('span', class_='price')
                    
                    for element in price_elements[:5]:  # 상위 5개 상품만
                        price_text = element.get_text().strip()
                        price = self._extract_price(price_text)
                        if price:
                            prices.append(price)
                
        except Exception as e:
            logger.error(f"마켓컬리 검색 중 오류: {e}")
        
        return prices
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """텍스트에서 가격 추출"""
        try:
            # 숫자와 쉼표만 추출
            price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
            if price_match:
                price = float(price_match.group().replace(',', ''))
                return price
        except (ValueError, AttributeError):
            pass
        return None
    
    async def estimate_recipe_cost(self, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """레시피의 총 비용 추정"""
        ingredient_names = []
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                name = ingredient.get('name') or ingredient.get('ingredient')
                if name:
                    ingredient_names.append(name)
            elif isinstance(ingredient, str):
                ingredient_names.append(ingredient)
        
        # 가격 정보 수집
        price_info = await self.get_ingredient_prices(ingredient_names)
        
        # 총 비용 계산
        total_cost = 0
        ingredient_costs = {}
        
        for ingredient_name, info in price_info.items():
            if info.get('average_price'):
                ingredient_costs[ingredient_name] = info['average_price']
                total_cost += info['average_price']
        
        return {
            "total_cost": total_cost,
            "currency": "KRW",
            "ingredient_costs": ingredient_costs,
            "price_details": price_info
        }

# 전역 가격 서비스 인스턴스
price_service = PriceService() 