from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.enums import (
    ActivityIntensity,
    DataSource,
    MoodLevel,
)
from app.models.provenance import MeasurementProvenance

class MeasurementBase(BaseModel):
    """Base model containing common measurement metadata."""

    model_config = ConfigDict(extra="forbid")

    measured_at: datetime
    source: DataSource
    provenance: MeasurementProvenance | None = None

    @field_validator("measured_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("The timestamp must include a timezone.")
        return value

    @model_validator(mode="after")
    def validate_provenance(self):
        if self.source == DataSource.SIMULATED:
            if (
                self.provenance is None
                or self.provenance.scenario_id is None
            ):
                raise ValueError(
                    "A simulated measurement must identify its scenario."
                )

        elif self.source == DataSource.SCIENTIFIC_DATASET:
            if (
                self.provenance is None
                or self.provenance.dataset_name is None
                or self.provenance.source_reference is None
            ):
                raise ValueError(
                    "A scientific measurement must identify its dataset "
                    "and source reference."
                )

        return self

class HeartRateMeasurement(MeasurementBase):
    value: float = Field(ge=0)
    unit: Literal["bpm"] = "bpm"


class BloodPressureMeasurement(MeasurementBase):
    systolic: float = Field(ge=0)
    diastolic: float = Field(ge=0)
    unit: Literal["mmHg"] = "mmHg"


class BloodGlucoseMeasurement(MeasurementBase):
    value: float = Field(ge=0)
    unit: Literal["mg/dL", "mmol/L"]


class BodyTemperatureMeasurement(MeasurementBase):
    value: float
    unit: Literal["°C"] = "°C"


class SleepMeasurement(MeasurementBase):
    duration_hours: float = Field(ge=0)


class MoodMeasurement(MeasurementBase):
    value: MoodLevel


class RespiratoryRateMeasurement(MeasurementBase):
    value: float = Field(ge=0)
    unit: Literal["breaths/min"] = "breaths/min"


class TidalVolumeMeasurement(MeasurementBase):
    value: float = Field(ge=0)
    unit: Literal["mL"] = "mL"


class MinuteVentilationMeasurement(MeasurementBase):
    value: float = Field(ge=0)
    unit: Literal["L/min"] = "L/min"


class AlveolarVentilationMeasurement(MeasurementBase):
    """Educational alveolar ventilation calculated from explicit inputs."""

    value: float = Field(ge=0)
    unit: Literal["L/min"] = "L/min"


class RespirationMeasurement(BaseModel):
    """A record containing up to four respiratory measurements."""

    model_config = ConfigDict(extra="forbid")

    respiratory_rate: RespiratoryRateMeasurement | None = None
    tidal_volume: TidalVolumeMeasurement | None = None
    minute_ventilation: MinuteVentilationMeasurement | None = None
    alveolar_ventilation: AlveolarVentilationMeasurement | None = None

    @model_validator(mode="after")
    def validate_at_least_one_measurement(self):
        measurements = (
            self.respiratory_rate,
            self.tidal_volume,
            self.minute_ventilation,
            self.alveolar_ventilation,
        )

        if all(measurement is None for measurement in measurements):
            raise ValueError(
                "A respiratory record must contain at least one measurement."
            )

        return self


class OxygenSaturationMeasurement(MeasurementBase):
    value: float = Field(ge=0, le=100)
    unit: Literal["%"] = "%"


class PhysicalActivityMeasurement(MeasurementBase):
    duration_minutes: float = Field(ge=0)
    step_count: int | None = Field(default=None, ge=0)
    intensity: ActivityIntensity | None = None

class FluidIntakeMeasurement(MeasurementBase):
    """Fluid intake recorded over a defined observation period."""

    value_ml: float = Field(ge=0)
    period_hours: float = Field(gt=0)

    unit: Literal["mL"] = "mL"