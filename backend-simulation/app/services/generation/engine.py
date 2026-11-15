"""Orchestration engine for scenario simulations."""

import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

from app.models.enums import ScenarioType
from app.models.simulation_requests import ScenarioSimulationRequest
from app.models.simulation_responses import SimulationObservation
from app.services.generation.context import GenerationContext
from app.services.generation.generators.base import ScenarioGenerator
from app.services.generation.randomizer import SimulationRandomizer


@dataclass(frozen=True, slots=True)
class GenerationResult:
    observations: list[SimulationObservation]
    simulation_start_at: datetime
    effective_seed: int
    notices: list[str]


class SimulationGenerationEngine:
    """Coordinates deterministic generation across simulation days."""

    def __init__(
        self,
        generators: Mapping[ScenarioType, ScenarioGenerator],
    ):
        self._generators = dict(generators)

    def generate(
        self,
        request: ScenarioSimulationRequest,
    ) -> GenerationResult:
        generator = self._generators.get(request.scenario_id)

        if generator is None:
            raise ValueError(
                f"No generator is registered for scenario "
                f"'{request.scenario_id.value}'."
            )

        effective_seed = (
            request.seed
            if request.seed is not None
            else secrets.randbits(64)
        )

        simulation_start_at = (
            request.simulation_start_at
            if request.simulation_start_at is not None
            else datetime.now(timezone.utc)
        )

        context = GenerationContext(
            scenario_id=request.scenario_id,
            mission_phase=request.mission_phase,
            parameters=request.parameters,
            simulation_start_at=simulation_start_at,
            effective_seed=effective_seed,
        )

        randomizer = SimulationRandomizer(effective_seed)
        simulation_days = request.parameters["simulation_days"]

        observations = []
        notices = []

        if (
            request.scenario_id == ScenarioType.RESPIRATORY_VARIATION
            and request.parameters.get("dead_space_volume_ml") is None
        ):
            notices.append(
                "Alveolar ventilation was not calculated because no "
                "dead-space volume was provided."
            )

        for day in range(1, simulation_days + 1):
            measured_at = context.timestamp_for_day(day)

            measurements = generator.generate_day(
                context=context,
                day=day,
                measured_at=measured_at,
                randomizer=randomizer,
            )

            observations.append(
                SimulationObservation(
                    day=day,
                    measurements=measurements,
                )
            )

        return GenerationResult(
            observations=observations,
            simulation_start_at=simulation_start_at,
            effective_seed=effective_seed,
            notices=notices,
        )
