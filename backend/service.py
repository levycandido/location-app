import threading

from math import radians, sin, cos, sqrt, atan2

from sqlalchemy.orm import Session
import crud
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def calculate_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


def get_people_density(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float
):
    five_minutes_ago = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )

    locations = crud.get_locations_since(
        db,
        five_minutes_ago
    )

    latest_locations = {}

    for location in locations:
        if location.device_id not in latest_locations:
            latest_locations[location.device_id] = location

    devices = set()

    for location in latest_locations.values():
        distance = calculate_distance(
            latitude,
            longitude,
            location.latitude,
            location.longitude
        )

        if distance <= radius_km:
            devices.add(location.device_id)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "radius_km": radius_km,
        "people": len(devices)
    }

def save_location(
    db: Session,
    location
):
    latest_location = crud.get_latest_location_by_device(
        db,
        location.device_id
    )

    # Primeira localização desse aparelho
    if latest_location is None:
        return crud.create_location(db, location)

    distance = calculate_distance(
        latest_location.latitude,
        latest_location.longitude,
        location.latitude,
        location.longitude
    )

    now = datetime.now(timezone.utc)

    seconds_since_last_location = (
        now - latest_location.created_at
    ).total_seconds()

    # Salva se moveu pelo menos 20 metros
    # ou se passou pelo menos 60 segundos
    if distance >= 0.02 or seconds_since_last_location >= 60:
        return crud.create_location(db, location)

    # Caso contrário, não grava novamente
    return latest_location

from datetime import datetime, timedelta, timezone


def get_nearby_locations(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float,
    current_device_id: str
):
    five_minutes_ago = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )

    locations = crud.get_locations_since(
        db,
        five_minutes_ago
    )

    nearby = []

    # Evita mostrar várias posições antigas
    # do mesmo dispositivo
    devices_found = set()

    # mais recentes primeiro
    locations = sorted(
        locations,
        key=lambda location: location.created_at,
        reverse=True
    )

    for location in locations:

        # Não mostra o próprio usuário
        if location.device_id == current_device_id:
            continue

        # Só usa uma posição por dispositivo
        if location.device_id in devices_found:
            continue

        distance = calculate_distance(
            latitude,
            longitude,
            location.latitude,
            location.longitude
        )

        if distance <= radius_km:
            nearby.append(location)
            devices_found.add(location.device_id)

    return nearby

_nominatim_lock = threading.Lock()
_last_nominatim_request = 0.0

def search_places(
    query: str,
    latitude: float | None = None,
    longitude: float | None = None
):
    params = {
        "q": query,
        "limit": 6
    }

    if latitude is not None and longitude is not None:
        params["lat"] = latitude
        params["lon"] = longitude

    url = (
        "https://photon.komoot.io/api?"
        + urlencode(params)
    )

    print("URL PHOTON:", url)

    request = Request(
        url,
        headers={
            "User-Agent": "IdentificadorPessoas/1.0",
            "Accept": "application/json"
        }
    )

    try:
        with urlopen(request, timeout=15) as response:
            raw = response.read().decode("utf-8")
            print("RESPOSTA PHOTON:", raw[:500])

            data = json.loads(raw)

    except HTTPError as error:
        print(
            "ERRO PHOTON HTTP:",
            error.code,
            error.reason
        )
        return []

    except URLError as error:
        print(
            "ERRO PHOTON CONEXAO:",
            error.reason
        )
        return []

    except Exception as error:
        print(
            "ERRO PHOTON:",
            repr(error)
        )
        return []

    results = []

    for feature in data.get("features", []):
        properties = feature.get(
            "properties",
            {}
        )

        coordinates = (
            feature
            .get("geometry", {})
            .get("coordinates", [])
        )

        if len(coordinates) < 2:
            continue

        name = properties.get(
            "name",
            ""
        )

        parts = [
            properties.get("street"),
            properties.get("district"),
            properties.get("city"),
            properties.get("state"),
            properties.get("country")
        ]

        description = ", ".join(
            str(part)
            for part in parts
            if part and part != name
        )

        results.append({
            "name": name or description,
            "description": description,
            "longitude": coordinates[0],
            "latitude": coordinates[1]
        })

    print(
        "RESULTADOS PROCESSADOS:",
        results
    )

    return results