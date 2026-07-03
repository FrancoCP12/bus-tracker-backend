import json
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, and_, select
from geoalchemy2 import Geography
from geoalchemy2.functions import (
    ST_DWithin,
    ST_GeomFromText,
    ST_LineLocatePoint,
    ST_Distance,
    ST_LineInterpolatePoint,
    ST_SetSRID,
    ST_MakePoint,
)
from shapely.geometry import shape
from app.domain.interfaces.route_repository import IRouteRepository
from app.domain.entities.route import Route, BusStop
from app.domain.entities.bus import Bus
from app.domain.exceptions import InvalidGeoJson
from app.models.route import Route as RouteModel
from app.models.bus_stop import BusStop as BusStopModel
from app.models.bus import Bus as BusModel
from app.core.config.config import settings




def _point_wkt(lon: float, lat: float) -> str:
    return f"SRID={settings.geo_srid};POINT({lon} {lat})"


class SQLRouteRepository(IRouteRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_stops_near(self, lat: float, lon: float, radius_m: int = settings.near_user_meters) -> list[BusStop]:
        user_point = _point_wkt(lon, lat)
        results = (
            self._session.query(BusStopModel)
            .filter(
                func.ST_DWithin(
                    func.cast(BusStopModel.position, Geography),
                    func.cast(func.ST_GeomFromText(user_point, settings.geo_srid), Geography),
                    radius_m,
                )
            )
            .all()
        )
        def _to_domain(bs: BusStopModel) -> BusStop:
            return BusStop(
                id_bus_stop=bs.id_bus_stop,
                id_route=bs.id_route,
                position=str(bs.position),
            )
        return [_to_domain(s) for s in results]

    @staticmethod
    def _to_domain_bus(model: BusModel) -> Bus:
        return Bus(
            id_bus=model.id_bus,
            id_route=model.id_route,
            patent=model.patent,
            identifier=model.identifier,
            company=model.company,
            is_active=model.is_active,
        )

    def get_next_stop(self, bus_id: int, lat: float, lon: float) -> BusStop | None:
        bus_point = _point_wkt(lon, lat)
        result = (
            self._session.query(BusStopModel)
            .join(RouteModel, BusStopModel.id_route == RouteModel.id_route)
            .join(BusModel, BusModel.id_route == RouteModel.id_route)
            .filter(
                BusModel.id_bus == bus_id,
                ST_LineLocatePoint(RouteModel.position, bus_point)
                < ST_LineLocatePoint(RouteModel.position, BusStopModel.position),
            )
            .order_by(ST_LineLocatePoint(RouteModel.position, BusStopModel.position))
            .first()
        )
        if not result:
            return None
        return BusStop(
            id_bus_stop=result.id_bus_stop,
            id_route=result.id_route,
            position=str(result.position),
        )

    def get_bus_ids_by_stop(self, stop_id: int) -> list[int]:
        results = (
            self._session.query(BusModel.id_bus)
            .join(RouteModel, BusModel.id_route == RouteModel.id_route)
            .join(BusStopModel, BusStopModel.id_route == RouteModel.id_route)
            .filter(BusStopModel.id_bus_stop == stop_id)
            .all()
        )
        return [r[0] for r in results]

    def search_buses_along_route(
        self, lat_origin: float, lon_origin: float, lat_dest: float, lon_dest: float
    ) -> list[Bus]:
        user_point = _point_wkt(lon_origin, lat_origin)
        final_point = _point_wkt(lon_dest, lat_dest)

        P_Origen = aliased(BusStopModel)
        P_Destiny = aliased(BusStopModel)

        stmt = (
            select(RouteModel.id_route)
            .join(P_Origen, RouteModel.id_route == P_Origen.id_route)
            .join(P_Destiny, RouteModel.id_route == P_Destiny.id_route)
            .where(
                and_(
                    ST_DWithin(P_Origen.position, user_point, settings.search_degrees),
                    ST_DWithin(P_Destiny.position, final_point, settings.search_degrees),
                    ST_LineLocatePoint(RouteModel.position, P_Origen.position)
                    < ST_LineLocatePoint(RouteModel.position, P_Destiny.position),
                )
            )
            .distinct()
        )

        route_ids = self._session.execute(stmt).scalars().all()
        results = self._session.query(BusModel).filter(BusModel.id_route.in_(route_ids)).all()
        return [self._to_domain_bus(b) for b in results]

    def get_distance_to_stop(self, bus_lon: float, bus_lat: float, stop_id: int) -> float:
        bus_point = ST_SetSRID(ST_MakePoint(bus_lon, bus_lat), settings.geo_srid)

        result = (
            self._session.query(
                ST_Distance(
                    ST_LineInterpolatePoint(
                        RouteModel.position, ST_LineLocatePoint(RouteModel.position, bus_point)
                    ),
                    ST_LineInterpolatePoint(
                        RouteModel.position, ST_LineLocatePoint(RouteModel.position, BusStopModel.position)
                    ),
                    True,
                ).label("distance_meters")
            )
            .join(BusModel, BusModel.id_route == RouteModel.id_route)
            .join(BusStopModel, BusStopModel.id_route == RouteModel.id_route)
            .filter(BusStopModel.id_bus_stop == stop_id)
            .first()
        )

        if not result:
            return 0.0
        return float(result.distance_meters)

    def create_route_from_geojson(self, geojson: str, bus_id: int) -> dict:
        try:
            data = json.loads(geojson)
        except json.JSONDecodeError:
            raise InvalidGeoJson("El GeoJSON proporcionado no es válido")

        features = data.get("features", [])

        route_data = next(
            (f for f in features if f["properties"].get("type") == "route"), None
        )
        if not route_data:
            raise InvalidGeoJson("No se encontró una ruta en el GeoJSON")

        geom_route = shape(route_data["geometry"])
        new_route = RouteModel(position=f"SRID={settings.geo_srid};{geom_route.wkt}")
        self._session.add(new_route)
        self._session.flush()

        for f in features:
            if f["properties"].get("type") == "bus_stop":
                geom_stop = shape(f["geometry"])
                point_wkt = f"SRID={settings.geo_srid};{geom_stop.wkt}"

                existing_stop = (
                    self._session.query(BusStopModel)
                    .filter(
                        func.ST_DWithin(
                            func.cast(BusStopModel.position, Geography),
                            func.cast(func.ST_GeomFromText(point_wkt, settings.geo_srid), Geography),
                            settings.near_stop_meters,
                        )
                    )
                    .first()
                )

                if existing_stop:
                    existing_stop.id_route = new_route.id_route
                    new_route.stops.append(existing_stop)
                else:
                    new_stop = BusStopModel(position=point_wkt, id_route=new_route.id_route)
                    self._session.add(new_stop)
                    new_route.stops.append(new_stop)

        db_bus = self._session.query(BusModel).filter(BusModel.id_bus == bus_id).first()
        if db_bus:
            db_bus.id_route = new_route.id_route

        self._session.commit()
        return {"message": "Ruta y paradas procesadas correctamente"}
