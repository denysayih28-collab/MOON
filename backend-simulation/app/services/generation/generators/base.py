"""Common interface for scenario-specific generators."""

from datetime import datetime
from typing import Protocol

from app.models.measurement_collection import MeasurementCollection
from app.services.generation.context import GenerationContext
from app.services.generation.randomizer import SimulationRandomizer


class ScenarioGenerator(Protocol):
    def generate_day(
        self,
        context: GenerationContext,
        day: int,
        measured_at: datetime,
        randomizer: SimulationRandomizer,
    ) -> MeasurementCollection:
        """Generate the measurements for one simulation day."""
        ...
