from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Indicator, Measurement
from ..schemas import MeasurementCreate, MeasurementOut, MeasurementResult
from ..services.measurements import DomainError, create_measurement, get_astronaut

router = APIRouter(prefix="/api", tags=["mesures"])


def _astronaut_or_404(db, code):
    try:
        return get_astronaut(db, code)
    except DomainError as e:
        raise HTTPException(e.status_code, str(e))


@router.get("/measurements", response_model=list[MeasurementOut])
def list_measurements(
    astronaut_code: str, indicator: str | None = None, since: datetime | None = None,
    until: datetime | None = None, limit: int = Query(500, ge=1, le=2000), db: Session = Depends(get_db),
):
    """Historique d'un astronaute (ordre chronologique), filtrable par indicateur et période."""
    a = _astronaut_or_404(db, astronaut_code)
    q = select(Measurement).where(Measurement.astronaut_id == a.id)
    if indicator:
        q = q.where(Measurement.indicator_code == indicator)
    if since:
        q = q.where(Measurement.recorded_at >= since)
    if until:
        q = q.where(Measurement.recorded_at <= until)
    # les `limit` plus récentes, renvoyées dans l'ordre chronologique
    rows = db.scalars(q.order_by(Measurement.recorded_at.desc(), Measurement.id.desc()).limit(limit)).all()
    return list(reversed(rows))


@router.get("/measurements/latest", response_model=list[MeasurementOut])
def latest_measurements(astronaut_code: str, db: Session = Depends(get_db)):
    """Dernière mesure de chaque indicateur (cartes du tableau de bord)."""
    a = _astronaut_or_404(db, astronaut_code)
    out = []
    for code in db.scalars(select(Indicator.code).order_by(Indicator.code)):
        m = db.scalar(
            select(Measurement)
            .where(Measurement.astronaut_id == a.id, Measurement.indicator_code == code)
            .order_by(Measurement.recorded_at.desc(), Measurement.id.desc()).limit(1)
        )
        if m:
            out.append(m)
    return out


@router.post("/measurements", response_model=MeasurementResult, status_code=201)
def post_measurement(payload: MeasurementCreate, db: Session = Depends(get_db)):
    """Valide, enregistre, évalue les règles, puis renvoie la mesure et les alertes créées."""
    try:
        m, alerts = create_measurement(
            db, astronaut_code=payload.astronaut_code, indicator=payload.indicator, value=payload.value,
            unit=payload.unit, recorded_at=payload.recorded_at, source=payload.source,
            source_reference=payload.source_reference,
        )
    except DomainError as e:
        db.rollback()
        raise HTTPException(e.status_code, str(e))
    db.commit()
    return MeasurementResult(measurement=MeasurementOut.model_validate(m),
                             alerts=[a for a in alerts])
