from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.enums import MeasurementType
from app.models.simulation_responses import (
    RuleEvaluation,
    SimulationObservation,
    SimulationResponse,
)


VALID_TIMESTAMP = "2026-11-15T12:00:00+01:00"


def build_manual_observation():
    return {
        "measurements": {
            "heart_rate": {
                "value": 72,
                "measured_at": VALID_TIMESTAMP,
                "source": "manual",
            }
        }
    }


def build_scenario_observation(day):
    return {
        "day": day,
        "measurements": {
            "heart_rate": {
                "value": 72,
                "measured_at": VALID_TIMESTAMP,
                "source": "simulated",
                "provenance": {
                    "scenario_id": "cardiovascular_variation"
                },
            }
        },
    }


def build_valid_response():
    return {
        "simulation_id": str(uuid4()),
        "simulation_type": "manual",
        "evaluated_at": VALID_TIMESTAMP,
        "observations": [
            build_manual_observation()
        ],
    }


def build_valid_scenario_response():
    return {
        "simulation_id": str(uuid4()),
        "simulation_type": "scenario",
        "scenario_id": "cardiovascular_variation",
        "mission_phase": "prolonged_microgravity",
        "evaluated_at": VALID_TIMESTAMP,
        "simulation_start_at": VALID_TIMESTAMP,
        "effective_seed": 42,
        "observations": [
            build_scenario_observation(1),
            build_scenario_observation(2),
        ],
    }


def test_simulation_response_accepts_valid_manual_data():
    response = SimulationResponse(**build_valid_response())

    assert response.simulation_type == "manual"
    assert len(response.observations) == 1
    assert response.observations[0].day is None
    assert response.observations[0].measurements.heart_rate.value == 72


def test_simulation_response_accepts_valid_scenario_data():
    response = SimulationResponse(**build_valid_scenario_response())

    assert response.simulation_type == "scenario"
    assert response.scenario_id.value == "cardiovascular_variation"
    assert response.mission_phase == "prolonged_microgravity"
    assert len(response.observations) == 2
    assert response.simulation_start_at.isoformat() == (
        "2026-11-15T12:00:00+01:00"
    )
    assert response.effective_seed == 42


def test_scenario_response_requires_simulation_start_at():
    data = build_valid_scenario_response()
    data.pop("simulation_start_at")

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_response_requires_effective_seed():
    data = build_valid_scenario_response()
    data.pop("effective_seed")

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_response_rejects_negative_effective_seed():
    data = build_valid_scenario_response()
    data["effective_seed"] = -1

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_response_rejects_start_timestamp_without_timezone():
    data = build_valid_scenario_response()
    data["simulation_start_at"] = "2026-11-15T12:00:00"

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_manual_response_rejects_simulation_start_at():
    data = build_valid_response()
    data["simulation_start_at"] = VALID_TIMESTAMP

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_manual_response_rejects_effective_seed():
    data = build_valid_response()
    data["effective_seed"] = 42

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


@pytest.mark.parametrize(
    "outcome",
    ["triggered", "not_triggered", "not_evaluable"],
)
def test_rule_evaluation_accepts_valid_outcomes(outcome):
    evaluation = RuleEvaluation(
        rule_id="example_rule",
        outcome=outcome,
        explanation="This is a test explanation.",
    )

    assert evaluation.outcome == outcome


def test_rule_evaluation_rejects_unknown_outcome():
    with pytest.raises(ValidationError):
        RuleEvaluation(
            rule_id="example_rule",
            outcome="unknown",
            explanation="This is a test explanation.",
        )


def test_simulation_response_rejects_timestamp_without_timezone():
    data = build_valid_response()
    data["evaluated_at"] = datetime(2026, 11, 15, 12, 0, 0)

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_simulation_response_rejects_unknown_simulation_type():
    data = build_valid_response()
    data["simulation_type"] = "automatic"

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_simulation_response_rejects_empty_observations():
    data = build_valid_response()
    data["observations"] = []

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_manual_simulation_rejects_multiple_observations():
    data = build_valid_response()
    data["observations"] = [
        build_manual_observation(),
        build_manual_observation(),
    ]

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_manual_simulation_rejects_simulation_day():
    data = build_valid_response()
    data["observations"][0]["day"] = 1

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_manual_simulation_rejects_simulated_measurements():
    data = build_valid_response()
    data["observations"][0] = build_scenario_observation(1)

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_requires_scenario_id():
    data = build_valid_scenario_response()
    data.pop("scenario_id")

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_requires_mission_phase():
    data = build_valid_scenario_response()
    data.pop("mission_phase")

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_rejects_unknown_phase():
    data = build_valid_scenario_response()
    data["mission_phase"] = "unknown_phase"

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_rejects_phase_from_another_scenario():
    data = build_valid_scenario_response()
    data["scenario_id"] = "dehydration"
    data["mission_phase"] = "suited_operations"

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_requires_consecutive_days():
    data = build_valid_scenario_response()
    data["observations"] = [
        build_scenario_observation(1),
        build_scenario_observation(3),
    ]

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_requires_days_starting_at_one():
    data = build_valid_scenario_response()
    data["observations"] = [
        build_scenario_observation(2),
    ]

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_rejects_manual_measurements():
    data = build_valid_scenario_response()
    data["observations"][0]["measurements"]["heart_rate"]["source"] = (
        "manual"
    )
    data["observations"][0]["measurements"]["heart_rate"].pop(
        "provenance"
    )

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_scenario_simulation_rejects_wrong_provenance():
    data = build_valid_scenario_response()
    data["observations"][0]["measurements"]["heart_rate"][
        "provenance"
    ]["scenario_id"] = "sleep_deprivation"

    with pytest.raises(ValidationError):
        SimulationResponse(**data)


def test_observation_accepts_empty_rule_evaluations():
    observation = SimulationObservation(
        **build_manual_observation()
    )

    assert observation.rule_evaluations == []


def test_rule_evaluation_accepts_valid_measurement_type():
    evaluation = RuleEvaluation(
        rule_id="heart_rate_rule",
        outcome="triggered",
        explanation="A test rule was triggered.",
        related_measurements=["heart_rate"],
    )

    assert evaluation.related_measurements == [
        MeasurementType.HEART_RATE
    ]


def test_rule_evaluation_rejects_unknown_measurement_type():
    with pytest.raises(ValidationError):
        RuleEvaluation(
            rule_id="unknown_rule",
            outcome="triggered",
            explanation="A test rule was triggered.",
            related_measurements=["banana"],
        )


def test_response_flattening_includes_alveolar_ventilation():
    from app.models.measurement_collection import MeasurementCollection
    from app.models.measurements import (
        AlveolarVentilationMeasurement,
        RespirationMeasurement,
    )

    alveolar = AlveolarVentilationMeasurement(
        value=4.9,
        measured_at=VALID_TIMESTAMP,
        source="manual",
    )
    measurements = MeasurementCollection(
        respiration=RespirationMeasurement(
            alveolar_ventilation=alveolar
        )
    )

    flattened = SimulationResponse._get_measurements(measurements)

    assert alveolar in flattened
