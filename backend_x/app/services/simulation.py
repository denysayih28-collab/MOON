"""Scénarios de démonstration : envoient des mesures `simulated` qui déclenchent des alertes."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..models import Alert, AlertLevel, DataSource, Measurement
from .measurements import create_measurement, get_astronaut

# nom -> (libellé, description, niveau attendu, [(indicateur, unité, valeur, nb de mesures)])
SCENARIOS = {
    "tachycardia": ("Tachycardie", "FC 110 bpm sur 2 mesures", AlertLevel.attention,
                    [("heart_rate", "bpm", 110, 2)]),
    "tachycardia_severe": ("Tachycardie sévère", "FC 135 bpm", AlertLevel.high_priority,
                           [("heart_rate", "bpm", 135, 1)]),
    "hypoxia": ("Hypoxie", "SpO2 92 % sur 2 mesures", AlertLevel.attention,
                [("spo2", "%", 92, 2)]),
    "hypoxia_severe": ("Hypoxie sévère", "SpO2 88 %", AlertLevel.high_priority,
                       [("spo2", "%", 88, 1)]),
    "fever": ("Fièvre", "38,3 °C sur 2 mesures", AlertLevel.attention,
              [("body_temperature", "°C", 38.3, 2)]),
    "fever_high": ("Forte fièvre", "39,6 °C", AlertLevel.high_priority,
                   [("body_temperature", "°C", 39.6, 1)]),
    "hypertension": ("Hypertension", "145/95 mmHg sur 2 mesures", AlertLevel.attention,
                     [("blood_pressure_systolic", "mmHg", 145, 2), ("blood_pressure_diastolic", "mmHg", 95, 2)]),
    "hypertensive_crisis": ("Crise hypertensive", "185/125 mmHg", AlertLevel.high_priority,
                            [("blood_pressure_systolic", "mmHg", 185, 1), ("blood_pressure_diastolic", "mmHg", 125, 1)]),
    "sleep_deprivation": ("Manque de sommeil", "5 h de sommeil", AlertLevel.attention,
                          [("sleep_duration", "h", 5, 1)]),
    "low_mood": ("Humeur basse", "Humeur 2/5 sur 3 entrées consécutives", AlertLevel.attention,
                 [("mood", "score/5", 2, 3)]),
}


def send_simulated(db: Session, astronaut_code: str, indicator: str, unit: str, value: float, repeat: int):
    """Envoie `repeat` mesures espacées d'une minute, la dernière étant 'maintenant'."""
    now = datetime.now(timezone.utc)
    created, alerts = 0, []
    for i in range(repeat):
        when = now - timedelta(minutes=repeat - 1 - i)
        _, new_alerts = create_measurement(
            db, astronaut_code=astronaut_code, indicator=indicator, value=value, unit=unit,
            recorded_at=when, source=DataSource.simulated, injected=True,
        )
        created += 1
        alerts.extend(new_alerts)
    return created, alerts


def run_scenario(db: Session, name: str, astronaut_code: str):
    label, _desc, _lvl, steps = SCENARIOS[name]
    total, alerts = 0, []
    for indicator, unit, value, repeat in steps:
        n, new_alerts = send_simulated(db, astronaut_code, indicator, unit, value, repeat)
        total += n
        alerts.extend(new_alerts)
    return total, alerts


def reset(db: Session, astronaut_code: str | None):
    """Supprime les mesures injectées par la simulation et les alertes qui en découlent."""
    q = select(Measurement.id).where(Measurement.injected.is_(True))
    if astronaut_code:
        q = q.where(Measurement.astronaut_id == get_astronaut(db, astronaut_code).id)
    ids = list(db.scalars(q))
    if not ids:
        return 0, 0
    a = db.execute(delete(Alert).where(Alert.measurement_id.in_(ids))).rowcount
    m = db.execute(delete(Measurement).where(Measurement.id.in_(ids))).rowcount
    return m, a
