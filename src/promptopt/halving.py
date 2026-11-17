"""Successive Halving (divide y venceras por rondas).

R = ceil(log2 m) rondas. En la ronda r quedan c_r candidatos
(c_0 = m, c_{r+1} = ceil(c_r / 2)) y cada uno se evalua con n0 * 2**r consultas.
Costo por ronda: c_r * n0 * 2**r = m * n0 cuando m es potencia de 2, por lo que
el total es m * n0 * log2 m; con n0 = B / (m log2 m) consume exactamente B.
Si m no es potencia de 2 el redondeo hacia arriba encarece cada ronda, asi que
se usa n0 = B // halving_cost(m, 1) para no exceder B.
El costo no depende de N (las instancias se muestrean con reemplazo).
"""
from __future__ import annotations

import math

import numpy as np

from .common import SearchResult
from .simulator import Simulator


def _rounds(m: int) -> int:
    return 0 if m <= 1 else math.ceil(math.log2(m))


def halving_cost(m: int, n0: int) -> int:
    """Consultas totales exactas: suma por rondas de c_r * n0 * 2**r."""
    total, c = 0, m
    for r in range(_rounds(m)):
        total += c * n0 * 2**r
        c = math.ceil(c / 2)
    return total


def successive_halving(sim: Simulator, B: int, rng: np.random.Generator) -> SearchResult:
    start = sim.queries
    m = sim.m
    configs = list(sim.all_configs())
    R = _rounds(m)
    if R == 0:
        return SearchResult(configs[0], 0, {"rounds": 0, "n0": 0, "cost_formula": 0})
    unit = halving_cost(m, 1)  # costo con n0 = 1 (== m*R si m es potencia de 2)
    n0 = B // unit
    if n0 < 1:
        raise ValueError(f"presupuesto B={B} insuficiente: se requiere B >= {unit}")
    alive = list(range(m))
    for r in range(R):
        n_r = n0 * 2**r
        scores = []
        for idx in alive:
            samples = rng.integers(0, sim.N, size=n_r)
            scores.append(sum(sim.query(configs[idx], int(i)) for i in samples) / n_r)
        keep = math.ceil(len(alive) / 2)
        # desempate aleatorio: orden por (-puntaje, ruido)
        order = sorted(range(len(alive)), key=lambda j: (-scores[j], rng.random()))
        alive = [alive[j] for j in order[:keep]]
    return SearchResult(
        configs[alive[0]],
        sim.queries - start,
        {"rounds": R, "n0": n0, "cost_formula": halving_cost(m, n0)},
    )
