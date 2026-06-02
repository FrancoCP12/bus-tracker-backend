from sqlalchemy.orm import Session
from app.models.route import Route
from app.models.bus_stop import BusStop
from app.models.bus import Bus
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_DWithin, ST_GeomFromText, ST_LineLocatePoint
from sqlalchemy import func, and_
from shapely.geometry import shape
import json
from typing import Optional


def create_route_from_geojson(db: Session, geojson: str, bus_id: int) -> dict:
    data = json.loads(geojson)
    features = data.get("features", [])

    ruta_data = next(
        (f for f in features if f["properties"].get("type") == "route"), None
    )
    if not ruta_data:
        return {"error": "No route found in GeoJSON"}

    geom_ruta = shape(ruta_data["geometry"])
    new_route = Route(position=f"SRID=4326;{geom_ruta.wkt}")
    db.add(new_route)
    db.flush()

    for f in features:
        if f["properties"].get("type") == "bus_stop":
            geom_parada = shape(f["geometry"])
            point_wkt = f"SRID=4326;{geom_parada.wkt}"

            existing_stop = (
                db.query(BusStop)
                .filter(
                    func.ST_DWithin(
                        func.cast(BusStop.position, Geography),
                        func.cast(func.ST_GeomFromText(point_wkt, 4326), Geography),
                        15,
                    )
                )
                .first()
            )

            if existing_stop:
                new_route.stops.append(existing_stop)
            else:
                nueva_parada = BusStop(position=point_wkt)
                db.add(nueva_parada)
                new_route.stops.append(nueva_parada)

    new_bus = db.query(Bus).filter(Bus.id_bus == bus_id).first()
    if new_bus:
        new_bus.id_route = new_route.id_route

    db.commit()
    return {"message": "Ruta y paradas procesadas correctamente"}


def get_bus_stops_near(db: Session, lat: float, lon: float):
    user_point = f"SRID=4326;POINT({lon} {lat})"

    return (
        db.query(BusStop)
        .filter(
            func.ST_DWithin(
                func.cast(BusStop.position, Geography),
                func.cast(func.ST_GeomFromText(user_point, 4326), Geography),
                500,
            )
        )
        .all()
    )


def get_next_bus_stop(db: Session, bus_id: int, lat: float, lon: float):
    bus_point = f"SRID=4326;POINT({lon} {lat})"

    return (
        db.query(BusStop)
        .join(Route, BusStop.id_route == Route.id_route)
        .join(Bus, Bus.id_route == Route.id_route)
        .filter(
            Bus.id_bus == bus_id,
            ST_LineLocatePoint(Route.position, bus_point)
            < ST_LineLocatePoint(Route.position, BusStop.position),
        )
        .order_by(ST_LineLocatePoint(Route.position, BusStop.position))
        .first()
    )


def get_buses_by_stop_id(db: Session, stop_id: int) -> list[int]:
    results = (
        db.query(Bus.id_bus)
        .join(Route, Bus.id_route == Route.id_route)
        .join(BusStop, BusStop.id_route == Route.id_route)
        .filter(BusStop.id_bus_stop == stop_id)
        .all()
    )
    return [r[0] for r in results]


def search_buses_by_location(
    db: Session, lat_origin: float, lon_origin: float, lat_dest: float, lon_dest: float
):
    user_point = f"SRID=4326;POINT({lon_origin} {lat_origin})"
    final_point = f"SRID=4326;POINT({lon_dest} {lat_dest})"

    from sqlalchemy.orm import aliased
    from sqlalchemy import select

    P_Origen = aliased(BusStop)
    P_Destiny = aliased(BusStop)

    stmt = (
        select(Route.id_route)
        .join(P_Origen, Route.id_route == P_Origen.id_route)
        .join(P_Destiny, Route.id_route == P_Destiny.id_route)
        .where(
            and_(
                ST_DWithin(P_Origen.position, user_point, 0.0045),
                ST_DWithin(P_Destiny.position, final_point, 0.0045),
                ST_LineLocatePoint(Route.position, P_Origen.position)
                < ST_LineLocatePoint(Route.position, P_Destiny.position),
            )
        )
        .distinct()
    )

    route_ids = db.execute(stmt).scalars().all()
    return db.query(Bus).filter(Bus.id_route.in_(route_ids)).all()


def get_distance_to_stop(
    db: Session, bus_lon: float, bus_lat: float, stop_id: int
) -> float:
    from geoalchemy2.functions import (
        ST_Distance,
        ST_LineInterpolatePoint,
        ST_LineLocatePoint,
        ST_SetSRID,
        ST_MakePoint,
    )

    bus_point = ST_SetSRID(ST_MakePoint(bus_lon, bus_lat), 4326)

    result = (
        db.query(
            ST_Distance(
                ST_LineInterpolatePoint(
                    Route.position, ST_LineLocatePoint(Route.position, bus_point)
                ),
                ST_LineInterpolatePoint(
                    Route.position, ST_LineLocatePoint(Route.position, BusStop.position)
                ),
                True,
            ).label("distance_meters")
        )
        .join(Bus, Bus.id_route == Route.id_route)
        .join(BusStop, BusStop.id_route == Route.id_route)
        .filter(BusStop.id_bus_stop == stop_id)
        .first()
    )

    if not result:
        return 0.0

    return float(result.distance_meters)
