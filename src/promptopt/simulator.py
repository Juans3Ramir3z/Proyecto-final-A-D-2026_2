"""Simulador de "LLM" por cobertura de reglas.

Modelo
------
* Universo de ``r`` reglas. Cada instancia ``i`` exige un subconjunto
  ``req[i]`` (tamano aleatorio entre 2 y ``r // 2``).
* Cada opcion ``o`` de la categoria ``c`` cubre un subconjunto ``cover[c, o]``.
* Una configuracion cubre la union de las coberturas de sus 5 opciones.
  Resuelve la instancia ``i`` si ``req[i]`` esta contenido en esa union.
* Una consulta devuelve un Bernoulli con probabilidad ``p_hi`` si la
  instancia esta resuelta y ``p_lo`` si no (ruido del "LLM").

Generacion de ``cover`` segun rho (interaccion entre instrucciones)
-------------------------------------------------------------------
La regla ``j`` tiene categoria duena ``j % 5``. Una opcion cubre cada regla de
su categoria con probabilidad ``P_OWN`` y cada regla de OTRA categoria con
probabilidad ``P_CROSS * rho``. Con rho = 0 los bloques son disjuntos
(instrucciones independientes); al subir rho las reglas pueden cubrirse desde
varias categorias, lo que crea redundancia y optimos locales.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterator

import numpy as np

N_CATEGORIES = 5
P_OWN = 0.5
P_CROSS = 0.3


class BudgetExceeded(Exception):
    """Se intento consultar mas veces que el presupuesto."""


@dataclass(frozen=True)
class SimParams:
    k: int
    n_instances: int
    n_rules: int = 12
    rho: float = 0.0
    p_hi: float = 0.95
    p_lo: float = 0.05
    seed: int = 0


class Simulator:
    def __init__(self, params: SimParams, budget: int | None = None):
        self.params = params
        self.k = params.k
        self.N = params.n_instances
        self.m = params.k ** N_CATEGORIES
        self.queries = 0
        self.budget = budget
        r = params.n_rules
        rng = np.random.default_rng(params.seed)
        owner = np.arange(r) % N_CATEGORIES
        cover = np.zeros((N_CATEGORIES, self.k, r), dtype=bool)
        for c in range(N_CATEGORIES):
            p = np.where(owner == c, P_OWN, P_CROSS * params.rho)
            cover[c] = rng.random((self.k, r)) < p
        self.cover = cover
        req = np.zeros((self.N, r), dtype=bool)
        lo, hi = 2, max(2, r // 2)
        for i in range(self.N):
            size = int(rng.integers(lo, hi + 1))
            req[i, rng.choice(r, size=size, replace=False)] = True
        self.req = req
        self._noise = np.random.default_rng(params.seed + 1)
        self._mask_cache: dict[tuple[int, ...], np.ndarray] = {}

    # -- consultas (con costo) -------------------------------------------
    def query(self, config: tuple[int, ...], i: int) -> int:
        if self.budget is not None and self.queries >= self.budget:
            raise BudgetExceeded(f"presupuesto {self.budget} agotado")
        self.queries += 1
        p = self.params.p_hi if self.solvable_mask(config)[i] else self.params.p_lo
        return int(self._noise.random() < p)

    def reset(self, budget: int | None = None) -> None:
        self.queries = 0
        self.budget = budget

    # -- verdad exacta (sin costo) ---------------------------------------
    def all_configs(self) -> Iterator[tuple[int, ...]]:
        return product(range(self.k), repeat=N_CATEGORIES)

    def coverage(self, config: tuple[int, ...]) -> np.ndarray:
        out = np.zeros(self.cover.shape[2], dtype=bool)
        for c, o in enumerate(config):
            out |= self.cover[c, o]
        return out

    def solvable_mask(self, config: tuple[int, ...]) -> np.ndarray:
        key = tuple(config)
        cached = self._mask_cache.get(key)
        if cached is None:
            cov = self.coverage(key)
            cached = ~(self.req & ~cov).any(axis=1)
            self._mask_cache[key] = cached
        return cached

    def expected_accuracy(self, config: tuple[int, ...]) -> float:
        f = float(self.solvable_mask(config).mean())
        return self.params.p_hi * f + self.params.p_lo * (1 - f)

    def optimum(self) -> tuple[tuple[int, ...], float]:
        best, best_acc = None, -1.0
        for c in self.all_configs():
            a = self.expected_accuracy(c)
            if a > best_acc:
                best, best_acc = c, a
        return best, best_acc
