import pytest
from pydantic import ValidationError
from app.models.simulation_requests import (
    ManualSimulationRequest,
    ScenarioSimulationRequest,
)
from app.models.enums import ActivityIntensity, MoodLevel
from app.models.measurements import (
    FluidIntakeMeasurement,
    HeartRateMeasurement,
    MoodMeasurement,
    OxygenSaturationMeasurement,
    PhysicalActivityMeasurement,
    RespirationMeasurement,
)



VALID_TIMESTAMP = "2026-11-15T14:30:00Z"


def test_valid_heart_rate():
    measurement = HeartRateMeasurement(
        value=72,
        measured_at=VALID_TIMESTAMP,
        source="manual",
    )

    assert measurement.value == 72
    assert measurement.unit == "bpm"


def test_reject_oxygen_saturation_above_100():
    with pytest.raises(ValidationError):
        OxygenSaturationMeasurement(
            value=105,
            measured_at=VALID_TIMESTAMP,
            source="manual",
        )


def test_reject_datetime_without_timezone():
    with pytest.raises(ValidationError):
        HeartRateMeasurement(
            value=72,
            measured_at="2026-11-15T14:30:00",
            source="manual",
        )


def test_respiration_can_contain_only_one_measurement():
    respiration = RespirationMeasurement(
        respiratory_rate={
            "value": 16,
            "unit": "breaths/min",
            "measured_at": VALID_TIMESTAMP,
            "source": "manual",
        }
    )

    assert respiration.respiratory_rate.value == 16
    assert respiration.tidal_volume is None
    assert respiration.minute_ventilation is None


def test_mood_accepts_defined_category():
    mood = MoodMeasurement(
        value=MoodLevel.GOOD,
        measured_at=VALID_TIMESTAMP,
        source="manual",
    )

    assert mood.value == MoodLevel.GOOD


def test_mood_rejects_unknown_category():
    with pytest.raises(ValidationError):
        MoodMeasurement(
            value="excellent",
            measured_at=VALID_TIMESTAMP,
            source="manual",
        )


def test_valid_physical_activity():
    activity = PhysicalActivityMeasurement(
        duration_minutes=45,
        step_count=5200,
        intensity=ActivityIntensity.MODERATE,
        measured_at=VALID_TIMESTAMP,
        source="manual",
    )

    assert activity.duration_minutes == 45
    assert activity.step_count == 5200
    assert activity.intensity == ActivityIntensity.MODERATE


def test_reject_negative_step_count():
    with pytest.raises(ValidationError):
        PhysicalActivityMeasurement(
            duration_minutes=45,
            step_count=-100,
            measured_at=VALID_TIMESTAMP,
            source="manual",
        )


from app.models.measurement_collection import MeasurementCollection


def test_measurement_collection_accepts_partial_data():
    collection = MeasurementCollection(
        heart_rate={
            "value": 72,
            "measured_at": VALID_TIMESTAMP,
            "source": "manual",
        },
        oxygen_saturation={
            "value": 98,
            "measured_at": VALID_TIMESTAMP,
            "source": "manual",
        },
    )

    assert collection.heart_rate.value == 72
    assert collection.oxygen_saturation.value == 98
    assert collection.sleep is None


def test_measurement_collection_rejects_empty_data():
    with pytest.raises(ValidationError):
        MeasurementCollection()


def test_respiration_rejects_empty_data():
    with pytest.raises(ValidationError):
        RespirationMeasurement()

def test_simulated_measurement_requires_scenario_id():
    with pytest.raises(ValidationError):
        HeartRateMeasurement(
            value=72,
            measured_at=VALID_TIMESTAMP,
            source="simulated",
        )


def test_simulated_measurement_accepts_scenario_id():
    measurement = HeartRateMeasurement(
        value=72,
        measured_at=VALID_TIMESTAMP,
        source="simulated",
        provenance={
            "scenario_id": "sleep_deprivation",
        },
    )

    assert measurement.provenance.scenario_id == "sleep_deprivation"


def test_scientific_measurement_requires_dataset_reference():
    with pytest.raises(ValidationError):
        HeartRateMeasurement(
            value=72,
            measured_at=VALID_TIMESTAMP,
            source="scientific_dataset",
            provenance={
                "dataset_name": "NASA HRP Dataset",
            },
        )


def test_scientific_measurement_accepts_documented_source():
    measurement = HeartRateMeasurement(
        value=72,
        measured_at=VALID_TIMESTAMP,
        source="scientific_dataset",
        provenance={
            "dataset_name": "NASA HRP Dataset",
            "source_reference": "https://example.org/dataset",
        },
    )

    assert measurement.provenance.dataset_name == "NASA HRP Dataset"
    assert measurement.provenance.source_reference == "https://example.org/dataset"

def test_manual_simulation_accepts_manual_measurements():
    request = ManualSimulationRequest(
        measurements={
            "heart_rate": {
                "value": 72,
                "measured_at": VALID_TIMESTAMP,
                "source": "manual",
            }
        }
    )

    assert request.measurements.heart_rate.value == 72


def test_manual_simulation_rejects_simulated_measurements():
    with pytest.raises(ValidationError):
        ManualSimulationRequest(
            measurements={
                "heart_rate": {
                    "value": 72,
                    "measured_at": VALID_TIMESTAMP,
                    "source": "simulated",
                    "provenance": {
                        "scenario_id": "sleep_deprivation",
                    },
                }
            }
        )


