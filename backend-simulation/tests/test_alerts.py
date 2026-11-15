from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.models.simulation_responses import (
    SimulationObservation,
    SimulationResponse,
)
from app.rules.engine import evaluate_simulation
from app.services import alert_store


@pytest.fixture
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setattr(
        alert_store,
        "DB_PATH",
        tmp_path / "test_alerts.sqlite3",
    )
    alert_store.init_db()


def build_manual_response(heart_rate_value):
    return SimulationResponse(
        simulation_id=uuid4(),
        simulation_type="manual",
        evaluated_at=datetime.now(timezone.utc),
        observations=[
            SimulationObservation(
                measurements={
                    "heart_rate": {
                        "value": heart_rate_value,
                        "measured_at": datetime.now(timezone.utc),
                        "source": "manual",
                    }
                }
            )
        ],
    )


def build_scenario_response():
    simulation_id = uuid4()
    timestamp = datetime.now(timezone.utc)

    observations = []

    for day in (1, 2):
        observations.append(
            SimulationObservation(
                day=day,
                measurements={
                    "heart_rate": {
                        "value": 55,
                        "measured_at": timestamp.replace(
                            day=timestamp.day
                        ),
                        "source": "simulated",
                        "provenance": {
                            "scenario_id": "cardiovascular_variation"
                        },
                    }
                },
            )
        )

    return SimulationResponse(
        simulation_id=simulation_id,
        simulation_type="scenario",
        scenario_id="cardiovascular_variation",
        mission_phase="prolonged_microgravity",
        evaluated_at=timestamp,
        simulation_start_at=timestamp,
        effective_seed=42,
        observations=observations,
    )


def test_extreme_heart_rate_creates_persistent_alert(isolated_database):
    response = evaluate_simulation(build_manual_response(35))

    evaluations = response.observations[0].rule_evaluations
    hr03 = next(item for item in evaluations if item.rule_id == "HR-03")

    assert hr03.outcome == "triggered"

    alerts = alert_store.list_alerts()

    assert len(alerts) == 1
    assert alerts[0]["rule_id"] == "HR-03"
    assert alerts[0]["severity"] == "high_priority"
    assert alerts[0]["status"] == "active"
    assert alerts[0]["source"] == "manual"
    assert alerts[0]["is_demo"] is True


def test_consecutive_rule_waits_for_required_measurements(isolated_database):
    response = evaluate_simulation(build_scenario_response())

    first_day = response.observations[0].rule_evaluations
    second_day = response.observations[1].rule_evaluations

    first_hr01 = next(item for item in first_day if item.rule_id == "HR-01")
    second_hr01 = next(item for item in second_day if item.rule_id == "HR-01")

    assert first_hr01.outcome == "not_evaluable"
    assert second_hr01.outcome == "triggered"

    alerts = alert_store.list_alerts()
    assert any(alert["rule_id"] == "HR-01" for alert in alerts)


def test_alert_is_not_duplicated_for_same_rule_and_simulation(isolated_database):
    measurement_id = alert_store.record_measurement(
        simulation_id="simulation-duplicate-test",
        observation_day=1,
        indicator="heart_rate",
        measurement_type="heart_rate",
        value=35,
        unit="bpm",
        measured_at=datetime.now(timezone.utc).isoformat(),
        source="manual",
        provenance_json=None,
    )

    arguments = {
        "simulation_id": "simulation-duplicate-test",
        "rule_id": "HR-03",
        "measurement_id": measurement_id,
        "indicator": "heart_rate",
        "severity": "high_priority",
        "value": 35,
        "unit": "bpm",
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual",
        "explanation": "Test alert.",
        "reference": "Test reference.",
        "is_demo": True,
    }

    first = alert_store.create_alert(**arguments)
    second = alert_store.create_alert(**arguments)

    assert first["id"] == second["id"]
    assert len(alert_store.list_alerts()) == 1


def test_alert_lifecycle_and_event_history(isolated_database):
    measurement_id = alert_store.record_measurement(
        simulation_id="simulation-lifecycle-test",
        observation_day=1,
        indicator="heart_rate",
        measurement_type="heart_rate",
        value=35,
        unit="bpm",
        measured_at=datetime.now(timezone.utc).isoformat(),
        source="manual",
        provenance_json=None,
    )

    alert = alert_store.create_alert(
        simulation_id="simulation-lifecycle-test",
        rule_id="HR-03",
        measurement_id=measurement_id,
        indicator="heart_rate",
        severity="high_priority",
        value=35,
        unit="bpm",
        measured_at=datetime.now(timezone.utc).isoformat(),
        source="manual",
        explanation="Test alert.",
        reference="Test reference.",
        is_demo=True,
    )

    acknowledged = alert_store.update_alert_status(
        alert["id"], "acknowledged", "Reviewed by operator."
    )
    assert acknowledged["status"] == "acknowledged"
    assert acknowledged["acknowledged_at"] is not None

    resolved = alert_store.update_alert_status(
        alert["id"], "resolved", "Review completed."
    )
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None

    events = alert_store.list_alert_events(alert["id"])
    assert [event["new_status"] for event in events] == [
        "active",
        "acknowledged",
        "resolved",
    ]


def test_resolved_alert_cannot_be_reopened(isolated_database):
    measurement_id = alert_store.record_measurement(
        simulation_id="simulation-transition-test",
        observation_day=1,
        indicator="heart_rate",
        measurement_type="heart_rate",
        value=35,
        unit="bpm",
        measured_at=datetime.now(timezone.utc).isoformat(),
        source="manual",
        provenance_json=None,
    )

    alert = alert_store.create_alert(
        simulation_id="simulation-transition-test",
        rule_id="HR-03",
        measurement_id=measurement_id,
        indicator="heart_rate",
        severity="high_priority",
        value=35,
        unit="bpm",
        measured_at=datetime.now(timezone.utc).isoformat(),
        source="manual",
        explanation="Test alert.",
        reference="Test reference.",
        is_demo=True,
    )

    alert_store.update_alert_status(alert["id"], "resolved")

    with pytest.raises(ValueError, match="Invalid alert transition"):
        alert_store.update_alert_status(alert["id"], "active")
