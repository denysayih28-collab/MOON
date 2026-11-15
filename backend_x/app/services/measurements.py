from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Alert, Astronaut, DataSource, Indicator, Measurement
from .alert_engine import evaluate_measurement


class DomainError(Exception):
    status_code = 400


class UnknownAstronaut(DomainError):
    status_code = 404


class UnknownIndicator(DomainError):
    status_code = 422


class InvalidMeasurement(DomainError):
    status_code = 422


def get_astronaut(db: Session, code: str) -> Astronaut:
    a = db.scalar(select(Astronaut).where(Astronaut.access_code == code.strip().upper()))
    if a is None or not a.is_active:
        raise UnknownAstronaut("Identifiant inconnu.")
    return a


def mission_day(astronaut: Astronaut, when: datetime) -> int | None:
    day = (when.date() - astronaut.mission.start_date.date()).days + 1
    return day if day >= 1 else None


def create_measurement(
    db: Session, *, astronaut_code: str, indicator: str, value: float, unit: str,
    recorded_at: datetime | None = None, source: DataSource = DataSource.manual,
    source_reference: str | None = None, injected: bool = False,
) -> tuple[Measurement, list[Alert]]:
    """Valide, enregistre (flush, sans commit) puis évalue les règles."""
    astronaut = get_astronaut(db, astronaut_code)
    ind = db.get(Indicator, indicator)
    if ind is None:
        raise UnknownIndicator(f"Indicateur inconnu : {indicator}")
    if unit != ind.unit:
        raise InvalidMeasurement(f"Unité incompatible pour {indicator} : attendu « {ind.unit} », reçu « {unit} ».")
    if not (ind.min_plausible <= value <= ind.max_plausible):
        raise InvalidMeasurement(
            f"Valeur hors plage plausible pour {indicator} ({ind.min_plausible:g} à {ind.max_plausible:g} {ind.unit})."
        )
    when = recorded_at or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    m = Measurement(
        astronaut_id=astronaut.id, indicator_code=indicator, value=value, unit=unit, recorded_at=when,
        source=source, source_reference=source_reference, mission_day=mission_day(astronaut, when), injected=injected,
    )
    db.add(m)
    db.flush()
    return m, evaluate_measurement(db, m)
