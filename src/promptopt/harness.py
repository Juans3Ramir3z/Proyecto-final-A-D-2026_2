from __future__ import annotations

import time
from typing import Callable

import numpy as np

from .common import SearchResult


def timed(fn: Callable[[], SearchResult]) -> tuple[SearchResult, float]:
    t0 = time.perf_counter()
    res = fn()
    return res, time.perf_counter() - t0


def fit_constant(ns: np.ndarray, times: np.ndarray, shape: Callable[[np.ndarray], np.ndarray]) -> float:
    """Minimos cuadrados para c en times ~ c * shape(ns)."""
    x = np.asarray(shape(np.asarray(ns, dtype=float)), dtype=float)
    y = np.asarray(times, dtype=float)
    return float((x @ y) / (x @ x))
