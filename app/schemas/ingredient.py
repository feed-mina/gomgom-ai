from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class IngredientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Ingredient name")
    price: float = Field(..., ge=0, description="Ingredient price")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    category: Optional[str] = Field(None, max_length=100, description="Ingredient category")
    image_url: Optional[str] = Field(None, description="Ingredient image URL")

class IngredientCreate(IngredientBase):
    pass

class IngredientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = None

class IngredientResponse(IngredientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class IngredientListResponse(BaseModel):
    ingredients: List[IngredientResponse]
    total: int
    page: int
    size: int

class IngredientKoreanBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Korean ingredient name")
    ingredient_id: int = Field(..., description="Reference to main ingredient")

class IngredientKoreanCreate(IngredientKoreanBase):
    pass

class IngredientKoreanResponse(IngredientKoreanBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 