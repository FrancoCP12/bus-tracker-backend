from geopy.distance import geodesic
from typing import Any


def calculate_speed(coords: list[list[float]]) -> float:
    if len(coords) < 2:
        return 0.0

    total_distance = 0.0
    for i in range(len(coords) - 1):
        coord_a = (coords[i][1], coords[i][0])
        coord_b = (coords[i + 1][1], coords[i + 1][0])
        total_distance += geodesic(coord_a, coord_b).meters

    time_0 = coords[0][2]
    time_1 = coords[-1][2]
    total_time = time_1 - time_0

    if total_time <= 0:
        return 0.0

    return total_distance / total_time


def calculate_eta(velocity: float, distance: float) -> dict[str, Any]:
    eta = distance / velocity if velocity > 0 else "waiting"

    return {"velocity": velocity, "distance": distance, "ETA": eta}
