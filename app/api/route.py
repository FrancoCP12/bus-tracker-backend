from fastapi import HTTPException, APIRouter, Depends
from app.services.eta_service import calculate_speed, calculate_eta
from app.repositories.route_repository import (
    create_route_from_geojson,
    get_bus_stops_near,
    get_next_bus_stop,
    get_buses_by_stop_id,
    search_buses_by_location,
    get_distance_to_stop,
)
from app.services.location_service import LocationService, get_location_service
from sqlalchemy.orm import Session
from app.db.base import get_db
from typing import Any

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/geojson/")
def store_route(geojson: str, bus_id: int, db: Session = Depends(get_db)):
    return create_route_from_geojson(db, geojson, bus_id)


@router.get("/bus-stop/{user_lat}/{user_lon}")
def get_bus_stops(user_lat: float, user_lon: float, db: Session = Depends(get_db)):
    return get_bus_stops_near(db, user_lat, user_lon)


@router.get("/buses/eta/")
async def get_eta(
    id_bus: int | None = None,
    company: str | None = None,
    stop_id: int | None = None,
    session: Session = Depends(get_db),
    location_service: LocationService = Depends(get_location_service),
) -> dict[str, dict[str, Any]]:
    bus_coords: dict[str, list[list[float]]] = {}
    id_stop = stop_id

    if id_bus or company:
        location = await location_service.get_location(
            str(id_bus) if id_bus else None, company
        )
        bus_info = location["buses"].get(str(id_bus))
        if bus_info and "coord" in bus_info:
            bus_coords[str(id_bus)] = bus_info["coord"]

    elif stop_id:
        for bus_id_int in get_buses_by_stop_id(session, stop_id):
            location = await location_service.get_location(str(bus_id_int), None)
            bus_info = location["buses"].get(str(bus_id_int))
            if bus_info and "coord" in bus_info:
                bus_coords[str(bus_id_int)] = bus_info["coord"]
    else:
        raise HTTPException(status_code=400, detail="Parámetros inválidos")

    if not stop_id and bus_coords:
        bus_id_str = list(bus_coords.keys())[0]
        coords = bus_coords[bus_id_str]
        if coords:
            bus_lat, bus_lon = coords[-1][0], coords[-1][1]
            stop_obj = get_next_bus_stop(session, int(bus_id_str), bus_lat, bus_lon)
            id_stop = stop_obj.id_bus_stop if stop_obj else None

    buses_eta = {}
    for bus_id_str, coords in bus_coords.items():
        if not coords:
            continue
        bus_lat, bus_lon = coords[-1][0], coords[-1][1]
        timestamp = coords[-1][2] if len(coords[-1]) > 2 else None

        if id_stop:
            velocity = calculate_speed(coords)
            distance = get_distance_to_stop(session, bus_lon, bus_lat, id_stop)
            eta_data = calculate_eta(velocity, distance)
            buses_eta[bus_id_str] = {
                "coord": [bus_lon, bus_lat],
                "timestamp": timestamp,
                **eta_data,
            }

    return buses_eta
