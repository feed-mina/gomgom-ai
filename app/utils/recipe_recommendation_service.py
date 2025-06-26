import asyncio
from typing import List, Dict, Any, Optional
from app.utils.external_apis import spoonacular_client
from app.utils.price_service import price_service
from app.schemas.recommendation import (
    RecipeRecommendation, RecipeIngredient, RecipeInstruction, 
    RecipeNutrition, RecipeSearchResponse
)
import logging

logger = logging.getLogger(__name__)

class RecipeRecommendationService:
    """레시피 추천 서비스 - 외부 API 통합"""
    
    def __init__(self):
        self.spoonacular_client = spoonacular_client
        self.price_service = price_service
    
    async def search_recipes(self, query: str, number: int = 10, include_price: bool = True) -> RecipeSearchResponse:
        """레시피 검색 및 추천"""
        try:
            # Spoonacular API에서 검색
            recipes = await self.spoonacular_client.search_recipes(query, number)
            
            # 결과 변환
            all_recipes = []
            for recipe in recipes:
                converted_recipe = await self._convert_spoonacular_recipe(recipe, include_price)
                if converted_recipe:
                    all_recipes.append(converted_recipe)
            
            # 결과 수 제한
            limited_recipes = all_recipes[:number]
            
            # 총 비용 계산
            total_cost = sum(recipe.total_cost or 0 for recipe in limited_recipes)
            
            return RecipeSearchResponse(
                query=query,
                total_results=len(limited_recipes),
                recipes=limited_recipes,
                estimated_total_cost=total_cost if include_price else None
            )
            
        except Exception as e:
            logger.error(f"레시피 검색 중 오류: {e}")
            return RecipeSearchResponse(
                query=query,
                total_results=0,
                recipes=[]
            )

# 전역 추천 서비스 인스턴스
recipe_recommendation_service = RecipeRecommendationService() 