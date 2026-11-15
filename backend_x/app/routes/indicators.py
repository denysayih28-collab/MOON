from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Indicator
from ..schemas import IndicatorOut

router = APIRouter(prefix="/api", tags=["indicateurs"])


@router.get("/indicators", response_model=list[IndicatorOut])
def list_indicators(db: Session = Depends(get_db)):
    return db.scalars(select(Indicator).order_by(Indicator.priority, Indicator.code)).all()
