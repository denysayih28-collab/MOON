from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AccessRequest, AstronautOut
from ..services.measurements import DomainError, get_astronaut, mission_day

router = APIRouter(prefix="/api", tags=["astronautes"])


def build_out(a) -> AstronautOut:
    out = AstronautOut.model_validate(a)
    out.mission_day = mission_day(a, datetime.now(timezone.utc))
    return out


@router.post("/access", response_model=AstronautOut)
def access(payload: AccessRequest, db: Session = Depends(get_db)):
    """Connexion par identifiant seul : renvoie le profil si l'ID existe."""
    try:
        return build_out(get_astronaut(db, payload.code))
    except DomainError as e:
        raise HTTPException(e.status_code, str(e))
