
from datetime import datetime

from app.models.measurement_collection import MeasurementCollection
from app.models.measurements import (
    AlveolarVentilationMeasurement,
    MinuteVentilationMeasurement,
    RespirationMeasurement,
    RespiratoryRateMeasurement,
    TidalVolumeMeasurement,
)
from app.scenarios.constants import RESPIRATORY_RELATIVE_VARIATION
from app.services.generation.context import GenerationContext
from app.services.generation.randomizer import SimulationRandomizer


class RespiratoryGenerator:
    """Generate mathematically consistent respiratory measurements."""

    RELATIVE_VARIATION = RESPIRATORY_RELATIVE_VARIATION

    def generate_day(self, context: GenerationContext, day: int,
                     measured_at: datetime,
                     randomizer: SimulationRandomizer) -> MeasurementCollection:
        p = context.parameters
        rate = float(p["baseline_respiratory_rate"])
        tidal_volume = float(p["baseline_tidal_volume_ml"])

        rate *= 1 + randomizer.uniform(
            -self.RELATIVE_VARIATION, self.RELATIVE_VARIATION
        )
        tidal_volume *= 1 + randomizer.uniform(
            -self.RELATIVE_VARIATION, self.RELATIVE_VARIATION
        )

        rate = round(max(0.0, rate), 2)
        tidal_volume = round(max(0.0, tidal_volume), 2)
        minute_ventilation = rate * tidal_volume / 1000
        provenance = {"scenario_id": context.scenario_id.value}

        alveolar_ventilation = None
        dead_space_volume = p.get("dead_space_volume_ml")

        if dead_space_volume is not None:
            alveolar_value = (
                (tidal_volume - float(dead_space_volume)) * rate / 1000
            )

            alveolar_ventilation = AlveolarVentilationMeasurement(
                value=round(alveolar_value, 4),
                measured_at=measured_at,
                source="simulated",
                provenance={
                    **provenance,
                    "derivation": (
                        "(tidal_volume_ml - dead_space_volume_ml) "
                        "* respiratory_rate_bpm / 1000"
                    ),
                    "input_measurements": [
                        "tidal_volume",
                        "respiratory_rate",
                    ],
                    "assumptions": [
                        f"dead_space_volume_ml={float(dead_space_volume):g}"
                    ],
                },
            )

        respiration = RespirationMeasurement(
            respiratory_rate=RespiratoryRateMeasurement(
                value=rate,
                measured_at=measured_at,
                source="simulated",
                provenance=provenance,
            ),
            tidal_volume=TidalVolumeMeasurement(
                value=tidal_volume,
                measured_at=measured_at,
                source="simulated",
                provenance=provenance,
            ),
            minute_ventilation=MinuteVentilationMeasurement(
                value=round(minute_ventilation, 4),
                measured_at=measured_at,
                source="simulated",
                provenance=provenance,
            ),
            alveolar_ventilation=alveolar_ventilation,
        )
        return MeasurementCollection(respiration=respiration)
