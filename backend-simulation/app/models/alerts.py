from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class AlertStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: AlertStatus
    note: str | None = Field(default=None, max_length=500)


class AlertOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    measurement_id: int
    simulation_id: str
    rule_id: str
    indicator: str
    severity: str
    status: AlertStatus
    value: float
    unit: str
    measured_at: datetime
    source: str
    explanation: str
    reference: str
    is_demo: bool
    created_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None


class AlertEventOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    alert_id: int
    previous_status: str | None
    new_status: str
    changed_at: datetime
    note: str | None = None


class AlertRuleOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str
    indicator: str
    measurement_type: str
    operator: str
    threshold: float
    consecutive: int
    severity: str
    message: str
    reference: str
    is_demo: bool
    enabled: bool
