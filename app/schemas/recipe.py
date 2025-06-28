from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RecipeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    description: Optional[str] = Field(None, max_length=1000, description="Recipe description")
    difficulty: str = Field(..., description="난이도 (ex: 쉬움, 보통, 어려움)")
    cooking_time: int = Field(..., ge=1, description="Cooking time in minutes")
    servings: int = Field(..., ge=1, description="Number of servings")
    instructions: str = Field(..., min_length=1, description="Cooking instructions")
    image_url: Optional[str] = Field(None, description="Recipe image URL")

class RecipeCreate(RecipeBase):
    pass

class RecipeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    difficulty: Optional[str] = Field(None, description="난이도 (ex: 쉬움, 보통, 어려움)")
    cooking_time: Optional[int] = Field(None, ge=1)
    servings: Optional[int] = Field(None, ge=1)
    instructions: Optional[str] = Field(None, min_length=1)
    image_url: Optional[str] = None

class RecipeResponse(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RecipeListResponse(BaseModel):
    recipes: List[RecipeResponse]
    total: int
    page: int
    size: int

# 레시피 검색 관련 스키마
class RecipeIngredient(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    price: Optional[float] = None

class RecipeInstruction(BaseModel):
    step: str
    number: Optional[int] = None

class RecipeNutrition(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrates: Optional[float] = None
    fiber: Optional[float] = None

class RecipeRecommendation(BaseModel):
    id: Optional[int] = None
    title: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: List[RecipeIngredient] = []
    instructions: List[RecipeInstruction] = []
    nutrition: Optional[RecipeNutrition] = None
    cooking_time: Optional[int] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    source: str
    total_cost: Optional[float] = None
    currency: str = "KRW"

class RecipeSearchRequest(BaseModel):
    query: str = Field(..., description="검색할 레시피 이름")
    number: int = Field(3, ge=1, le=50, description="반환할 레시피 개수")
    include_price: bool = Field(False, description="가격 정보 포함 여부")
    max_cooking_time: Optional[int] = Field(None, ge=1, description="최대 조리 시간 (분)")
    cuisine_type: Optional[str] = Field(None, description="요리 타입")

class RecipeSearchResponse(BaseModel):
    query: str
    total_results: int
    recipes: List[RecipeRecommendation]
    estimated_total_cost: Optional[float] = None
    currency: str = "KRW" 