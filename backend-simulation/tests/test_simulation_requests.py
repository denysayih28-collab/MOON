import pytest
from pydantic import ValidationError

from app.models.simulation_requests import ScenarioSimulationRequest


def build_respiratory_request(dead_space_volume_ml=150):
    parameters = {
        "simulation_days": 1,
        "baseline_respiratory_rate": 14,
        "baseline_tidal_volume_ml": 500,
    }

    if dead_space_volume_ml is not None:
        parameters["dead_space_volume_ml"] = dead_space_volume_ml

    return {
        "scenario_id": "respiratory_variation",
        "mission_phase": "prolonged_microgravity",
        "parameters": parameters,
        "seed": 42,
    }


def test_respiratory_request_accepts_explicit_dead_space():
    request = ScenarioSimulationRequest(
        **build_respiratory_request(150)
    )

    assert request.parameters["dead_space_volume_ml"] == 150


def test_respiratory_request_rejects_dead_space_above_minimum_tidal_volume():
    with pytest.raises(ValidationError, match="minimum generated tidal volume"):
        ScenarioSimulationRequest(
            **build_respiratory_request(485.01)
        )


def test_respiratory_request_accepts_dead_space_at_minimum_tidal_volume():
    request = ScenarioSimulationRequest(
        **build_respiratory_request(485)
    )

    assert request.parameters["dead_space_volume_ml"] == 485


def test_respiratory_request_allows_missing_dead_space():
    request = ScenarioSimulationRequest(
        **build_respiratory_request(None)
    )

    assert "dead_space_volume_ml" not in request.parameters
