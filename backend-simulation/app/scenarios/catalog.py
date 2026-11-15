from dataclasses import dataclass
from typing import Literal

from app.models.enums import MeasurementType, ScenarioType


ParameterType = Literal[
    "integer",
    "number",
    "boolean",
    "string",
    "enum",
]


@dataclass(frozen=True, slots=True)
class ScenarioParameter:
    """Description of a configurable scenario parameter."""

    parameter_id: str
    value_type: ParameterType
    description: str
    required: bool = True
    unit: str | None = None
    default_value: str | int | float | bool | None = None
    allowed_values: tuple[str, ...] = ()
    minimum: float | None = None
    maximum: float | None = None


@dataclass(frozen=True, slots=True)
class ScenarioPhase:
    """Description of a mission phase within a scenario."""

    phase_id: str
    name: str
    description: str


@dataclass(frozen=True, slots=True)
class ScientificReference:
    """Scientific source supporting a scenario."""

    title: str
    url: str
    description: str


@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    """Complete descriptive definition of a simulation scenario."""

    scenario_id: ScenarioType
    name: str
    description: str
    objective: str
    measurement_types: tuple[MeasurementType, ...]
    parameters: tuple[ScenarioParameter, ...]
    phases: tuple[ScenarioPhase, ...]
    relationships: tuple[str, ...]
    scientific_references: tuple[ScientificReference, ...]
    limitations: tuple[str, ...]


