from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Alert, AlertLevel, AlertStatus
from ..schemas import AlertOut, AlertStatusUpdate
from ..services.measurements import DomainError, get_astronaut

router = APIRouter(prefix="/api", tags=["alertes"])


def _astronaut_or_404(db, code):
    try:
        return get_astronaut(db, code)
    except DomainError as e:
        raise HTTPException(e.status_code, str(e))


def _own_alert(db, alert_id: int, astronaut_code: str) -> Alert:
    a = _astronaut_or_404(db, astronaut_code)
    alert = db.get(Alert, alert_id)
    if alert is None or alert.astronaut_id != a.id:
        raise HTTPException(404, "Alerte introuvable.")
    return alert


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(astronaut_code: str, status: AlertStatus | None = None, level: AlertLevel | None = None,
                db: Session = Depends(get_db)):
    """Historique des alertes d'un astronaute, les plus récentes d'abord."""
    a = _astronaut_or_404(db, astronaut_code)
    q = select(Alert).where(Alert.astronaut_id == a.id)
    if status:
        q = q.where(Alert.status == status)
    if level:
        q = q.where(Alert.level == level)
    return db.scalars(q.order_by(Alert.created_at.desc(), Alert.id.desc())).all()


@router.get("/alerts/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, astronaut_code: str, db: Session = Depends(get_db)):
    return _own_alert(db, alert_id, astronaut_code)


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
def update_alert(alert_id: int, astronaut_code: str, payload: AlertStatusUpdate, db: Session = Depends(get_db)):
    """Change l'état (active → acknowledged → resolved). Une alerte n'est jamais supprimée."""
    alert = _own_alert(db, alert_id, astronaut_code)
    alert.status = payload.status
    alert.resolved_at = datetime.now(timezone.utc) if payload.status == AlertStatus.resolved else None
    db.commit()
    return alert
