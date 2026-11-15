
from datetime import datetime

from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import PhysicalActivityMeasurement
from app.services.generation.context import GenerationContext
from app.services.generation.randomizer import SimulationRandomizer


class PhysicalActivityGenerator:
    """Generate activity duration without fabricating step counts."""

    MAX_PROGRESSIVE_REDUCTION = 0.30
    IRREGULAR_VARIATION = 0.20

    def generate_day(self, context: GenerationContext, day: int,
                     measured_at: datetime,
                     randomizer: SimulationRandomizer) -> MeasurementCollection:
        p = context.parameters
        baseline = float(p["baseline_activity_duration"])
        pattern = p["activity_pattern"]
        days = int(p["simulation_days"])

        if pattern == "progressive_reduction":
            progress = day / days
            duration = baseline * (
                1 - self.MAX_PROGRESSIVE_REDUCTION * progress
            )
        elif pattern == "irregular_activity":
            duration = baseline * (
                1 + randomizer.uniform(
                    -self.IRREGULAR_VARIATION, self.IRREGULAR_VARIATION
                )
            )
        else:
            duration = baseline * randomizer.uniform(0.97, 1.03)

        return MeasurementCollection(
            physical_activity=PhysicalActivityMeasurement(
                duration_minutes=round(max(0.0, duration), 2),
                step_count=None,
                measured_at=measured_at,
                source="simulated",
                provenance={"scenario_id": context.scenario_id.value},
            )
        )