SCENARIO_CATALOG: dict[ScenarioType, ScenarioDefinition] = {

    ScenarioType.SLEEP_DEPRIVATION: ScenarioDefinition(
        scenario_id=ScenarioType.SLEEP_DEPRIVATION,
        name="Sleep Deprivation",
        description=(
            "Educational simulation of sleep reduction and irregular "
            "sleep patterns during spaceflight."
        ),
        objective=(
            "Explore how changes in sleep duration and regularity may "
            "relate to fatigue, mood and human performance."
        ),
        measurement_types=(
            MeasurementType.SLEEP,
            MeasurementType.MOOD,
            MeasurementType.HEART_RATE,
        ),
        parameters=(
            ScenarioParameter(
                parameter_id="simulation_days",
                value_type="integer",
                description="Duration of the simulation in days.",
                unit="days",
                minimum=1,
            ),
            ScenarioParameter(
                parameter_id="sleep_duration_hours",
                value_type="number",
                description="Target daily sleep duration.",
                unit="hours",
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="baseline_sleep_hours",
                value_type="number",
                description="Reference daily sleep duration.",
                unit="hours",
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="sleep_pattern",
                value_type="enum",
                description="Pattern used to generate sleep variations.",
                allowed_values=(
                    "stable_sleep",
                    "progressive_reduction",
                    "irregular_sleep",
                ),
            ),
        ),
        phases=(
            ScenarioPhase(
                "terrestrial_baseline",
                "Terrestrial Baseline",
                "Reference sleep conditions before the mission.",
            ),
            ScenarioPhase(
                "early_microgravity",
                "Early Microgravity",
                "Initial adaptation to the spaceflight environment.",
            ),
            ScenarioPhase(
                "prolonged_microgravity",
                "Prolonged Microgravity",
                "Sleep monitoring during an extended mission.",
            ),
            ScenarioPhase(
                "postflight_recovery",
                "Postflight Recovery",
                "Sleep monitoring after returning to Earth.",
            ),
        ),
        relationships=(
            "Reduced sleep duration may contribute to fatigue.",
            "Irregular sleep schedules may affect circadian regulation.",
            "Mood is a subjective measurement and must not be treated "
            "as a direct measurement of cognitive performance.",
        ),
        scientific_references=(
            ScientificReference(
                title="Risk from Inadequate Sleep and Irregular Schedules",
                url=(
                    "https://www.nasa.gov/reference/"
                    "risk-from-inadequate-sleep-and-irregular-schedules/"
                ),
                description="NASA overview of sleep-related spaceflight risks.",
            ),
        ),
        limitations=(
            "The scenario does not diagnose sleep disorders.",
            "Heart rate must not be assumed to increase automatically.",
            "Cognitive performance is not directly measured.",
            "Generated measurements are fictional.",
        ),
    ),

    ScenarioType.CARDIOVASCULAR_VARIATION: ScenarioDefinition(
        scenario_id=ScenarioType.CARDIOVASCULAR_VARIATION,
        name="Cardiovascular Variation",
        description=(
            "Educational simulation of cardiovascular adaptations "
            "during microgravity and postflight recovery."
        ),
        objective=(
            "Explore cardiovascular changes associated with fluid "
            "redistribution, microgravity exposure and readaptation "
            "to Earth's gravity."
        ),
        measurement_types=(
            MeasurementType.HEART_RATE,
            MeasurementType.BLOOD_PRESSURE,
            MeasurementType.PHYSICAL_ACTIVITY,
        ),
        parameters=(
            ScenarioParameter(
                parameter_id="simulation_days",
                value_type="integer",
                description="Duration of the simulation in days.",
                unit="days",
                minimum=1,
            ),
            ScenarioParameter(
                parameter_id="baseline_heart_rate",
                value_type="integer",
                description="Reference heart rate.",
                unit="beats/min",
                required=False,
                minimum=0,
            ),

            ScenarioParameter(
                parameter_id="baseline_systolic_pressure",
                value_type="integer",
                description="Reference systolic blood pressure.",
                unit="mmHg",
                required=False,
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="baseline_diastolic_pressure",
                value_type="integer",
                description="Reference diastolic blood pressure.",
                unit="mmHg",
                required=False,
                minimum=0,
            ),
            
            ScenarioParameter(
                parameter_id="exercise_countermeasure",
                value_type="boolean",
                description=(
                    "Indicates whether an exercise countermeasure "
                    "is included in the scenario."
                ),
            ),
        ),
        phases=(
            ScenarioPhase(
                "terrestrial_baseline",
                "Terrestrial Baseline",
                "Cardiovascular reference before spaceflight.",
            ),
            ScenarioPhase(
                "early_microgravity",
                "Early Microgravity",
                "Initial cardiovascular adaptation to microgravity.",
            ),
            ScenarioPhase(
                "prolonged_microgravity",
                "Prolonged Microgravity",
                "Cardiovascular monitoring during extended exposure.",
            ),
            ScenarioPhase(
                "postflight_recovery",
                "Postflight Recovery",
                "Readaptation following the return to Earth's gravity.",
            ),
        ),
        relationships=(
            "Microgravity can modify fluid distribution.",
            "Cardiovascular responses vary between individuals.",
            "Exercise countermeasures may help limit some adaptations.",
            "Postflight orthostatic responses depend on individual context.",
        ),
        scientific_references=(
            ScientificReference(
                title="Risk of Cardiovascular Adaptations",
                url=(
                    "https://www.nasa.gov/reference/"
                    "risk-of-cardiovascular-adaptations/"
                ),
                description="NASA overview of cardiovascular risks in space.",
            ),
        ),
        limitations=(
            "Heart rate alone cannot establish cardiovascular health.",
            "Blood pressure changes are not automatically pathological.",
            "Blood volume is not directly measured.",
            "Exercise does not guarantee prevention of all adaptations.",
        ),
    ),

    ScenarioType.RESPIRATORY_VARIATION: ScenarioDefinition(
        scenario_id=ScenarioType.RESPIRATORY_VARIATION,
        name="Respiratory Variation",
        description=(
            "Educational simulation of respiratory measurements "
            "and respiratory mechanics in microgravity."
        ),
        objective=(
            "Explore relationships between respiratory rate, tidal "
            "volume and minute ventilation during spaceflight."
        ),
        measurement_types=(
            MeasurementType.RESPIRATORY_RATE,
            MeasurementType.TIDAL_VOLUME,
            MeasurementType.MINUTE_VENTILATION,
            MeasurementType.ALVEOLAR_VENTILATION,
        ),
        parameters=(
            ScenarioParameter(
                parameter_id="simulation_days",
                value_type="integer",
                description="Duration of the simulation in days.",
                unit="days",
                minimum=1,
            ),
            ScenarioParameter(
                parameter_id="baseline_respiratory_rate",
                value_type="number",
                description="Reference respiratory rate.",
                unit="breaths/min",
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="baseline_tidal_volume_ml",
                value_type="number",
                description="Reference tidal volume.",
                unit="mL",
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="dead_space_volume_ml",
                value_type="number",
                description=(
                    "Explicit assumed dead-space volume used to "
                    "calculate educational alveolar ventilation."
                ),
                unit="mL",
                required=False,
                minimum=0,
            ),
        ),
        phases=(
            ScenarioPhase(
                "terrestrial_baseline",
                "Terrestrial Baseline",
                "Reference respiratory measurements before flight.",
            ),
            ScenarioPhase(
                "early_microgravity",
                "Early Microgravity",
                "Initial respiratory adaptation.",
            ),
            ScenarioPhase(
                "prolonged_microgravity",
                "Prolonged Microgravity",
                "Respiratory monitoring during extended exposure.",
            ),
            ScenarioPhase(
                "postflight_recovery",
                "Postflight Recovery",
                "Respiratory monitoring after return to Earth.",
            ),
        ),
        relationships=(
            "Minute ventilation depends on respiratory rate "
            "and tidal volume.",
            "Alveolar ventilation is calculated using tidal volume, "
            "dead-space volume and respiratory rate.",
            "Oxygen saturation must not be inferred from respiratory rate.",
        ),
        scientific_references=(
            ScientificReference(
                title="Lung Volumes in Microgravity",
                url="https://ntrs.nasa.gov/citations/19950011389",
                description=(
                    "NASA technical research concerning respiratory "
                    "measurements in microgravity."
                ),
            ),
        ),
        limitations=(
            "Alveolar ventilation is an educational calculated value, "
            "not a direct measurement.",
            "Dead-space assumptions must be explicitly documented.",
            "Respiratory changes do not automatically indicate "
            "lung deterioration.",
            "Pulmonary perfusion and gas exchange are not directly measured.",
        ),
    ),

    ScenarioType.PHYSICAL_INACTIVITY: ScenarioDefinition(
        scenario_id=ScenarioType.PHYSICAL_INACTIVITY,
        name="Physical Inactivity",
        description=(
            "Educational simulation of physical activity patterns "
            "and exercise countermeasures during spaceflight."
        ),
        objective=(
            "Explore how activity patterns and exercise countermeasures "
            "relate to physical conditioning during and after missions."
        ),
        measurement_types=(
            MeasurementType.PHYSICAL_ACTIVITY,
            MeasurementType.HEART_RATE,
        ),
        parameters=(
            ScenarioParameter(
                parameter_id="simulation_days",
                value_type="integer",
                description="Duration of the simulation in days.",
                unit="days",
                minimum=1,
            ),
            ScenarioParameter(
                parameter_id="baseline_activity_duration",
                value_type="number",
                description="Reference daily activity duration.",
                unit="minutes",
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="activity_pattern",
                value_type="enum",
                description="Pattern used to generate activity variations.",
                allowed_values=(
                    "stable_activity",
                    "progressive_reduction",
                    "irregular_activity",
                ),
            ),
            ScenarioParameter(
                parameter_id="countermeasure_profile",
                value_type="enum",
                description="Type of exercise countermeasure.",
                allowed_values=(
                    "none",
                    "aerobic",
                    "resistance",
                    "combined",
                ),
            ),
        ),
        phases=(
            ScenarioPhase(
                "terrestrial_baseline",
                "Terrestrial Baseline",
                "Reference activity before the mission.",
            ),
            ScenarioPhase(
                "early_microgravity",
                "Early Microgravity",
                "Initial adaptation to physical activity in microgravity.",
            ),
            ScenarioPhase(
                "prolonged_microgravity",
                "Prolonged Microgravity",
                "Activity and exercise monitoring during extended missions.",
            ),
            ScenarioPhase(
                "postflight_recovery",
                "Postflight Recovery",
                "Physical recovery after returning to Earth.",
            ),
        ),
        relationships=(
            "Reduced physical activity may contribute to deconditioning.",
            "Aerobic and resistance exercises target different "
            "physical capacities.",
            "Exercise countermeasures do not eliminate all "
            "deconditioning risks.",
        ),
        scientific_references=(
            ScientificReference(
                title="Risk of Reduced Cardiorespiratory "
                "and Musculoskeletal Fitness",
                url=(
                    "https://www.nasa.gov/reference/"
                    "risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/"
                ),
                description=(
                    "NASA overview of physical fitness risks "
                    "during spaceflight."
                ),
            ),
        ),
        limitations=(
            "Step count does not fully represent activity in microgravity.",
            "Physical activity duration does not directly measure "
            "muscle strength.",
            "Aerobic capacity is not directly measured.",
            "Heart rate must not be modified deterministically "
            "to represent inactivity.",
        ),
    ),

    ScenarioType.DEHYDRATION: ScenarioDefinition(
        scenario_id=ScenarioType.DEHYDRATION,
        name="Hydration and Fluid Balance",
        description=(
            "Educational simulation of fluid intake and contextual "
            "factors that may influence hydration balance."
        ),
        objective=(
            "Explore the relationship between fluid intake, operational "
            "conditions and potential fluid losses during spaceflight."
        ),
        measurement_types=(
            MeasurementType.FLUID_INTAKE,
            MeasurementType.BODY_TEMPERATURE,
            MeasurementType.HEART_RATE,
            MeasurementType.BLOOD_PRESSURE,
        ),
        parameters=(
            ScenarioParameter(
                parameter_id="simulation_days",
                value_type="integer",
                description="Duration of the simulation in days.",
                unit="days",
                minimum=1,
            ),
            ScenarioParameter(
                parameter_id="baseline_fluid_intake_ml",
                value_type="number",
                description="Reference daily fluid intake.",
                unit="mL",
                minimum=0,
            ),
            ScenarioParameter(
                parameter_id="intake_pattern",
                value_type="enum",
                description="Pattern used to generate fluid intake variations.",
                allowed_values=(
                    "stable_intake",
                    "progressive_reduction",
                    "irregular_intake",
                ),
            ),
            ScenarioParameter(
                parameter_id="heat_exposure",
                value_type="enum",
                description="Simulated operational heat exposure.",
                allowed_values=("none", "moderate", "high"),
            ),
            ScenarioParameter(
                parameter_id="suited_activity",
                value_type="boolean",
                description=(
                    "Indicates whether suited activity is included "
                    "in the scenario."
                ),
            ),
        ),
        phases=(
            ScenarioPhase(
                "terrestrial_baseline",
                "Terrestrial Baseline",
                "Reference fluid intake before the mission.",
            ),
            ScenarioPhase(
                "early_microgravity",
                "Early Microgravity",
                "Initial fluid balance adaptation.",
            ),
            ScenarioPhase(
                "suited_operations",
                "Suited Operations",
                "Operational context involving suited activity.",
            ),
            ScenarioPhase(
                "prolonged_microgravity",
                "Prolonged Microgravity",
                "Fluid intake monitoring during extended exposure.",
            ),
            ScenarioPhase(
                "postflight_recovery",
                "Postflight Recovery",
                "Fluid intake monitoring after return to Earth.",
            ),
        ),
        relationships=(
            "Reduced fluid intake may contribute to an imbalance "
            "when considered against individual needs and losses.",
            "Heat exposure and physical activity may influence "
            "fluid loss.",
            "Fluid intake alone cannot establish hydration status.",
        ),
        scientific_references=(
            ScientificReference(
                title="Characterizing Dehydration in Short-Term Spaceflight",
                url="https://www.nature.com/articles/s41526-024-00374-8",
                description=(
                    "Research using evidence from Project Mercury "
                    "to characterize dehydration during short missions."
                ),
            ),
        ),
        limitations=(
            "Fluid intake is not a direct measurement of hydration status.",
            "Fluid losses are not measured by the current data model.",
            "Microgravity-related fluid redistribution does not "
            "automatically indicate dehydration.",
            "No universal fluid intake threshold is applied.",
        ),
    ),
}