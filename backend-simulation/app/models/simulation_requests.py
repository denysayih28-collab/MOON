from datetime import datetime
from math import isfinite
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.enums import DataSource, ScenarioType
from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import RespirationMeasurement
from app.scenarios.catalog import SCENARIO_CATALOG, ScenarioParameter
from app.scenarios.constants import RESPIRATORY_RELATIVE_VARIATION


class ManualSimulationRequest(BaseModel):
    """Request payload for a user-defined manual simulation."""

    model_config = ConfigDict(extra="forbid")

    measurements: MeasurementCollection

    @model_validator(mode="after")
    def validate_measurement_sources(self):
        submitted_measurements = []

        for field_name in MeasurementCollection.model_fields:
            measurement = getattr(self.measurements, field_name)

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

        if any(
            measurement.source != DataSource.MANUAL
            for measurement in submitted_measurements
        ):
            raise ValueError(
                "Manual simulation only accepts measurements "
                "with source='manual'."
            )

        return self


class ScenarioSimulationRequest(BaseModel):
    """Request payload for a predefined scenario simulation."""

    model_config = ConfigDict(extra="forbid")

    scenario_id: ScenarioType
    mission_phase: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    seed: int | None = Field(default=None, ge=0)
    simulation_start_at: datetime | None = None

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
    def validate_scenario_configuration(self):
        scenario = SCENARIO_CATALOG[self.scenario_id]

        self._validate_mission_phase(scenario.phases)
        self._validate_parameters(scenario.parameters)

        if self.scenario_id == ScenarioType.RESPIRATORY_VARIATION:
            self._validate_respiratory_parameters()

        return self

    def _validate_respiratory_parameters(self):
        dead_space = self.parameters.get("dead_space_volume_ml")

        if dead_space is None:
            return

        baseline_tidal_volume = self.parameters["baseline_tidal_volume_ml"]

        minimum_generated_tidal_volume = round(
            baseline_tidal_volume * (1 - RESPIRATORY_RELATIVE_VARIATION),
            2,
        )

        if dead_space > minimum_generated_tidal_volume:
            raise ValueError(
                "Parameter 'dead_space_volume_ml' cannot exceed the "
                "minimum generated tidal volume "
                f"({minimum_generated_tidal_volume} mL)."
            )

    def _validate_mission_phase(self, phases):
        allowed_phases = {phase.phase_id for phase in phases}

        if self.mission_phase not in allowed_phases:
            raise ValueError(
                "The selected mission_phase does not belong "
                "to the specified scenario."
            )

    def _validate_parameters(
        self,
        parameter_definitions: tuple[ScenarioParameter, ...],
    ):
        definitions = {
            parameter.parameter_id: parameter
            for parameter in parameter_definitions
        }

        unknown_parameters = set(self.parameters) - set(definitions)

        if unknown_parameters:
            names = ", ".join(sorted(unknown_parameters))
            raise ValueError(f"Unknown scenario parameters: {names}.")

        for parameter_id, definition in definitions.items():
            if parameter_id not in self.parameters:
                if definition.default_value is not None:
                    self.parameters[parameter_id] = definition.default_value
                elif definition.required:
                    raise ValueError(
                        f"Missing required scenario parameter: "
                        f"{parameter_id}."
                    )
                else:
                    continue

            self._validate_parameter_value(
                definition,
                self.parameters[parameter_id],
            )

    @staticmethod
    def _validate_parameter_value(
        definition: ScenarioParameter,
        value: Any,
    ):
        parameter_id = definition.parameter_id
        value_type = definition.value_type

        if value_type == "integer":
            valid_type = type(value) is int

        elif value_type == "number":
            valid_type = (
                type(value) in (int, float)
                and isfinite(value)
            )

        elif value_type == "boolean":
            valid_type = type(value) is bool

        elif value_type in ("string", "enum"):
            valid_type = isinstance(value, str)

        else:
            raise ValueError(
                f"Unsupported parameter type '{value_type}' "
                f"for '{parameter_id}'."
            )

        if not valid_type:
            raise ValueError(
                f"Parameter '{parameter_id}' must have type "
                f"'{value_type}'."
            )

        if value_type == "enum" and value not in definition.allowed_values:
            allowed = ", ".join(definition.allowed_values)
            raise ValueError(
                f"Parameter '{parameter_id}' must be one of: {allowed}."
            )

        if value_type in ("integer", "number"):
            if definition.minimum is not None and value < definition.minimum:
                raise ValueError(
                    f"Parameter '{parameter_id}' must be at least "
                    f"{definition.minimum}."
                )

            if definition.maximum is not None and value > definition.maximum:
                raise ValueError(
                    f"Parameter '{parameter_id}' must be at most "
                    f"{definition.maximum}."
                )
