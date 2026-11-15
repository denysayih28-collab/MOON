from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.enums import MeasurementType, ScenarioType
from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import RespirationMeasurement
from app.scenarios.catalog import SCENARIO_CATALOG


class RuleEvaluation(BaseModel):
    """Result of evaluating a simulation rule."""

    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(min_length=1)

    outcome: Literal[
        "triggered",
        "not_triggered",
        "not_evaluable",
    ]

    explanation: str = Field(min_length=1)

    related_measurements: list[MeasurementType] = Field(
        default_factory=list
    )


class SimulationObservation(BaseModel):
    """Measurements and rule evaluations at one simulation time point."""

    model_config = ConfigDict(extra="forbid")

    day: int | None = Field(default=None, ge=1)

    measurements: MeasurementCollection

    rule_evaluations: list[RuleEvaluation] = Field(
        default_factory=list
    )


class SimulationResponse(BaseModel):
    """Standard response returned after a simulation."""

    model_config = ConfigDict(extra="forbid")

    simulation_id: UUID

    simulation_type: Literal["manual", "scenario"]

    scenario_id: ScenarioType | None = None

    mission_phase: str | None = None

    evaluated_at: datetime

    simulation_start_at: datetime | None = None
    effective_seed: int | None = Field(default=None, ge=0)

    observations: list[SimulationObservation] = Field(
        min_length=1
    )

    notices: list[str] = Field(default_factory=list)

    @field_validator("evaluated_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "The evaluation timestamp must include a timezone."
            )

        return value

    @field_validator("simulation_start_at")
    @classmethod
    def validate_simulation_start_timezone(
        cls, value: datetime | None,
    ) -> datetime | None:
        if value is not None and (
            value.tzinfo is None or value.utcoffset() is None
        ):
            raise ValueError(
                "The simulation start timestamp must include a timezone."
            )
        return value

    @model_validator(mode="after")
    def validate_simulation_context(self):
        if self.simulation_type == "manual":
            self._validate_manual_simulation()
        else:
            self._validate_scenario_simulation()

        return self

    def _validate_manual_simulation(self):
        if self.scenario_id is not None:
            raise ValueError(
                "Manual simulations cannot have a scenario_id."
            )

        if self.mission_phase is not None:
            raise ValueError(
                "Manual simulations cannot have a mission_phase."
            )

        if self.simulation_start_at is not None:
            raise ValueError(
                "Manual simulations cannot have a simulation_start_at."
            )

        if self.effective_seed is not None:
            raise ValueError(
                "Manual simulations cannot have an effective_seed."
            )

        if len(self.observations) != 1:
            raise ValueError(
                "Manual simulations must contain exactly one observation."
            )

        observation = self.observations[0]

        if observation.day is not None:
            raise ValueError(
                "Manual observations cannot have a simulation day."
            )

        for measurement in self._get_measurements(
            observation.measurements
        ):
            if measurement.source != "manual":
                raise ValueError(
                    "Manual simulations only accept measurements "
                    "with source='manual'."
                )

    def _validate_scenario_simulation(self):
        if self.scenario_id is None:
            raise ValueError(
                "Scenario simulations require a scenario_id."
            )

        if self.mission_phase is None:
            raise ValueError(
                "Scenario simulations require a mission_phase."
            )

        if self.simulation_start_at is None:
            raise ValueError(
                "Scenario simulations require a simulation_start_at."
            )

        if self.effective_seed is None:
            raise ValueError(
                "Scenario simulations require an effective_seed."
            )

        scenario = SCENARIO_CATALOG[self.scenario_id]

        allowed_phases = {
            phase.phase_id
            for phase in scenario.phases
        }

        if self.mission_phase not in allowed_phases:
            raise ValueError(
                "The selected mission_phase does not belong "
                "to the specified scenario."
            )

        for expected_day, observation in enumerate(
            self.observations,
            start=1,
        ):
            if observation.day != expected_day:
                raise ValueError(
                    "Scenario observation days must start at 1 "
                    "and increase consecutively."
                )

            for measurement in self._get_measurements(
                observation.measurements
            ):
                if measurement.source != "simulated":
                    raise ValueError(
                        "Scenario simulations only accept measurements "
                        "with source='simulated'."
                    )

                if (
                    measurement.provenance is None
                    or measurement.provenance.scenario_id
                    != self.scenario_id.value
                ):
                    raise ValueError(
                        "Every simulated measurement must identify "
                        "the response scenario in its provenance."
                    )

    @staticmethod
    def _get_measurements(measurements: MeasurementCollection):
        """Return individual measurements from a measurement collection."""

        submitted_measurements = []

        for field_name in MeasurementCollection.model_fields:
            measurement = getattr(measurements, field_name)

            if measurement is None:
                continue

            if isinstance(measurement, RespirationMeasurement):
                submitted_measurements.extend(
                    item
                    for item in (
                        measurement.respiratory_rate,
                        measurement.tidal_volume,
                        measurement.minute_ventilation,
                        measurement.alveolar_ventilation,
                    )
                    if item is not None
                )
            else:
                submitted_measurements.append(measurement)

        return submitted_measurements