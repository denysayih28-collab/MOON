"""Moteur d'alertes : évalue une mesure enregistrée contre les règles de son indicateur."""
import operator as _op

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Alert, AlertLevel, AlertRule, AlertStatus, Measurement, Operator

LEVEL_ORDER = {AlertLevel.information: 0, AlertLevel.attention: 1, AlertLevel.high_priority: 2}
_OPS = {Operator.gt: _op.gt, Operator.gte: _op.ge, Operator.lt: _op.lt, Operator.lte: _op.le}


def rule_matches(rule: AlertRule, value: float) -> bool:
    return _OPS[rule.operator](value, rule.threshold)


def evaluate_measurement(db: Session, m: Measurement) -> list[Alert]:
    """Crée (au plus) une alerte : celle de la règle de plus haut niveau déclenchée.

    - Persistance : une règle avec consecutive=N exige que les N dernières mesures de cet
      astronaute pour cet indicateur la satisfassent toutes (réduit les fausses alertes).
    - Pas de doublon : si une alerte active existe déjà pour (astronaute, règle), rien n'est créé.
    """
    rules = db.scalars(
        select(AlertRule).where(AlertRule.indicator_code == m.indicator_code, AlertRule.enabled.is_(True))
    ).all()
    if not rules:
        return []

    window = max(r.consecutive for r in rules)
    recent = db.scalars(
        select(Measurement)
        .where(Measurement.astronaut_id == m.astronaut_id, Measurement.indicator_code == m.indicator_code)
        .order_by(Measurement.recorded_at.desc(), Measurement.id.desc())
        .limit(window)
    ).all()

    triggered = [
        r for r in rules
        if len(recent) >= r.consecutive and all(rule_matches(r, x.value) for x in recent[: r.consecutive])
    ]
    if not triggered:
        return []

    best = max(triggered, key=lambda r: LEVEL_ORDER[r.level])
    already = db.scalar(
        select(Alert.id).where(
            Alert.astronaut_id == m.astronaut_id, Alert.rule_id == best.id, Alert.status == AlertStatus.active
        )
    )
    if already:
        return []

    alert = Alert(
        astronaut_id=m.astronaut_id, measurement_id=m.id, rule_id=best.id, indicator_code=m.indicator_code,
        level=best.level, status=AlertStatus.active, value=m.value, unit=m.unit,
        message=best.message, recommendation=best.recommendation, source=m.source,
    )
    db.add(alert)
    db.flush()
    return [alert]
