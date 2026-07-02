from app.domain.interfaces.location_service import ILocationService
from app.domain.interfaces.route_repository import IRouteRepository
from app.domain.exceptions import InvalidParameters
from app.services.eta_service import calculate_speed, calculate_eta
from typing import Any


class EtaUseCase:
    def __init__(self, location_service: ILocationService, route_repo: IRouteRepository):
        self._location_service = location_service
        self._route_repo = route_repo

    async def calculate(
        self,
        id_bus: int | None = None,
        company: str | None = None,
        stop_id: int | None = None,
    ) -> dict[str, dict[str, Any]]:
    
        bus_coords: dict[str, list[list[float]]] = {}
        id_stop = stop_id

        if id_bus or company:
            location = await self._location_service.get_location(
                str(id_bus) if id_bus else None, company
            )
            bus_info = location["buses"].get(str(id_bus))
            if bus_info and "coord" in bus_info:
                bus_coords[str(id_bus)] = bus_info["coord"]

        elif stop_id:
            for bus_id_int in self._route_repo.get_bus_ids_by_stop(stop_id):
                location = await self._location_service.get_location(str(bus_id_int), None)
                bus_info = location["buses"].get(str(bus_id_int))
                if bus_info and "coord" in bus_info:
                    bus_coords[str(bus_id_int)] = bus_info["coord"]
        else:
            raise InvalidParameters("id_bus, company or stop_id required")

        if not stop_id and bus_coords:
            bus_id_str = list(bus_coords.keys())[0]
            coords = bus_coords[bus_id_str]
            if coords:
                bus_lon, bus_lat = coords[-1][0], coords[-1][1]
                stop_obj = self._route_repo.get_next_stop(int(bus_id_str), bus_lat, bus_lon)
                id_stop = stop_obj.id_bus_stop if stop_obj else None

        buses_eta = {}
        for bus_id_str, coords in bus_coords.items():
            if not coords:
                continue
            bus_lon, bus_lat = coords[-1][0], coords[-1][1]
            timestamp = coords[-1][2] if len(coords[-1]) > 2 else None

            if id_stop:
                velocity = calculate_speed(coords)
                distance = self._route_repo.get_distance_to_stop(bus_lon, bus_lat, id_stop)
                eta_data = calculate_eta(velocity, distance)
                buses_eta[bus_id_str] = {
                    "coord": [bus_lon, bus_lat],
                    "timestamp": timestamp,
                    **eta_data,
                }

        return buses_eta
