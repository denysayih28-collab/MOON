
from app.models.enums import ScenarioType
from app.services.generation.engine import SimulationGenerationEngine
from app.services.generation.generators.cardiovascular import CardiovascularGenerator
from app.services.generation.generators.fluid_intake import FluidIntakeGenerator
from app.services.generation.generators.physical_activity import PhysicalActivityGenerator
from app.services.generation.generators.respiratory import RespiratoryGenerator
from app.services.generation.generators.sleep import SleepGenerator


def build_default_generation_engine() -> SimulationGenerationEngine:
    """Build an engine with all supported scenario generators."""
    return SimulationGenerationEngine(
        generators={
            ScenarioType.SLEEP_DEPRIVATION: SleepGenerator(),
            ScenarioType.CARDIOVASCULAR_VARIATION: CardiovascularGenerator(),
            ScenarioType.RESPIRATORY_VARIATION: RespiratoryGenerator(),
            ScenarioType.PHYSICAL_INACTIVITY: PhysicalActivityGenerator(),
            ScenarioType.DEHYDRATION: FluidIntakeGenerator(),
        }
    )
