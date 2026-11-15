"""Catalogue des indicateurs et des règles d'alerte (données, pas logique).

Les bornes « normales » viennent de références publiées (valeurs d'un adulte au repos, sur Terre).
Les paliers d'escalade (attention / priorité élevée) sont un découpage choisi par l'équipe.
is_demo=True signale un seuil choisi par l'équipe plutôt qu'une norme publiée.
"""
from .models import AlertLevel as L
from .models import Operator as O

AHA_BP = "AHA/ACC — catégories de pression artérielle (heart.org)"
AHA_HR = "AHA / Mayo Clinic — fréquence cardiaque au repos 60–100 bpm"
SPO2_REF = "Références cliniques usuelles : SpO2 normale 95–100 %, hypoxémie < 90 %"
TEMP_REF = "MedlinePlus / Cleveland Clinic — normale 36,1–37,2 °C, fièvre ≥ 38 °C, hypothermie < 35 °C"
SLEEP_REF = "AASM/SRS 2015 — adultes : 7 h ou plus par nuit"
TEAM = "Palier d'escalade défini par l'équipe (pas une norme publiée)"

# code, label, unit, category, min_plausible, max_plausible, normal_min, normal_max, norm_reference, description
INDICATORS = [
    ("blood_pressure_systolic", "Pression artérielle systolique", "mmHg", "physiological", 50, 260, 90, 120, AHA_BP,
     "Pression exercée sur les artères quand le cœur se contracte."),
    ("blood_pressure_diastolic", "Pression artérielle diastolique", "mmHg", "physiological", 30, 160, 60, 80, AHA_BP,
     "Pression dans les artères entre deux battements."),
    ("heart_rate", "Fréquence cardiaque", "bpm", "physiological", 20, 250, 60, 100, AHA_HR,
     "Nombre de battements du cœur par minute."),
    ("body_temperature", "Température corporelle", "°C", "physiological", 30, 43, 36.1, 37.2, TEMP_REF,
     "Température du corps (préciser le site de mesure : cutané ou central)."),
    ("spo2", "Saturation en oxygène", "%", "physiological", 50, 100, 95, 100, SPO2_REF,
     "Part de l'hémoglobine saturée en oxygène."),
    ("sleep_duration", "Durée du sommeil", "h", "behavioral", 0, 24, 7, None, SLEEP_REF,
     "Durée de sommeil déclarée ou estimée sur la nuit."),
    ("mood", "Humeur déclarée", "score/5", "psychological", 1, 5, None, None, None,
     "Auto-évaluation (1 = très bas, 5 = très bon). Donnée déclarative, sans norme médicale."),
        ("blood_glucose", "Glycémie", "mg/dL", "physiological", 20, 600, None, None, None,
     "Concentration de glucose dans le sang. Unité de référence du backend : mg/dL."),

    ("respiratory_rate", "Fréquence respiratoire", "breaths/min", "physiological", 0, 80, None, None, None,
     "Nombre de cycles respiratoires par minute."),

    ("tidal_volume", "Volume courant", "mL", "physiological", 0, 3000, None, None, None,
     "Volume d'air mobilisé au cours d'une respiration."),

    ("minute_ventilation", "Ventilation minute", "L/min", "physiological", 0, 50, None, None, None,
     "Volume total d'air ventilé par minute."),

    ("alveolar_ventilation", "Ventilation alvéolaire", "L/min", "physiological", 0, 50, None, None, None,
     "Volume d'air atteignant les alvéoles par minute. Valeur dépendante du volume d'espace mort."),

    ("activity_duration", "Durée d'activité physique", "min", "behavioral", 0, 1440, None, None, None,
     "Durée quotidienne d'activité physique enregistrée en minutes."),

    ("step_count", "Nombre de pas", "steps", "behavioral", 0, 100000, None, None, None,
     "Nombre de pas enregistrés pendant une période d'observation."),
]

