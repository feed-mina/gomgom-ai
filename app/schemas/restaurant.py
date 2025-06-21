from typing import List, Optional
from pydantic import BaseModel

class DeliveryFeeDisplay(BaseModel):
    basic: str

class Restaurant(BaseModel):
    id: int
    name: str
    logo_url: str
    categories: List[str]
    review_avg: float
    review_count: int
    delivery_fee_to_display: DeliveryFeeDisplay
    address: str
    keywords: Optional[List[str]] = None

class RestaurantListResponse(BaseModel):
    restaurants: List[Restaurant]
    address: Optional[str] = None 