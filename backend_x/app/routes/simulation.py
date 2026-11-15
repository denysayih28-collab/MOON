"""Panneau de simulation (mode opérateur). Protégé par l'en-tête X-Operator-Key."""
import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Astronaut
from ..schemas import (AstronautOut, ResetRequest, ResetResult, ScenarioOut, ScenarioRequest,
                       SimulatedMeasurementRequest, SimulationResult)
from ..services import simulation as sim
from ..models import Indicator
from ..services.measurements import DomainError
from .astronauts import build_out


def require_operator(x_operator_key: str | None = Header(default=None)):
    expected = os.environ.get("MOON_OPERATOR_KEY", "moon-operator")
    if not x_operator_key or not secrets.compare_digest(x_operator_key, expected):
        raise HTTPException(401, "Clé opérateur manquante ou invalide.")


router = APIRouter(prefix="/api/simulation", tags=["simulation"], dependencies=[Depends(require_operator)])


@router.get("/astronauts", response_model=list[AstronautOut])
def list_astronauts(db: Session = Depends(get_db)):
    return [build_out(a) for a in db.scalars(select(Astronaut).order_by(Astronaut.id))]


@router.get("/scenarios", response_model=list[ScenarioOut])
def list_scenarios():
    return [ScenarioOut(name=n, label=s[0], description=s[1], expected_level=s[2]) for n, s in sim.SCENARIOS.items()]


@router.post("/scenarios/{name}", response_model=SimulationResult)
def run_scenario(name: str, payload: ScenarioRequest, db: Session = Depends(get_db)):
    if name not in sim.SCENARIOS:
        raise HTTPException(404, f"Scénario inconnu : {name}")
    try:
        n, alerts = sim.run_scenario(db, name, payload.astronaut_code)
    except DomainError as e:
        db.rollback()
        raise HTTPException(e.status_code, str(e))
    db.commit()
    return SimulationResult(measurements_created=n, alerts=alerts)


@router.post("/measurements", response_model=SimulationResult)
def send_measurement(payload: SimulatedMeasurementRequest, db: Session = Depends(get_db)):
    """Envoie une valeur libre (répétée `repeat` fois) pour un astronaute et un indicateur."""
    ind = db.get(Indicator, payload.indicator)
    if ind is None:
        raise HTTPException(422, f"Indicateur inconnu : {payload.indicator}")
    try:
        n, alerts = sim.send_simulated(db, payload.astronaut_code, payload.indicator, ind.unit,
                                       payload.value, payload.repeat)
    except DomainError as e:
        db.rollback()
        raise HTTPException(e.status_code, str(e))
    db.commit()
    return SimulationResult(measurements_created=n, alerts=alerts)


@router.post("/reset", response_model=ResetResult)
def reset(payload: ResetRequest, db: Session = Depends(get_db)):
    """Retire les mesures et alertes créées par la simulation ; les données de départ restent."""
    try:
        m, a = sim.reset(db, payload.astronaut_code)
    except DomainError as e:
        raise HTTPException(e.status_code, str(e))
    db.commit()
    return ResetResult(measurements_deleted=m, alerts_deleted=a)
