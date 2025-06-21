from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class LocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Location name")
    address: Optional[str] = Field(None, max_length=500, description="Location address")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    description: Optional[str] = Field(None, max_length=1000, description="Location description")

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = Field(None, max_length=20)
    website: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)

class LocationResponse(LocationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LocationListResponse(BaseModel):
    locations: List[LocationResponse]
    total: int
    page: int
    size: int

class LocationSearchRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="User's latitude")
    longitude: float = Field(..., ge=-180, le=180, description="User's longitude")
    radius: float = Field(10.0, ge=0.1, le=100, description="Search radius in kilometers")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results") 