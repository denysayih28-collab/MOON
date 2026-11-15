"""Demonstration rules. These are not validated astronaut medical thresholds."""

from dataclasses import dataclass


REFERENCE = (
    "Repère contextuel de démonstration. "
    "Ce seuil n'est pas une norme opérationnelle validée pour les astronautes."
)


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    rule_id: str
    indicator: str
    measurement_type: str
    operator: str
    threshold: float
    consecutive: int
    severity: str
    message: str
    reference: str = REFERENCE
    is_demo: bool = True
    enabled: bool = True


RULES = (
    RuleDefinition("HR-01", "heart_rate", "heart_rate", "<", 60, 2, "information",
                   "Fréquence cardiaque inférieure au seuil de démonstration."),
    RuleDefinition("HR-02", "heart_rate", "heart_rate", "<", 50, 2, "attention",
                   "Fréquence cardiaque très basse selon le seuil de démonstration."),
    RuleDefinition("HR-03", "heart_rate", "heart_rate", "<", 40, 1, "high_priority",
                   "Fréquence cardiaque extrêmement basse selon le seuil de démonstration."),
    RuleDefinition("HR-04", "heart_rate", "heart_rate", ">", 100, 2, "attention",
                   "Fréquence cardiaque élevée selon le seuil de démonstration."),
    RuleDefinition("HR-05", "heart_rate", "heart_rate", ">", 130, 1, "high_priority",
                   "Fréquence cardiaque très élevée selon le seuil de démonstration."),

    RuleDefinition("SPO2-01", "oxygen_saturation", "oxygen_saturation", "<", 95, 2,
                   "attention", "Saturation en oxygène basse selon le seuil de démonstration."),
    RuleDefinition("SPO2-02", "oxygen_saturation", "oxygen_saturation", "<", 90, 1,
                   "high_priority", "Saturation en oxygène très basse selon le seuil de démonstration."),

    RuleDefinition("TEMP-01", "body_temperature", "body_temperature", ">=", 37.3, 2,
                   "information", "Température supérieure au seuil de démonstration."),
    RuleDefinition("TEMP-02", "body_temperature", "body_temperature", ">=", 38, 2,
                   "attention", "Température élevée selon le seuil de démonstration."),
    RuleDefinition("TEMP-03", "body_temperature", "body_temperature", ">=", 39.5, 1,
                   "high_priority", "Température très élevée selon le seuil de démonstration."),
    RuleDefinition("TEMP-04", "body_temperature", "body_temperature", "<", 35, 1,
                   "high_priority", "Température basse selon le seuil de démonstration."),

    RuleDefinition("SBP-01", "blood_pressure_systolic", "blood_pressure", ">=", 120, 2,
                   "information", "Pression systolique supérieure au seuil de démonstration."),
    RuleDefinition("SBP-02", "blood_pressure_systolic", "blood_pressure", ">=", 130, 2,
                   "attention", "Pression systolique élevée selon le seuil de démonstration."),
    RuleDefinition("SBP-03", "blood_pressure_systolic", "blood_pressure", ">", 180, 1,
                   "high_priority", "Pression systolique très élevée selon le seuil de démonstration."),
    RuleDefinition("SBP-04", "blood_pressure_systolic", "blood_pressure", "<", 90, 2,
                   "attention", "Pression systolique basse selon le seuil de démonstration."),

    RuleDefinition("DBP-01", "blood_pressure_diastolic", "blood_pressure", ">=", 80, 2,
                   "attention", "Pression diastolique supérieure au seuil de démonstration."),
    RuleDefinition("DBP-02", "blood_pressure_diastolic", "blood_pressure", ">", 120, 1,
                   "high_priority", "Pression diastolique très élevée selon le seuil de démonstration."),
    RuleDefinition("DBP-03", "blood_pressure_diastolic", "blood_pressure", "<", 60, 2,
                   "attention", "Pression diastolique basse selon le seuil de démonstration."),

    RuleDefinition("SLEEP-01", "sleep", "sleep", "<", 7, 1, "information",
                   "Durée de sommeil inférieure au seuil de démonstration."),
    RuleDefinition("SLEEP-02", "sleep", "sleep", "<=", 6, 1, "attention",
                   "Durée de sommeil très courte selon le seuil de démonstration."),

    RuleDefinition("MOOD-01", "mood", "mood", "<=", 2, 1, "information",
                   "Humeur déclarée basse selon l'échelle de démonstration."),
    RuleDefinition("MOOD-02", "mood", "mood", "<=", 2, 3, "attention",
                   "Humeur déclarée basse de manière répétée selon l'échelle de démonstration."),
)

SEVERITY_ORDER = {
    "information": 1,
    "attention": 2,
    "high_priority": 3,
}

RULES_BY_INDICATOR = {}
for rule in RULES:
    if rule.enabled:
        RULES_BY_INDICATOR.setdefault(rule.indicator, []).append(rule)
