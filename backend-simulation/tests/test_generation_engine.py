from datetime import timedelta, timezone

import pytest

from app.models.enums import ScenarioType
from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import HeartRateMeasurement
from app.models.simulation_requests import ScenarioSimulationRequest
from app.services.generation.engine import SimulationGenerationEngine
from app.services.generation.randomizer import SimulationRandomizer


class TestSleepGenerator:
    def generate_day(
        self,
        context,
        day,
        measured_at,
        randomizer,
    ):
        return MeasurementCollection(
            heart_rate=HeartRateMeasurement(
                value=randomizer.randint(60, 80),
                measured_at=measured_at,
                source="simulated",
                provenance={
                    "scenario_id": context.scenario_id.value,
                },
            )
        )


def build_request(**overrides):
    data = {
        "scenario_id": "sleep_deprivation",
        "mission_phase": "prolonged_microgravity",
        "parameters": {
            "simulation_days": 3,
            "sleep_duration_hours": 6.5,
            "baseline_sleep_hours": 8,
            "sleep_pattern": "progressive_reduction",
        },
        "seed": 42,
        "simulation_start_at": "2026-11-15T12:00:00+01:00",
    }
    data.update(overrides)
    return ScenarioSimulationRequest(**data)


def build_engine():
    return SimulationGenerationEngine(
        generators={
            ScenarioType.SLEEP_DEPRIVATION: TestSleepGenerator(),
        }
    )


def test_randomizer_is_reproducible():
    first = SimulationRandomizer(42)
    second = SimulationRandomizer(42)

    assert [first.randint(60, 80) for _ in range(5)] == [
        second.randint(60, 80) for _ in range(5)
    ]


def test_engine_generates_one_observation_per_day():
    result = build_engine().generate(build_request())

    assert len(result.observations) == 3
    assert [item.day for item in result.observations] == [1, 2, 3]


def test_engine_generates_timestamps_24_hours_apart():
    result = build_engine().generate(build_request())

    timestamps = [
        item.measurements.heart_rate.measured_at
        for item in result.observations
    ]

    assert timestamps[1] - timestamps[0] == timedelta(hours=24)
    assert timestamps[2] - timestamps[1] == timedelta(hours=24)
    assert all(item.utcoffset() == timedelta(0) for item in timestamps)


def test_engine_preserves_effective_seed():
    result = build_engine().generate(build_request())

    assert result.effective_seed == 42


def test_engine_preserves_simulation_start_instant():
    result = build_engine().generate(build_request())

    assert result.simulation_start_at.isoformat() == (
        "2026-11-15T12:00:00+01:00"
    )


def test_engine_generates_simulated_measurements_with_provenance():
    result = build_engine().generate(build_request())

    for observation in result.observations:
        measurement = observation.measurements.heart_rate

        assert measurement.source == "simulated"
        assert measurement.provenance.scenario_id == "sleep_deprivation"


def test_engine_is_reproducible_with_same_seed():
    engine = build_engine()

    first = engine.generate(build_request())
    second = engine.generate(build_request())

    first_values = [
        item.measurements.heart_rate.value
        for item in first.observations
    ]
    second_values = [
        item.measurements.heart_rate.value
        for item in second.observations
    ]

    assert first_values == second_values


def test_engine_generates_seed_when_omitted():
    result = build_engine().generate(
        build_request(seed=None)
    )

    assert isinstance(result.effective_seed, int)
    assert result.effective_seed >= 0


def test_engine_rejects_unregistered_scenario():
    engine = SimulationGenerationEngine(generators={})

    with pytest.raises(ValueError, match="No generator is registered"):
        engine.generate(build_request())
