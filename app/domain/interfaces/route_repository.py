from abc import ABC, abstractmethod
from app.domain.entities.route import Route, BusStop
from app.domain.entities.bus import Bus


class IRouteRepository(ABC):
    @abstractmethod
    def get_stops_near(self, lat: float, lon: float, radius_m: int = 500) -> list[BusStop]: ...

    @abstractmethod
    def get_next_stop(self, bus_id: int, lat: float, lon: float) -> BusStop | None: ...

    @abstractmethod
    def get_bus_ids_by_stop(self, stop_id: int) -> list[int]: ...

    @abstractmethod
    def search_buses_along_route(
        self, lat_origin: float, lon_origin: float, lat_dest: float, lon_dest: float
    ) -> list[Bus]: ...

    @abstractmethod
    def get_distance_to_stop(self, bus_lon: float, bus_lat: float, stop_id: int) -> float: ...

    @abstractmethod
    def create_route_from_geojson(self, geojson: str, bus_id: int) -> dict: ...
