"""Deterministic random number generation for simulations."""

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


class SimulationRandomizer:
    """Isolated random generator initialized with an explicit seed."""

    def __init__(self, seed: int):
        if seed < 0:
            raise ValueError("The random seed cannot be negative.")

        self.seed = seed
        self._random = random.Random(seed)

    def random(self) -> float:
        return self._random.random()

    def uniform(self, minimum: float, maximum: float) -> float:
        return self._random.uniform(minimum, maximum)

    def randint(self, minimum: int, maximum: int) -> int:
        return self._random.randint(minimum, maximum)

    def choice(self, values: Sequence[T]) -> T:
        if not values:
            raise ValueError("Cannot choose from an empty sequence.")

        return self._random.choice(values)

    def gauss(self, mean: float, standard_deviation: float) -> float:
        return self._random.gauss(mean, standard_deviation)
