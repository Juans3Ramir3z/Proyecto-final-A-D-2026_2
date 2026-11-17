"""Backtracking con poda por cota superior (algoritmo exacto de referencia).

Arbol de profundidad 5: el nivel ``d`` fija la opcion de la categoria ``d``.
Una hoja (configuracion completa) se evalua con exactamente N consultas.

Cota superior optimista en un nodo con prefijo fijo (sin consultas, solver de
caja blanca sobre ``sim.cover`` y ``sim.req``): sea ``f`` la fraccion de
instancias cuyas reglas quedan contenidas en
``cobertura(prefijo) U union de todas las opciones de las categorias restantes``.
Ninguna hoja descendiente puede resolver mas instancias que esas, asi que

    ub = p_hi * f + p_lo * (1 - f)

acota la precision esperada de todo el subarbol. Se poda si ``ub`` no supera el
mejor valor observado. Peor caso (sin poda efectiva): m * N consultas.

Nota: el valor de una hoja es la media *observada* (ruidosa), mientras que la
cota es sobre la precision esperada; el ruido puede causar podas erroneas, por
eso ``stats['found_optimum']`` indica si se hallo el optimo verdadero.
"""
from __future__ import annotations

import numpy as np

from .common import SearchResult
from .simulator import N_CATEGORIES, Simulator


def backtracking(sim: Simulator, prune: bool = True) -> SearchResult:
    p = sim.params
    start = sim.queries
    # union de coberturas de las categorias d..4
    suffix = [np.zeros(sim.cover.shape[2], dtype=bool) for _ in range(N_CATEGORIES + 1)]
    for d in range(N_CATEGORIES - 1, -1, -1):
        suffix[d] = suffix[d + 1] | sim.cover[d].any(axis=0)

    def upper_bound(cov: np.ndarray, d: int) -> float:
        full = cov | suffix[d]
        f = float((~(sim.req & ~full).any(axis=1)).mean())
        return p.p_hi * f + p.p_lo * (1 - f)

    state = {"best": -1.0, "cfg": None, "visited": 0, "pruned": 0, "leaves": 0}

    def dfs(d: int, cfg: tuple[int, ...], cov: np.ndarray) -> None:
        state["visited"] += 1
        if d == N_CATEGORIES:
            state["leaves"] += 1
            value = sum(sim.query(cfg, i) for i in range(sim.N)) / sim.N
            if value > state["best"]:
                state["best"], state["cfg"] = value, cfg
            return
        children = []
        for o in range(sim.k):
            ccov = cov | sim.cover[d, o]
            children.append((upper_bound(ccov, d + 1), o, ccov))
        if prune:
            children.sort(key=lambda t: -t[0])
        for ub, o, ccov in children:
            if prune and ub <= state["best"]:
                state["pruned"] += 1
                continue
            dfs(d + 1, cfg + (o,), ccov)

    dfs(0, (), np.zeros(sim.cover.shape[2], dtype=bool))
    best = state["cfg"]
    opt_acc = sim.optimum()[1]
    return SearchResult(
        best_config=best,
        queries=sim.queries - start,
        stats={
            "nodes_visited": state["visited"],
            "nodes_pruned": state["pruned"],
            "leaves_evaluated": state["leaves"],
            "found_optimum": bool(abs(sim.expected_accuracy(best) - opt_acc) < 1e-12),
        },
    )
