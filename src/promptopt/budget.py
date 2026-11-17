"""Reparto del presupuesto de consultas B entre las m configuraciones.

* Uniforme: B // m consultas por configuracion (costo total (B//m)*m <= B).
* Adaptativo (eliminacion por cotas de Hoeffding): 1 consulta de calentamiento
  por configuracion y despues pasos de 1 consulta por configuracion viva. Una
  configuracion se elimina cuando su cota superior ``mean + rad`` queda por
  debajo de la mayor cota inferior ``mean - rad`` entre las vivas, con
  ``rad = sqrt(ln(2m/delta) / (2 n))``. Se detiene al agotar B o al quedar una.
"""
from __future__ import annotations

import math

import numpy as np

from .common import SearchResult
from .simulator import Simulator


def _check(sim: Simulator, B: int) -> None:
    if B < sim.m:
        raise ValueError(f"presupuesto B={B} < m={sim.m}: no alcanza para una consulta por configuracion")


def _argmax_random(values: np.ndarray, rng: np.random.Generator) -> int:
    ties = np.flatnonzero(values == values.max())
    return int(rng.choice(ties))


def uniform_allocation(sim: Simulator, B: int, rng: np.random.Generator) -> SearchResult:
    _check(sim, B)
    start = sim.queries
    per = B // sim.m
    configs = list(sim.all_configs())
    means = np.empty(sim.m)
    for j, cfg in enumerate(configs):
        samples = rng.integers(0, sim.N, size=per)
        means[j] = sum(sim.query(cfg, int(i)) for i in samples) / per
    best = _argmax_random(means, rng)
    return SearchResult(configs[best], sim.queries - start, {"per_config": per})


def adaptive_allocation(
    sim: Simulator, B: int, rng: np.random.Generator, delta: float = 0.05
) -> SearchResult:
    _check(sim, B)
    start = sim.queries
    m = sim.m
    configs = list(sim.all_configs())
    n = np.zeros(m, dtype=int)
    wins = np.zeros(m)
    alive = list(range(m))
    spent = 0
    alive_history = []
    log_term = math.log(2 * m / delta)
    while len(alive) > 1 and spent < B:
        for j in alive:
            if spent >= B:
                break
            wins[j] += sim.query(configs[j], int(rng.integers(0, sim.N)))
            n[j] += 1
            spent += 1
        alive_history.append(len(alive))
        if all(n[j] > 0 for j in alive):
            mean = wins[alive] / n[alive]
            rad = np.sqrt(log_term / (2 * n[alive]))
            max_lcb = (mean - rad).max()
            alive = [j for j, u in zip(alive, mean + rad) if u >= max_lcb]
    means = np.where(n > 0, wins / np.maximum(n, 1), -1.0)
    cand = np.full(m, -1.0)
    cand[alive] = means[alive]
    best = _argmax_random(cand, rng)
    return SearchResult(
        configs[best],
        sim.queries - start,
        {"per_config_queries": n.tolist(), "alive_history": alive_history},
    )
