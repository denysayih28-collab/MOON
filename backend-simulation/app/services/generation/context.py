"""Immutable context shared by scenario generators."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from types import MappingProxyType
from typing import Any, Mapping

from app.models.enums import ScenarioType


@dataclass(frozen=True, slots=True)
class GenerationContext:
    scenario_id: ScenarioType
    mission_phase: str
    parameters: Mapping[str, Any]
    simulation_start_at: datetime
    effective_seed: int

    def __post_init__(self):
        if (
            self.simulation_start_at.tzinfo is None
            or self.simulation_start_at.utcoffset() is None
        ):
            raise ValueError(
                "The simulation start timestamp must include a timezone."
            )

        if self.effective_seed < 0:
            raise ValueError("The effective seed cannot be negative.")

        object.__setattr__(
            self,
            "parameters",
            MappingProxyType(dict(self.parameters)),
        )

    def timestamp_for_day(self, day: int) -> datetime:
        if day < 1:
            raise ValueError("Simulation days must start at 1.")

        start_utc = self.simulation_start_at.astimezone(timezone.utc)

        return start_utc + timedelta(days=day - 1)
