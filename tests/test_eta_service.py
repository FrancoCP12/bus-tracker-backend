import pytest
from app.services.eta_service import calculate_speed, calculate_eta


class TestCalculateSpeed:
    def test_less_than_two_points_returns_zero(self):
        coords = [[-34.0, -58.0, 100.0]]
        assert calculate_speed(coords) == 0.0

    def test_empty_list_returns_zero(self):
        assert calculate_speed([]) == 0.0

    def test_two_points_calculates_speed(self):
        coords = [
            [-34.0, -58.0, 0.0],
            [-34.001, -58.0, 3600.0],
        ]
        speed = calculate_speed(coords)
        assert speed > 0.0

    def test_zero_time_delta_returns_zero(self):
        coords = [
            [-34.0, -58.0, 100.0],
            [-34.001, -58.0, 100.0],
        ]
        assert calculate_speed(coords) == 0.0

    def test_multiple_points_averaged(self):
        coords = [
            [-34.0, -58.0, 0.0],
            [-34.0005, -58.0, 1800.0],
            [-34.001, -58.0, 3600.0],
        ]
        speed = calculate_speed(coords)
        assert speed > 0.0


class TestCalculateEta:
    def test_positive_velocity_returns_eta(self):
        result = calculate_eta(10.0, 100.0)
        assert result["velocity"] == 10.0
        assert result["distance"] == 100.0
        assert result["ETA"] == 10.0

    def test_zero_velocity_returns_waiting(self):
        result = calculate_eta(0.0, 100.0)
        assert result["velocity"] == 0.0
        assert result["distance"] == 100.0
        assert result["ETA"] == "waiting"

    def test_zero_distance(self):
        result = calculate_eta(10.0, 0.0)
        assert result["ETA"] == 0.0
