
from datetime import datetime

from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import SleepMeasurement
from app.services.generation.context import GenerationContext
from app.services.generation.randomizer import SimulationRandomizer


class SleepGenerator:
    """Generate educational sleep-duration observations."""

    def generate_day(self, context: GenerationContext, day: int,
                     measured_at: datetime,
                     randomizer: SimulationRandomizer) -> MeasurementCollection:
        p = context.parameters
        baseline = float(p["baseline_sleep_hours"])
        target = float(p["sleep_duration_hours"])
        pattern = p["sleep_pattern"]
        days = int(p["simulation_days"])

        if pattern == "progressive_reduction":
            progress = day / days
            duration = baseline + (target - baseline) * progress
            duration += randomizer.uniform(-0.15, 0.15)
        elif pattern == "irregular_sleep":
            duration = target + randomizer.uniform(-0.75, 0.75)
        else:
            duration = target + randomizer.uniform(-0.15, 0.15)

        return MeasurementCollection(
            sleep=SleepMeasurement(
                duration_hours=round(max(0.0, duration), 2),
                measured_at=measured_at,
                source="simulated",
                provenance={"scenario_id": context.scenario_id.value},
            )
        )
