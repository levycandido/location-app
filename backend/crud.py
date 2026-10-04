from sqlalchemy.orm import Session

import models
from schemas import LocationCreate


def create_location(db: Session, location: LocationCreate):
    new_location = models.Location(
        device_id=location.device_id,
        latitude=location.latitude,
        longitude=location.longitude
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location

def get_locations(db: Session):
    return db.query(models.Location).all()

from datetime import datetime

def get_locations_since(
    db: Session,
    since: datetime
):
    return (
        db.query(models.Location)
        .filter(models.Location.created_at >= since)
        .order_by(models.Location.created_at.desc())
        .all()
    )

def get_latest_location_by_device(
    db: Session,
    device_id: str
):
    return (
        db.query(models.Location)
        .filter(models.Location.device_id == device_id)
        .order_by(models.Location.created_at.desc())
        .first()
    )