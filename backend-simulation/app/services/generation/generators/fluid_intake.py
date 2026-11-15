
from datetime import datetime

from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import FluidIntakeMeasurement
from app.services.generation.context import GenerationContext
from app.services.generation.randomizer import SimulationRandomizer


class FluidIntakeGenerator:
    """Generate fluid intake without inferring hydration status."""

    MAX_PROGRESSIVE_REDUCTION = 0.30
    IRREGULAR_VARIATION = 0.20

    def generate_day(self, context: GenerationContext, day: int,
                     measured_at: datetime,
                     randomizer: SimulationRandomizer) -> MeasurementCollection:
        p = context.parameters
        baseline = float(p["baseline_fluid_intake_ml"])
        pattern = p["intake_pattern"]
        days = int(p["simulation_days"])

        if pattern == "progressive_reduction":
            progress = day / days
            intake = baseline * (1 - self.MAX_PROGRESSIVE_REDUCTION * progress)
        elif pattern == "irregular_intake":
            intake = baseline * (
                1 + randomizer.uniform(
                    -self.IRREGULAR_VARIATION, self.IRREGULAR_VARIATION
                )
            )
        else:
            intake = baseline * randomizer.uniform(0.97, 1.03)

        return MeasurementCollection(
            fluid_intake=FluidIntakeMeasurement(
                value_ml=round(max(0.0, intake), 1),
                period_hours=24,
                measured_at=measured_at,
                source="simulated",
                provenance={"scenario_id": context.scenario_id.value},
            )
        )
