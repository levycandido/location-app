from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class LocationCreate(BaseModel):
    device_id: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationResponse(BaseModel):
    id: int
    device_id: str
    latitude: float
    longitude: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PeopleDensityResponse(BaseModel):
    latitude: float
    longitude: float
    radius_km: float
    people: int