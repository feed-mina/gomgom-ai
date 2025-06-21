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