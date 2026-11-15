from pydantic import BaseModel, ConfigDict, model_validator

from app.models.measurements import (
    BloodGlucoseMeasurement,
    BloodPressureMeasurement,
    BodyTemperatureMeasurement,
    FluidIntakeMeasurement,
    HeartRateMeasurement,
    MoodMeasurement,
    OxygenSaturationMeasurement,
    PhysicalActivityMeasurement,
    RespirationMeasurement,
    SleepMeasurement,
)


class MeasurementCollection(BaseModel):
    """Collection of measurements that can be partially populated."""

    model_config = ConfigDict(extra="forbid")

    heart_rate: HeartRateMeasurement | None = None
    blood_pressure: BloodPressureMeasurement | None = None
    blood_glucose: BloodGlucoseMeasurement | None = None
    body_temperature: BodyTemperatureMeasurement | None = None
    sleep: SleepMeasurement | None = None
    mood: MoodMeasurement | None = None
    respiration: RespirationMeasurement | None = None
    oxygen_saturation: OxygenSaturationMeasurement | None = None
    physical_activity: PhysicalActivityMeasurement | None = None
    fluid_intake: FluidIntakeMeasurement | None = None

    @model_validator(mode="after")
    def validate_at_least_one_measurement(self):
        if not any(
            getattr(self, field_name) is not None
            for field_name in self.__class__.model_fields
        ):
            raise ValueError(
                "The collection must contain at least one measurement."
            )

        return self