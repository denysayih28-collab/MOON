
import pytest

from app.models.enums import ScenarioType
from app.models.simulation_requests import ScenarioSimulationRequest
from app.services.generation.registry import build_default_generation_engine


START = "2026-11-15T12:00:00+01:00"


def generate(scenario_id, parameters, seed=42):
    request = ScenarioSimulationRequest(
        scenario_id=scenario_id,
        mission_phase="prolonged_microgravity",
        parameters=parameters,
        seed=seed,
        simulation_start_at=START,
    )
    return build_default_generation_engine().generate(request)


def test_sleep_generator_produces_sleep_without_inventing_other_measures():
    result = generate(ScenarioType.SLEEP_DEPRIVATION, {
        "simulation_days": 3,
        "sleep_duration_hours": 6.5,
        "baseline_sleep_hours": 8,
        "sleep_pattern": "progressive_reduction",
    })
    assert len(result.observations) == 3
    for item in result.observations:
        assert item.measurements.sleep is not None
        assert item.measurements.mood is None
        assert item.measurements.heart_rate is None


def test_cardiovascular_generator_requires_reference_data():
    with pytest.raises(ValueError, match="requires a heart-rate baseline"):
        generate(ScenarioType.CARDIOVASCULAR_VARIATION, {
            "simulation_days": 2,
            "exercise_countermeasure": False,
        })


def test_cardiovascular_generator_requires_complete_pressure_baseline():
    with pytest.raises(ValueError, match="Both systolic and diastolic"):
        generate(ScenarioType.CARDIOVASCULAR_VARIATION, {
            "simulation_days": 2,
            "baseline_systolic_pressure": 120,
            "exercise_countermeasure": False,
        })


def test_cardiovascular_generator_uses_provided_heart_rate_baseline():
    result = generate(ScenarioType.CARDIOVASCULAR_VARIATION, {
        "simulation_days": 2,
        "baseline_heart_rate": 70,
        "exercise_countermeasure": True,
    })
    for item in result.observations:
        assert item.measurements.heart_rate is not None
        assert item.measurements.blood_pressure is None


def test_respiratory_generator_calculates_minute_ventilation():
    result = generate(ScenarioType.RESPIRATORY_VARIATION, {
        "simulation_days": 2,
        "baseline_respiratory_rate": 14,
        "baseline_tidal_volume_ml": 500,
    })
    for item in result.observations:
        respiration = item.measurements.respiration
        expected = (
            respiration.respiratory_rate.value
            * respiration.tidal_volume.value / 1000
        )
        assert respiration.minute_ventilation.value == pytest.approx(
            expected, abs=0.001
        )
        assert item.measurements.oxygen_saturation is None


def test_physical_activity_does_not_invent_step_count():
    result = generate(ScenarioType.PHYSICAL_INACTIVITY, {
        "simulation_days": 3,
        "baseline_activity_duration": 60,
        "activity_pattern": "progressive_reduction",
        "countermeasure_profile": "combined",
    })
    activity = [
        item.measurements.physical_activity
        for item in result.observations
    ]
    assert all(item.step_count is None for item in activity)
    assert activity[0].duration_minutes > activity[-1].duration_minutes


def test_fluid_intake_does_not_infer_dehydration():
    result = generate(ScenarioType.DEHYDRATION, {
        "simulation_days": 3,
        "baseline_fluid_intake_ml": 2000,
        "intake_pattern": "progressive_reduction",
        "heat_exposure": "high",
        "suited_activity": True,
    })
    intake = [item.measurements.fluid_intake for item in result.observations]
    assert all(item.period_hours == 24 for item in intake)
    assert intake[0].value_ml > intake[-1].value_ml
    assert all(
        item.measurements.body_temperature is None
        for item in result.observations
    )


def test_generators_preserve_provenance():
    result = generate(ScenarioType.DEHYDRATION, {
        "simulation_days": 1,
        "baseline_fluid_intake_ml": 2000,
        "intake_pattern": "stable_intake",
        "heat_exposure": "none",
        "suited_activity": False,
    })
    measurement = result.observations[0].measurements.fluid_intake
    assert measurement.source == "simulated"
    assert measurement.provenance.scenario_id == "dehydration"


def test_generators_are_reproducible_with_same_seed():
    parameters = {
        "simulation_days": 3,
        "baseline_fluid_intake_ml": 2000,
        "intake_pattern": "irregular_intake",
        "heat_exposure": "moderate",
        "suited_activity": False,
    }
    first = generate(ScenarioType.DEHYDRATION, parameters, seed=123)
    second = generate(ScenarioType.DEHYDRATION, parameters, seed=123)
    assert [
        item.measurements.fluid_intake.value_ml
        for item in first.observations
    ] == [
        item.measurements.fluid_intake.value_ml
        for item in second.observations
    ]



def test_alveolar_ventilation_uses_explicit_dead_space():
    result = generate(ScenarioType.RESPIRATORY_VARIATION, {
        "simulation_days": 2,
        "baseline_respiratory_rate": 14,
        "baseline_tidal_volume_ml": 500,
        "dead_space_volume_ml": 150,
    })

    for observation in result.observations:
        respiration = observation.measurements.respiration
        alveolar = respiration.alveolar_ventilation

        expected = (
            (respiration.tidal_volume.value - 150)
            * respiration.respiratory_rate.value
            / 1000
        )

        assert alveolar.value == pytest.approx(expected, abs=0.0001)
        assert alveolar.unit == "L/min"
        assert alveolar.source.value == "simulated"
        assert alveolar.provenance.derivation is not None
        assert alveolar.provenance.input_measurements == [
            "tidal_volume",
            "respiratory_rate",
        ]
        assert alveolar.provenance.assumptions == [
            "dead_space_volume_ml=150"
        ]


def test_alveolar_ventilation_is_not_calculated_without_dead_space():
    result = generate(ScenarioType.RESPIRATORY_VARIATION, {
        "simulation_days": 1,
        "baseline_respiratory_rate": 14,
        "baseline_tidal_volume_ml": 500,
    })

    respiration = result.observations[0].measurements.respiration

    assert respiration.alveolar_ventilation is None
    assert len(result.notices) == 1
    assert "no dead-space volume" in result.notices[0]
