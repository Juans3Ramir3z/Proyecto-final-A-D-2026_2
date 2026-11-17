import numpy as np
import pytest

from promptopt.budget import adaptive_allocation, uniform_allocation
from promptopt.simulator import SimParams, Simulator


def make(k=3, n=100, **kw):
    return Simulator(SimParams(k=k, n_instances=n, **kw))


def test_uniform_cost():
    sim = make()
    B = 243 * 7 + 5
    uniform_allocation(sim, B, np.random.default_rng(0))
    assert sim.queries == (B // 243) * 243 <= B


def test_adaptive_never_exceeds_budget():
    sim = make()
    B = 243 * 20
    res = adaptive_allocation(sim, B, np.random.default_rng(0))
    assert sim.queries <= B
    assert sum(res.stats["per_config_queries"]) == sim.queries


def test_adaptive_spends_less_on_losers():
    sim = make(k=2, seed=0, n_rules=6, p_hi=1.0, p_lo=0.0)
    B = 32 * 600
    res = adaptive_allocation(sim, B, np.random.default_rng(0))
    cfgs = list(sim.all_configs())
    acc = [sim.expected_accuracy(c) for c in cfgs]
    q = res.stats["per_config_queries"]
    assert q[int(np.argmin(acc))] < q[int(np.argmax(acc))]
    assert sim.queries <= B


def test_small_budget_raises():
    sim = make()
    with pytest.raises(ValueError):
        uniform_allocation(sim, 242, np.random.default_rng(0))
    with pytest.raises(ValueError):
        adaptive_allocation(sim, 242, np.random.default_rng(0))
