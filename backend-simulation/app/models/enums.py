from enum import Enum


class DataSource(str, Enum):
    MANUAL = "manual"
    SIMULATED = "simulated"
    SCIENTIFIC_DATASET = "scientific_dataset"


class MoodLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    NEUTRAL = "neutral"
    GOOD = "good"
    VERY_GOOD = "very_good"


class ActivityIntensity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class MeasurementType(str, Enum):
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_GLUCOSE = "blood_glucose"
    BODY_TEMPERATURE = "body_temperature"
    SLEEP = "sleep"
    MOOD = "mood"
    RESPIRATORY_RATE = "respiratory_rate"
    TIDAL_VOLUME = "tidal_volume"
    MINUTE_VENTILATION = "minute_ventilation"
    ALVEOLAR_VENTILATION = "alveolar_ventilation"
    OXYGEN_SATURATION = "oxygen_saturation"
    PHYSICAL_ACTIVITY = "physical_activity"
    FLUID_INTAKE = "fluid_intake"

class ScenarioType(str, Enum):
    SLEEP_DEPRIVATION = "sleep_deprivation"
    CARDIOVASCULAR_VARIATION = "cardiovascular_variation"
    RESPIRATORY_VARIATION = "respiratory_variation"
    PHYSICAL_INACTIVITY = "physical_inactivity"
    DEHYDRATION = "dehydration"

