"""Busqueda local por descenso de coordenadas.

Una pasada recorre las 5 categorias; en cada una evalua las k opciones con
``s`` instancias (la misma muestra para las k opciones, comparacion pareada) y
fija la mejor. Costo exacto: 5*k*s consultas por pasada, I*5*k*s para I pasadas;
no depende de m = k**5. Termina tras ``max_iters`` pasadas o cuando una pasada
completa no cambia la configuracion (optimo local respecto a cambios de una
sola categoria).
"""
from __future__ import annotations

import numpy as np

from .common import SearchResult
from .simulator import N_CATEGORIES, Simulator


def coordinate_search(
    sim: Simulator,
    s: int,
    max_iters: int,
    rng: np.random.Generator,
    init: tuple[int, ...] | None = None,
) -> SearchResult:
    start = sim.queries
    cfg = tuple(init) if init is not None else (0,) * N_CATEGORIES
    iters, converged = 0, False
    while iters < max_iters:
        iters += 1
        changed = False
        for c in range(N_CATEGORIES):
            sample = rng.choice(sim.N, size=s, replace=s > sim.N)
            scores = []
            for o in range(sim.k):
                trial = cfg[:c] + (o,) + cfg[c + 1:]
                scores.append(sum(sim.query(trial, int(i)) for i in sample) / s)
            best = max(scores)
            ties = [o for o, v in enumerate(scores) if v == best]
            # conserva la opcion actual si esta empatada (evita oscilar)
            new = cfg[c] if cfg[c] in ties else int(rng.choice(ties))
            if new != cfg[c]:
                changed = True
                cfg = cfg[:c] + (new,) + cfg[c + 1:]
        if not changed:
            converged = True
            break
    return SearchResult(cfg, sim.queries - start, {"iters": iters, "converged": converged})
