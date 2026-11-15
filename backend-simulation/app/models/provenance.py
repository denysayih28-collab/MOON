from pydantic import BaseModel, ConfigDict, Field


class MeasurementProvenance(BaseModel):
    """Metadata used to identify the origin of a measurement."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: str | None = Field(default=None, min_length=1)
    dataset_name: str | None = Field(default=None, min_length=1)
    dataset_id: str | None = Field(default=None, min_length=1)
    study_name: str | None = Field(default=None, min_length=1)
    source_reference: str | None = Field(default=None, min_length=1)
    derivation: str | None = Field(default=None, min_length=1)
    input_measurements: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
