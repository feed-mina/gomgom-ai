from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RecommendationBase(BaseModel):
    user_id: int = Field(..., description="User ID")
    recipe_id: int = Field(..., description="Recipe ID")
    score: float = Field(..., ge=0, le=5, description="Recommendation score (0-5)")

class RecommendationCreate(RecommendationBase):
    pass

class RecommendationUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=5, description="Recommendation score (0-5)")

class RestaurantResult(BaseModel):
    store: str
    description: str
    category: str
    keywords: List[str]
    logo_url: str

class RestaurantInfo(BaseModel):
    name: str
    review_avg: str
    address: str
    id: str
    categories: str
    logo_url: str

class RecommendationResponse(BaseModel):
    result: RestaurantResult
    restaurants: List[RestaurantInfo]
    text: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    types: Optional[List[str]] = None
    score: Optional[Dict[str, int]] = None

class RecommendationListResponse(BaseModel):
    recommendations: List[RecommendationResponse]
    total: int
    page: int
    size: int

class RecommendationWithRecipe(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    score: float
    recipe_name: str
    recipe_description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RecommendationRequest(BaseModel):
    user_id: int = Field(..., description="User ID")
    limit: int = Field(10, ge=1, le=50, description="Number of recommendations to return")

class IngredientPrice(BaseModel):
    """재료 가격 정보"""
    korean_name: str
    english_name: Optional[str] = None
    average_price: float
    currency: str = "KRW"
    platform_prices: Dict[str, List[float]] = {}

class RecipeIngredient(BaseModel):
    """레시피 재료 정보"""
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None

class RecipeInstruction(BaseModel):
    """레시피 조리 단계"""
    step: str
    number: Optional[int] = None

class RecipeNutrition(BaseModel):
    """영양 정보"""
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    fiber: Optional[float] = None

class RecipeRecommendation(BaseModel):
    """레시피 추천 결과"""
    id: Optional[int] = None
    title: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: List[RecipeIngredient]
    instructions: List[RecipeInstruction]
    nutrition: Optional[RecipeNutrition] = None
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    source: str  # "spoonacular" 또는 "edamam"
    total_cost: Optional[float] = None
    currency: str = "KRW"

class RecipeSearchRequest(BaseModel):
    """레시피 검색 요청"""
    query: str
    number: int = 10
    include_price: bool = True
    max_cooking_time: Optional[int] = None
    cuisine_type: Optional[str] = None

class RecipeSearchResponse(BaseModel):
    """레시피 검색 응답"""
    query: str
    total_results: int
    recipes: List[RecipeRecommendation]
    estimated_total_cost: Optional[float] = None
    currency: str = "KRW" 