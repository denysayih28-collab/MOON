"""Rule evaluation and persistence for simulation observations."""

import json

from app.models.enums import MeasurementType
from app.models.measurements import RespirationMeasurement
from app.models.simulation_responses import RuleEvaluation
from app.rules.catalog import (
    REFERENCE,
    RULES_BY_INDICATOR,
    SEVERITY_ORDER,
)
from app.services import alert_store


OPERATORS = {
    "<": lambda value, threshold: value < threshold,
    "<=": lambda value, threshold: value <= threshold,
    ">": lambda value, threshold: value > threshold,
    ">=": lambda value, threshold: value >= threshold,
}

MOOD_SCORE = {
    "very_low": 1,
    "low": 2,
    "neutral": 3,
    "good": 4,
    "very_good": 5,
}


def _measurement_record(measurement, indicator, measurement_type, value, unit):
    provenance = (
        measurement.provenance.model_dump(mode="json")
        if measurement.provenance is not None
        else None
    )
    return {
        "indicator": indicator,
        "measurement_type": measurement_type,
        "value": float(value),
        "unit": unit,
        "measured_at": measurement.measured_at.isoformat(),
        "source": measurement.source.value,
        "provenance_json": json.dumps(provenance) if provenance else None,
    }


def extract_measurements(collection):
    records = []

    def add(measurement, indicator, measurement_type, value, unit):
        if measurement is not None and value is not None:
            records.append(
                _measurement_record(
                    measurement, indicator, measurement_type, value, unit
                )
            )

    add(collection.heart_rate, "heart_rate", "heart_rate",
        collection.heart_rate.value if collection.heart_rate else None, "bpm")

    if collection.blood_pressure is not None:
        bp = collection.blood_pressure
        add(bp, "blood_pressure_systolic", "blood_pressure", bp.systolic, "mmHg")
        add(bp, "blood_pressure_diastolic", "blood_pressure", bp.diastolic, "mmHg")

    add(collection.blood_glucose, "blood_glucose", "blood_glucose",
        collection.blood_glucose.value if collection.blood_glucose else None,
        collection.blood_glucose.unit if collection.blood_glucose else "")

    add(collection.body_temperature, "body_temperature", "body_temperature",
        collection.body_temperature.value if collection.body_temperature else None, "°C")

    add(collection.sleep, "sleep", "sleep",
        collection.sleep.duration_hours if collection.sleep else None, "h")

    if collection.mood is not None:
        mood_value = collection.mood.value.value
        add(collection.mood, "mood", "mood", MOOD_SCORE[mood_value], "ordinal_1_to_5")

    if collection.respiration is not None:
        respiration = collection.respiration
        add(respiration.respiratory_rate, "respiratory_rate", "respiratory_rate",
            respiration.respiratory_rate.value if respiration.respiratory_rate else None,
            "breaths/min")
        add(respiration.tidal_volume, "tidal_volume", "tidal_volume",
            respiration.tidal_volume.value if respiration.tidal_volume else None, "mL")
        add(respiration.minute_ventilation, "minute_ventilation", "minute_ventilation",
            respiration.minute_ventilation.value if respiration.minute_ventilation else None,
            "L/min")
        add(respiration.alveolar_ventilation, "alveolar_ventilation",
            "alveolar_ventilation",
            respiration.alveolar_ventilation.value
            if respiration.alveolar_ventilation else None,
            "L/min")

    add(collection.oxygen_saturation, "oxygen_saturation", "oxygen_saturation",
        collection.oxygen_saturation.value if collection.oxygen_saturation else None, "%")

    if collection.physical_activity is not None:
        activity = collection.physical_activity
        add(activity, "activity_duration", "physical_activity",
            activity.duration_minutes, "min")
        if activity.step_count is not None:
            add(activity, "activity_steps", "physical_activity",
                activity.step_count, "steps")

    if collection.fluid_intake is not None:
        add(collection.fluid_intake, "fluid_intake", "fluid_intake",
            collection.fluid_intake.value_ml, "mL")

    return records


def evaluate_simulation(response):
    """Persist measurements, evaluate rules, and attach evaluations to observations."""

    alert_store.init_db()

    for observation in response.observations:
        current_records = {}

        for record in extract_measurements(observation.measurements):
            measurement_id = alert_store.record_measurement(
                simulation_id=response.simulation_id,
                observation_day=observation.day,
                **record,
            )
            current_records[record["indicator"]] = {
                **record,
                "measurement_id": measurement_id,
            }

        evaluations = []
        triggered_by_indicator = {}

        for indicator, current in current_records.items():
            rules = RULES_BY_INDICATOR.get(indicator, [])

            for rule in rules:
                recent_values = alert_store.get_recent_values(
                    response.simulation_id,
                    indicator,
                    current["source"],
                    rule.consecutive,
                )

                if len(recent_values) < rule.consecutive:
                    outcome = "not_evaluable"
                    explanation = (
                        f"Historique insuffisant : {len(recent_values)} "
                        f"mesure(s) disponible(s), {rule.consecutive} requise(s)."
                    )
                else:
                    matched = all(
                        OPERATORS[rule.operator](value, rule.threshold)
                        for value in recent_values
                    )
                    outcome = "triggered" if matched else "not_triggered"
                    explanation = (
                        f"{current['value']} {current['unit']} ; "
                        f"condition {rule.operator} {rule.threshold} ; "
                        f"{rule.consecutive} mesure(s) consécutive(s)."
                    )

                evaluations.append(
                    RuleEvaluation(
                        rule_id=rule.rule_id,
                        outcome=outcome,
                        explanation=explanation,
                        related_measurements=[
                            MeasurementType(rule.measurement_type)
                        ],
                    )
                )

                if outcome == "triggered":
                    triggered_by_indicator.setdefault(indicator, []).append(rule)

        # One alert per indicator and observation: keep the highest severity.
        for indicator, triggered_rules in triggered_by_indicator.items():
            selected_rule = max(
                triggered_rules,
                key=lambda item: (
                    SEVERITY_ORDER[item.severity],
                    item.rule_id,
                ),
            )
            current = current_records[indicator]

            alert_store.create_alert(
                simulation_id=response.simulation_id,
                rule_id=selected_rule.rule_id,
                measurement_id=current["measurement_id"],
                indicator=indicator,
                severity=selected_rule.severity,
                value=current["value"],
                unit=current["unit"],
                measured_at=current["measured_at"],
                source=current["source"],
                explanation=(
                    f"{selected_rule.message} "
                    f"Valeur observée : {current['value']} {current['unit']}. "
                    f"Source : {current['source']}."
                ),
                reference=selected_rule.reference or REFERENCE,
                is_demo=selected_rule.is_demo,
            )

        observation.rule_evaluations = evaluations

    return response
