from pydantic import BaseModel, Field
from typing import Optional, List, Dict
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