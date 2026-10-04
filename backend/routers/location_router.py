from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    LocationCreate,
    LocationResponse,
    PeopleDensityResponse
)
import crud
import service


router = APIRouter()


@router.post(
    "/locations",
    response_model=LocationResponse
)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db)
):
    return service.save_location(
        db,
        location
    )

@router.get(
    "/locations",
    response_model=list[LocationResponse]
)
def get_locations(
    db: Session = Depends(get_db)
):
    return crud.get_locations(db)


@router.get(
    "/people-density",
    response_model=PeopleDensityResponse
)
def get_people_density(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_km: float = Query(default=1.0, gt=0),
    db: Session = Depends(get_db)
):
    return service.get_people_density(
        db,
        latitude,
        longitude,
        radius_km
    )

@router.get(
    "/nearby-locations",
    response_model=list[LocationResponse]
)
def get_nearby_locations(
    latitude: float,
    longitude: float,
    radius_km: float = 1,
    device_id: str = "emulator-001",
    db: Session = Depends(get_db)
):
    return service.get_nearby_locations(
        db,
        latitude,
        longitude,
        radius_km,
        device_id
    )

@router.get("/search-places")
def search_places(
    q: str,
    latitude: float | None = None,
    longitude: float | None = None
):
    return service.search_places(
        q,
        latitude,
        longitude
    )