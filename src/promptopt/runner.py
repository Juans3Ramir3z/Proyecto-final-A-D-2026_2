"""Lista comun de algoritmos para las demos (consola e interactiva)."""
from __future__ import annotations

import numpy as np

from .backtracking import backtracking
from .budget import adaptive_allocation, uniform_allocation
from .coordinate import coordinate_search
from .halving import halving_cost, successive_halving
from .simulator import Simulator

NAMES = [
    "Backtracking sin poda",
    "Backtracking con poda",
    "Successive Halving",
    "Coordinate Search",
    "Reparto uniforme",
    "Reparto adaptativo",
]


def build_runs(sim: Simulator, seed: int, budget_mult: int = 8):
    """Devuelve [(nombre, funcion_sin_argumentos)] en el orden de NAMES."""
    B = budget_mult * sim.m
    rng = lambda: np.random.default_rng(seed)
    fns = [
        lambda: backtracking(sim, prune=False),
        lambda: backtracking(sim),
        lambda: successive_halving(sim, 4 * halving_cost(sim.m, 1), rng()),
        lambda: coordinate_search(sim, 20, 10, rng()),
        lambda: uniform_allocation(sim, B, rng()),
        lambda: adaptive_allocation(sim, B, rng()),
    ]
    return list(zip(NAMES, fns))
