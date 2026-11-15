
"""Initialise la base de démonstration.

Crée :
- Une mission fictive.
- Cinq astronautes fictifs.
- Les 14 indicateurs du catalogue.
- Les règles d'alerte.
- Jusqu'à 14 jours de mesures simulées.

Les données sont fictives et destinées aux démonstrations.
Les plages de plausibilité ne constituent pas des normes médicales.
"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from .catalog import INDICATORS, RULES
from .database import Base, SessionLocal, engine
from .models import AlertRule, Astronaut, DataSource, Indicator, Measurement, Mission
from .services.measurements import mission_day


# access_code, nom, prénom, valeurs de base
# Toutes les données sont fictives.
ASTRONAUTS = [
    (
        "AST-4K7Q2X", "Marchand", "Léa",
        dict(
            hr=66, spo2=98.0, temp=36.6, sys=108, dia=68,
            sleep=7.8, glucose=90, rr=16, tidal=500,
            activity=90, steps=5000,
        ),
    ),
    (
        "AST-9M3TZB", "Okoro", "Yanis",
        dict(
            hr=74, spo2=97.0, temp=36.8, sys=112, dia=72,
            sleep=7.4, glucose=94, rr=15, tidal=480,
            activity=85, steps=4600,
        ),
    ),
    (
        "AST-2W8HNC", "Traoré", "Amina",
        dict(
            hr=70, spo2=98.5, temp=36.5, sys=104, dia=66,
            sleep=8.1, glucose=88, rr=17, tidal=510,
            activity=100, steps=5600,
        ),
    ),
    (
        "AST-6R5VDJ", "Valmont", "Hugo",
        dict(
            hr=78, spo2=96.8, temp=36.9, sys=114, dia=74,
            sleep=7.5, glucose=96, rr=16, tidal=490,
            activity=80, steps=4300,
        ),
    ),
    (
        "AST-3P9YLE", "Anselmi", "Sofia",
        dict(
            hr=68, spo2=97.6, temp=36.7, sys=110, dia=70,
            sleep=7.9, glucose=92, rr=15, tidal=520,
            activity=95, steps=5200,
        ),
    ),
]


# Demi-amplitude de variation des données simulées.
NOISE = {
    "hr": 4,
    "spo2": 0.5,
    "temp": 0.2,
    "sys": 4,
    "dia": 3,
    "sleep": 0.4,
    "glucose": 8,
    "rr": 2,
    "tidal": 40,
    "activity": 15,
    "steps": 500,
}


# code indicateur : (clé de base, heures de mesure, précision)
INDICATOR_KEY = {
    "heart_rate": ("hr", [8, 14, 20], 0),
    "spo2": ("spo2", [8, 14, 20], 0),
    "body_temperature": ("temp", [8, 20], 1),
    "blood_pressure_systolic": ("sys", [9, 21], 0),
    "blood_pressure_diastolic": ("dia", [9, 21], 0),
    "sleep_duration": ("sleep", [7], 1),
    "blood_glucose": ("glucose", [8, 20], 0),
    "respiratory_rate": ("rr", [8, 20], 1),
    "tidal_volume": ("tidal", [8, 20], 1),
    "activity_duration": ("activity", [20], 1),
    "step_count": ("steps", [20], 0),
}


def generate_value(
    base: dict,
    key: str,
    rng: random.Random,
    decimals: int,
) -> float:
    """Génère une valeur simulée autour de sa valeur de base."""

    variation = NOISE[key]

    return round(
        rng.uniform(
            base[key] - variation,
            base[key] + variation,
        ),
        decimals,
    )


def seed_database(db: Session, days: int = 14) -> bool:
    """Initialise une base vide.

    Retourne False si le catalogue contient déjà des indicateurs.
    Cette fonction ne met pas à jour une base déjà initialisée.
    """

    if db.query(Indicator).first():
        return False

    now = datetime.now(timezone.utc)

    # 1. Création du catalogue des indicateurs.
    units = {}

    for (
        code,
        label,
        unit,
        category,
        min_plausible,
        max_plausible,
        normal_min,
        normal_max,
        norm_reference,
        description,
    ) in INDICATORS:

        db.add(
            Indicator(
                code=code,
                label=label,
                unit=unit,
                category=category,
                min_plausible=min_plausible,
                max_plausible=max_plausible,
                normal_min=normal_min,
                normal_max=normal_max,
                norm_reference=norm_reference,
                description=description,
            )
        )

        units[code] = unit

    db.flush()

    # 2. Création des règles d'alerte.
    for (
        rule_id,
        indicator,
        operator,
        threshold,
        level,
        consecutive,
        message,
        recommendation,
        reference,
        is_team,
    ) in RULES:

        db.add(
            AlertRule(
                id=rule_id,
                indicator_code=indicator,
                operator=operator,
                threshold=threshold,
                level=level,
                consecutive=consecutive,
                message=message,
                recommendation=recommendation,
                reference=reference,
                is_demo=is_team,
            )
        )

    # 3. Création de la mission fictive.
    start = (
        now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        - timedelta(days=days - 1)
    )

    mission = Mission(
        name="MOON-DEMO-01",
        description="Mission lunaire fictive de démonstration",
        start_date=start,
        planned_days=180,
    )

    db.add(mission)
    db.flush()

    # 4. Création des astronautes et de leurs mesures.
    for idx, (code, last, first, base) in enumerate(ASTRONAUTS):

        astronaut = Astronaut(
            access_code=code,
            last_name=last,
            first_name=first,
            mission_id=mission.id,
        )

        db.add(astronaut)
        db.flush()

        # Générateur reproductible pour chaque astronaute.
        rng = random.Random(42 + idx)

        for day_index in range(days):

            day = start + timedelta(days=day_index)

            # Valeurs respiratoires partagées par heure
            # afin de garantir la cohérence des calculs.
            respiratory_values = {}

            # 4.1. Mesures indépendantes.
            for indicator, (key, hours, decimals) in INDICATOR_KEY.items():

                for hour in hours:

                    recorded_at = day + timedelta(hours=hour)

                    if recorded_at > now:
                        continue

                    value = generate_value(
                        base,
                        key,
                        rng,
                        decimals,
                    )

                    # Conserver les valeurs respiratoires
                    # pour calculer les ventilations.
                    if key in ("rr", "tidal"):
                        respiratory_values.setdefault(hour, {})
                        respiratory_values[hour][key] = value

                    db.add(
                        Measurement(
                            astronaut_id=astronaut.id,
                            indicator_code=indicator,
                            value=value,
                            unit=units[indicator],
                            recorded_at=recorded_at,
                            source=DataSource.simulated,
                            mission_day=mission_day(
                                astronaut,
                                recorded_at,
                            ),
                        )
                    )

            # 4.2. Mesures respiratoires dérivées.
            for hour, values in respiratory_values.items():

                if "rr" not in values or "tidal" not in values:
                    continue

                respiratory_rate = values["rr"]
                tidal_volume = values["tidal"]

                recorded_at = day + timedelta(hours=hour)

                # Ventilation minute :
                # fréquence respiratoire × volume courant / 1000.
                minute_ventilation = round(
                    respiratory_rate * tidal_volume / 1000,
                    2,
                )

                # Ventilation alvéolaire :
                # (volume courant - espace mort) × fréquence / 1000.
                # Hypothèse pédagogique : espace mort fixé à 150 mL.
                dead_space_volume = 150

                alveolar_ventilation = round(
                    max(0, tidal_volume - dead_space_volume)
                    * respiratory_rate
                    / 1000,
                    2,
                )

                for indicator, value in (
                    ("minute_ventilation", minute_ventilation),
                    ("alveolar_ventilation", alveolar_ventilation),
                ):

                    db.add(
                        Measurement(
                            astronaut_id=astronaut.id,
                            indicator_code=indicator,
                            value=value,
                            unit=units[indicator],
                            recorded_at=recorded_at,
                            source=DataSource.simulated,
                            mission_day=mission_day(
                                astronaut,
                                recorded_at,
                            ),
                        )
                    )

            # 4.3. Humeur déclarée.
            mood_time = day + timedelta(
                hours=20,
                minutes=30,
            )

            if mood_time <= now:

                db.add(
                    Measurement(
                        astronaut_id=astronaut.id,
                        indicator_code="mood",
                        value=rng.choice([3, 4, 4, 5]),
                        unit=units["mood"],
                        recorded_at=mood_time,
                        source=DataSource.simulated,
                        mission_day=mission_day(
                            astronaut,
                            mood_time,
                        ),
                    )
                )

    # 5. Enregistrement de toutes les données.
    db.commit()

    return True


if __name__ == "__main__":

    Base.metadata.create_all(engine)

    with SessionLocal() as session:

        if seed_database(session):

            print(
                "Base initialisée : "
                "5 astronautes fictifs, "
                "14 indicateurs, "
                "mission MOON-DEMO-01."
            )

            for code, last, first, _ in ASTRONAUTS:
                print(f"  {code}  {first} {last}")

        else:

            print(
                "Base déjà initialisée, "
                "aucune modification effectuée."
            )
