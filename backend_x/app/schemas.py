from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .models import AlertLevel, AlertStatus, DataSource


class MissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    start_date: datetime
    planned_days: int


class AstronautOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    access_code: str
    last_name: str
    first_name: str
    mission: MissionOut
    mission_day: int | None = None


class AccessRequest(BaseModel):
    code: str = Field(min_length=1, max_length=20)


class IndicatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    label: str
    unit: str
    category: str
    priority: str
    description: str
    normal_min: float | None
    normal_max: float | None
    norm_reference: str | None


class MeasurementCreate(BaseModel):
    astronaut_code: str
    indicator: str
    value: float
    unit: str
    recorded_at: datetime | None = None  # défaut : maintenant
    source: DataSource = DataSource.manual
    source_reference: str | None = None

    @model_validator(mode="after")
    def check_reference(self):
        if self.source == DataSource.public_dataset and not self.source_reference:
            raise ValueError("source_reference est obligatoire pour un public_dataset")
        return self


class MeasurementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    astronaut_id: int
    indicator: str = Field(validation_alias="indicator_code")
    value: float
    unit: str
    recorded_at: datetime
    source: DataSource
    source_reference: str | None
    mission_day: int | None


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    astronaut_id: int
    measurement_id: int
    rule_id: str
    rule_condition: str
    rule_reference: str | None
    rule_is_team_threshold: bool
    indicator_code: str
    level: AlertLevel
    status: AlertStatus
    value: float
    unit: str
    message: str
    recommendation: str
    source: DataSource
    created_at: datetime
    resolved_at: datetime | None


class AlertStatusUpdate(BaseModel):
    status: AlertStatus


class MeasurementResult(BaseModel):
    """Réponse du POST /api/measurements : la mesure enregistrée + les alertes créées."""
    measurement: MeasurementOut
    alerts: list[AlertOut] = []


# ---- Simulation ----
class SimulatedMeasurementRequest(BaseModel):
    astronaut_code: str
    indicator: str
    value: float
    repeat: int = Field(default=2, ge=1, le=10)  # nb de mesures identiques (persistance des règles)


class ScenarioOut(BaseModel):
    name: str
    label: str
    description: str
    expected_level: AlertLevel


class ScenarioRequest(BaseModel):
    astronaut_code: str


class SimulationResult(BaseModel):
    measurements_created: int
    alerts: list[AlertOut]


class ResetRequest(BaseModel):
    astronaut_code: str | None = None  # None = tous les astronautes


class ResetResult(BaseModel):
    measurements_deleted: int
    alerts_deleted: int