def build_valid_scenario_request():
    return {
        "scenario_id": "sleep_deprivation",
        "mission_phase": "prolonged_microgravity",
        "parameters": {
            "simulation_days": 7,
            "sleep_duration_hours": 6.5,
            "baseline_sleep_hours": 8,
            "sleep_pattern": "progressive_reduction",
        },
        "seed": 42,
    }


def test_scenario_simulation_accepts_valid_request():
    request = ScenarioSimulationRequest(**build_valid_scenario_request())

    assert request.scenario_id == "sleep_deprivation"
    assert request.mission_phase == "prolonged_microgravity"
    assert request.parameters["simulation_days"] == 7
    assert request.seed == 42
    assert request.simulation_start_at is None


def test_scenario_request_accepts_timezone_aware_start():
    data = build_valid_scenario_request()
    data["simulation_start_at"] = "2026-11-15T12:00:00+01:00"

    request = ScenarioSimulationRequest(**data)

    assert request.simulation_start_at.isoformat() == (
        "2026-11-15T12:00:00+01:00"
    )


def test_scenario_request_accepts_missing_start_timestamp():
    data = build_valid_scenario_request()
    data.pop("simulation_start_at", None)

    request = ScenarioSimulationRequest(**data)

    assert request.simulation_start_at is None


def test_scenario_request_rejects_start_without_timezone():
    data = build_valid_scenario_request()
    data["simulation_start_at"] = "2026-11-15T12:00:00"

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_negative_seed():
    data = build_valid_scenario_request()
    data["seed"] = -1

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_unknown_scenario():
    data = build_valid_scenario_request()
    data["scenario_id"] = "banana"

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_unknown_mission_phase():
    data = build_valid_scenario_request()
    data["mission_phase"] = "unknown_phase"

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_phase_from_another_scenario():
    data = build_valid_scenario_request()
    data["scenario_id"] = "cardiovascular_variation"
    data["mission_phase"] = "suited_operations"

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_missing_required_parameter():
    data = build_valid_scenario_request()
    data["parameters"].pop("sleep_duration_hours")

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_unknown_parameter():
    data = build_valid_scenario_request()
    data["parameters"]["unknown_parameter"] = 10

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_wrong_parameter_type():
    data = build_valid_scenario_request()
    data["parameters"]["simulation_days"] = "seven"

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_boolean_as_integer():
    data = build_valid_scenario_request()
    data["parameters"]["simulation_days"] = True

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_value_below_minimum():
    data = build_valid_scenario_request()
    data["parameters"]["sleep_duration_hours"] = -1

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_rejects_invalid_enum_value():
    data = build_valid_scenario_request()
    data["parameters"]["sleep_pattern"] = "random_pattern"

    with pytest.raises(ValidationError):
        ScenarioSimulationRequest(**data)


def test_scenario_simulation_accepts_omitted_optional_parameters():
    request = ScenarioSimulationRequest(
        scenario_id="cardiovascular_variation",
        mission_phase="prolonged_microgravity",
        parameters={
            "simulation_days": 5,
            "exercise_countermeasure": True,
        },
    )

    assert "baseline_heart_rate" not in request.parameters
    assert "baseline_systolic_pressure" not in request.parameters
    assert "baseline_diastolic_pressure" not in request.parameters


def test_valid_fluid_intake():
    measurement = FluidIntakeMeasurement(
        value_ml=1500,
        period_hours=12,
        measured_at=VALID_TIMESTAMP,
        source="manual",
    )

    assert measurement.value_ml == 1500
    assert measurement.period_hours == 12
    assert measurement.unit == "mL"


def test_fluid_intake_rejects_negative_volume():
    with pytest.raises(ValidationError):
        FluidIntakeMeasurement(
            value_ml=-500,
            period_hours=12,
            measured_at=VALID_TIMESTAMP,
            source="manual",
        )


def test_fluid_intake_rejects_zero_period():
    with pytest.raises(ValidationError):
        FluidIntakeMeasurement(
            value_ml=1500,
            period_hours=0,
            measured_at=VALID_TIMESTAMP,
            source="manual",
        )


def test_simulated_fluid_intake_requires_scenario_id():
    with pytest.raises(ValidationError):
        FluidIntakeMeasurement(
            value_ml=1500,
            period_hours=12,
            measured_at=VALID_TIMESTAMP,
            source="simulated",
        )


def test_simulated_fluid_intake_accepts_scenario_id():
    measurement = FluidIntakeMeasurement(
        value_ml=1500,
        period_hours=12,
        measured_at=VALID_TIMESTAMP,
        source="simulated",
        provenance={
            "scenario_id": "dehydration",
        },
    )

    assert measurement.provenance.scenario_id == "dehydration"


def test_manual_simulation_accepts_fluid_intake():
    request = ManualSimulationRequest(
        measurements={
            "fluid_intake": {
                "value_ml": 1500,
                "period_hours": 12,
                "measured_at": VALID_TIMESTAMP,
                "source": "manual",
            }
        }
    )

    assert request.measurements.fluid_intake.value_ml == 1500