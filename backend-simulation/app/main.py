from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query

from app.models.alerts import (
    AlertEventOut,
    AlertOut,
    AlertRuleOut,
    AlertStatus,
    AlertStatusUpdate,
)
from app.models.simulation_requests import (
    ManualSimulationRequest,
    ScenarioSimulationRequest,
)
from app.models.simulation_responses import (
    SimulationObservation,
    SimulationResponse,
)
from app.rules.catalog import RULES
from app.rules.engine import evaluate_simulation
from app.services import alert_store
from app.services.generation.registry import build_default_generation_engine


app = FastAPI(
    title="M.O.O.N. Simulation API",
    description=(
        "API de simulation, d'évaluation de règles et de gestion "
        "des alertes du prototype M.O.O.N."
    ),
    version="0.2.0",
)

generation_engine = build_default_generation_engine()
alert_store.init_db()


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "service": "moon-simulation-api",
    }


@app.post(
    "/api/simulations/manual",
    response_model=SimulationResponse,
    tags=["Simulations"],
)
def create_manual_simulation(request: ManualSimulationRequest):
    response = SimulationResponse(
        simulation_id=uuid4(),
        simulation_type="manual",
        evaluated_at=datetime.now(timezone.utc),
        observations=[
            SimulationObservation(measurements=request.measurements)
        ],
    )
    return evaluate_simulation(response)


@app.post(
    "/api/simulations/scenarios",
    response_model=SimulationResponse,
    tags=["Simulations"],
)
def create_scenario_simulation(request: ScenarioSimulationRequest):
    result = generation_engine.generate(request)

    response = SimulationResponse(
        simulation_id=uuid4(),
        simulation_type="scenario",
        scenario_id=request.scenario_id,
        mission_phase=request.mission_phase,
        evaluated_at=datetime.now(timezone.utc),
        simulation_start_at=result.simulation_start_at,
        effective_seed=result.effective_seed,
        observations=result.observations,
        notices=result.notices,
    )
    return evaluate_simulation(response)


@app.get(
    "/api/rules",
    response_model=list[AlertRuleOut],
    tags=["Rules"],
)
def list_rules():
    return [asdict(rule) for rule in RULES]


@app.get(
    "/api/alerts",
    response_model=list[AlertOut],
    tags=["Alerts"],
)
def list_alerts(
    status: AlertStatus | None = Query(default=None),
    simulation_id: str | None = Query(default=None),
):
    return alert_store.list_alerts(
        status=status.value if status else None,
        simulation_id=simulation_id,
    )


@app.get(
    "/api/alerts/{alert_id}",
    response_model=AlertOut,
    tags=["Alerts"],
)
def get_alert(alert_id: int):
    alert = alert_store.get_alert(alert_id)

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    return alert


@app.get(
    "/api/alerts/{alert_id}/events",
    response_model=list[AlertEventOut],
    tags=["Alerts"],
)
def get_alert_events(alert_id: int):
    if alert_store.get_alert(alert_id) is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    return alert_store.list_alert_events(alert_id)


@app.patch(
    "/api/alerts/{alert_id}",
    response_model=AlertOut,
    tags=["Alerts"],
)
def change_alert_status(
    alert_id: int,
    request: AlertStatusUpdate,
):
    try:
        alert = alert_store.update_alert_status(
            alert_id,
            request.status.value,
            request.note,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    return alert
