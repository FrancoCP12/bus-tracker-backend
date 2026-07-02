from app.domain.interfaces.route_repository import IRouteRepository
from app.domain.interfaces.location_service import ILocationService


class RouteUseCase:
    def __init__(self, route_repo: IRouteRepository, location_service: ILocationService):
        self._route_repo = route_repo
        self._location_service = location_service

    def create_from_geojson(self, geojson: str, bus_id: int) -> dict:
        return self._route_repo.create_route_from_geojson(geojson, bus_id)

    def get_stops_near(self, lat: float, lon: float) -> list:
        return self._route_repo.get_stops_near(lat, lon)

    def search_buses(self, lat_origin: float, lon_origin: float, lat_dest: float, lon_dest: float) -> list:
        return self._route_repo.search_buses_along_route(lat_origin, lon_origin, lat_dest, lon_dest)
