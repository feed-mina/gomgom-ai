from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Location
from app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
# from app.core.cache import get_cache, set_cache, delete_cache

router = APIRouter()

@router.get("/", response_model=List[LocationResponse])
def read_locations(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """
    위치 정보 목록을 조회합니다.
    """
    # cache_key = f"locations:list:{skip}:{limit}:{search}"
    # cached_result = get_cache(cache_key)
    # if cached_result:
    #     return cached_result

    query = db.query(Location)
    if search:
        query = query.filter(Location.name.ilike(f"%{search}%"))
    
    locations = query.offset(skip).limit(limit).all()
    # set_cache(cache_key, locations)
    return locations

@router.get("/{location_id}", response_model=LocationResponse)
def read_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """
    특정 위치 정보를 조회합니다.
    """
    # cache_key = f"location:{location_id}"
    # cached_result = get_cache(cache_key)
    # if cached_result:
    #     return cached_result

    location = db.query(Location).filter(Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    # set_cache(cache_key, location)
    return location

@router.post("/", response_model=LocationResponse)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 위치 정보를 생성합니다.
    """
    db_location = Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    # delete_cache("locations:list:*")
    return db_location

@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db)
):
    """
    위치 정보를 수정합니다.
    """
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    for field, value in location.dict(exclude_unset=True).items():
        setattr(db_location, field, value)
    
    db.commit()
    db.refresh(db_location)
    # delete_cache(f"location:{location_id}")
    # delete_cache("locations:list:*")
    return db_location

@router.delete("/{location_id}")
def delete_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """
    위치 정보를 삭제합니다.
    """
    db_location = db.query(Location).filter(Location.id == location_id).first()
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    db.delete(db_location)
    db.commit()
    # delete_cache(f"location:{location_id}")
    # delete_cache("locations:list:*")
    return {"message": "Location deleted successfully"} 