# id, indicateur, opérateur, seuil, niveau, mesures consécutives, message, recommandation, référence, is_demo
RULES = [
    ("HR-01", "heart_rate", O.lt, 60, L.information, 2,
     "Fréquence cardiaque inférieure à 60 bpm (bradycardie au repos).",
     "Vérifier le contexte (repos, sommeil, entraînement) ; fréquent chez les personnes très actives.", AHA_HR, False),
    ("HR-02", "heart_rate", O.lt, 50, L.attention, 2,
     "Fréquence cardiaque inférieure à 50 bpm.",
     "Refaire la mesure et signaler à l'équipe médicale si des symptômes sont présents.", TEAM, True),
    ("HR-03", "heart_rate", O.lt, 40, L.high_priority, 1,
     "Fréquence cardiaque inférieure à 40 bpm.",
     "Contacter l'équipe de soutien médical selon le protocole de la mission.", TEAM, True),
    ("HR-04", "heart_rate", O.gt, 100, L.attention, 2,
     "Fréquence cardiaque supérieure à 100 bpm au repos (tachycardie).",
     "Vérifier le contexte (effort, stress) et refaire une mesure au repos.", AHA_HR, False),
    ("HR-05", "heart_rate", O.gt, 130, L.high_priority, 1,
     "Fréquence cardiaque supérieure à 130 bpm.",
     "Contacter l'équipe de soutien médical selon le protocole de la mission.", TEAM, True),

    ("SPO2-01", "spo2", O.lt, 95, L.attention, 2,
     "Saturation en oxygène inférieure à 95 %.",
     "Contrôler le capteur et la ventilation de l'habitacle, puis refaire la mesure.", SPO2_REF, False),
    ("SPO2-02", "spo2", O.lt, 90, L.high_priority, 1,
     "Saturation en oxygène inférieure à 90 % (hypoxémie).",
     "Alerter l'équipe médicale selon le protocole de la mission.", SPO2_REF, False),

    ("TEMP-01", "body_temperature", O.gte, 37.3, L.information, 2,
     "Température légèrement élevée (37,3 °C ou plus).",
     "Surveiller l'évolution et refaire une mesure.", TEMP_REF, False),
    ("TEMP-02", "body_temperature", O.gte, 38.0, L.attention, 2,
     "Fièvre : température de 38,0 °C ou plus.",
     "Refaire la mesure, surveiller les symptômes et informer l'équipe médicale.", TEMP_REF, False),
    ("TEMP-03", "body_temperature", O.gte, 39.5, L.high_priority, 1,
     "Forte fièvre : température de 39,5 °C ou plus.",
     "Contacter l'équipe de soutien médical selon le protocole de la mission.", TEAM, True),
    ("TEMP-04", "body_temperature", O.lt, 35.0, L.high_priority, 1,
     "Température inférieure à 35,0 °C (seuil d'hypothermie).",
     "Contrôler la mesure et contacter l'équipe médicale.", TEMP_REF, False),

    ("BPS-01", "blood_pressure_systolic", O.gte, 120, L.information, 2,
     "Pression systolique dans la zone « élevée » (120 mmHg ou plus).",
     "Suivre la tendance et privilégier les habitudes favorables au cœur.", AHA_BP, False),
    ("BPS-02", "blood_pressure_systolic", O.gte, 130, L.attention, 2,
     "Pression systolique de 130 mmHg ou plus (hypertension stade 1 ou plus).",
     "Refaire la mesure au repos et suivre la tendance.", AHA_BP, False),
    ("BPS-03", "blood_pressure_systolic", O.gt, 180, L.high_priority, 1,
     "Pression systolique supérieure à 180 mmHg (zone de crise hypertensive).",
     "Refaire la mesure après repos ; si elle reste élevée, contacter l'équipe médicale sans attendre.", AHA_BP, False),
    ("BPS-04", "blood_pressure_systolic", O.lt, 90, L.attention, 2,
     "Pression systolique inférieure à 90 mmHg (basse).",
     "Refaire la mesure et faire évaluer par un professionnel de santé.", "Cleveland Clinic — signes vitaux de l'adulte (90/60 à 120/80)", False),
    ("BPD-01", "blood_pressure_diastolic", O.gte, 80, L.attention, 2,
     "Pression diastolique de 80 mmHg ou plus (hypertension stade 1 ou plus).",
     "Refaire la mesure au repos et suivre la tendance.", AHA_BP, False),
    ("BPD-02", "blood_pressure_diastolic", O.gt, 120, L.high_priority, 1,
     "Pression diastolique supérieure à 120 mmHg (zone de crise hypertensive).",
     "Refaire la mesure après repos ; si elle reste élevée, contacter l'équipe médicale sans attendre.", AHA_BP, False),
    ("BPD-03", "blood_pressure_diastolic", O.lt, 60, L.attention, 2,
     "Pression diastolique inférieure à 60 mmHg (basse).",
     "Refaire la mesure et faire évaluer par un professionnel de santé.", "Cleveland Clinic — signes vitaux de l'adulte (90/60 à 120/80)", False),

    ("SLEEP-01", "sleep_duration", O.lt, 7, L.information, 1,
     "Sommeil inférieur à 7 h, la durée recommandée pour un adulte.",
     "Consulter les conseils de routine de sommeil.", SLEEP_REF, False),
    ("SLEEP-02", "sleep_duration", O.lte, 6, L.attention, 1,
     "Sommeil de 6 h ou moins : considéré comme insuffisant pour un adulte.",
     "Prévoir une période de récupération et en parler au soutien de la mission.", SLEEP_REF, False),

    ("MOOD-01", "mood", O.lte, 2, L.information, 1,
     "Humeur déclarée basse (2/5 ou moins).",
     "Proposer un moment d'échange ou de détente.", TEAM, True),
    ("MOOD-02", "mood", O.lte, 2, L.attention, 3,
     "Humeur déclarée basse sur 3 entrées consécutives.",
     "Proposer un échange avec le soutien psychologique de la mission. Donnée déclarative : ce n'est pas un diagnostic.", TEAM, True),
]
