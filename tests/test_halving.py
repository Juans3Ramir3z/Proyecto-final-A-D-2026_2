import numpy as np
import pytest

from promptopt.halving import halving_cost, successive_halving
from promptopt.simulator import SimParams, Simulator


def make(k, n=100, **kw):
    return Simulator(SimParams(k=k, n_instances=n, **kw))


def test_exact_budget_for_power_of_two():
    sim = make(2)  # m = 32, R = 5
    n0 = 4
    B = 32 * n0 * 5
    successive_halving(sim, B, np.random.default_rng(0))
    assert sim.queries == B == halving_cost(32, n0)


def test_matches_formula_non_power_of_two():
    sim = make(3)  # m = 243
    B = 20000
    res = successive_halving(sim, B, np.random.default_rng(0))
    assert sim.queries == halving_cost(243, res.stats["n0"])
    assert sim.queries <= B


def test_independent_of_N():
    counts = []
    for n in (50, 5000):
        sim = make(2, n=n)
        successive_halving(sim, 1000, np.random.default_rng(0))
        counts.append(sim.queries)
    assert counts[0] == counts[1]


def test_sampling_beyond_N():
    sim = make(2, n=3)
    res = successive_halving(sim, 32 * 5 * 50, np.random.default_rng(0))
    assert sim.queries == halving_cost(32, res.stats["n0"])


def test_too_small_budget_raises():
    sim = make(2)
    with pytest.raises(ValueError):
        successive_halving(sim, 32 * 5 - 1, np.random.default_rng(0))


def test_k1():
    sim = make(1)
    res = successive_halving(sim, 10, np.random.default_rng(0))
    assert res.best_config == (0, 0, 0, 0, 0)
    assert sim.queries == 0
