
from datetime import datetime

from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import (
    BloodPressureMeasurement,
    HeartRateMeasurement,
)
from app.services.generation.context import GenerationContext
from app.services.generation.randomizer import SimulationRandomizer


class CardiovascularGenerator:
    """Generate cardiovascular measurements from explicit baselines."""

    RELATIVE_VARIATION = 0.03

    def generate_day(self, context: GenerationContext, day: int,
                     measured_at: datetime,
                     randomizer: SimulationRandomizer) -> MeasurementCollection:
        p = context.parameters
        hr_base = p.get("baseline_heart_rate")
        sys_base = p.get("baseline_systolic_pressure")
        dia_base = p.get("baseline_diastolic_pressure")

        if (sys_base is None) != (dia_base is None):
            raise ValueError(
                "Both systolic and diastolic baselines must be provided together."
            )

        if hr_base is None and sys_base is None:
            raise ValueError(
                "Cardiovascular simulation requires a heart-rate baseline "
                "or both blood-pressure baselines."
            )

        provenance = {"scenario_id": context.scenario_id.value}
        heart_rate = None
        blood_pressure = None

        if hr_base is not None:
            factor = 1 + randomizer.uniform(
                -self.RELATIVE_VARIATION, self.RELATIVE_VARIATION
            )
            heart_rate = HeartRateMeasurement(
                value=round(max(0.0, hr_base * factor), 1),
                measured_at=measured_at,
                source="simulated",
                provenance=provenance,
            )

        if sys_base is not None:
            sys_factor = 1 + randomizer.uniform(
                -self.RELATIVE_VARIATION, self.RELATIVE_VARIATION
            )
            dia_factor = 1 + randomizer.uniform(
                -self.RELATIVE_VARIATION, self.RELATIVE_VARIATION
            )
            blood_pressure = BloodPressureMeasurement(
                systolic=round(max(0.0, sys_base * sys_factor), 1),
                diastolic=round(max(0.0, dia_base * dia_factor), 1),
                measured_at=measured_at,
                source="simulated",
                provenance=provenance,
            )

        return MeasurementCollection(
            heart_rate=heart_rate,
            blood_pressure=blood_pressure,
        )
