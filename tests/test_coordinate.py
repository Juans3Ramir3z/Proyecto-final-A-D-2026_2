import numpy as np

from promptopt.coordinate import coordinate_search
from promptopt.simulator import SimParams, Simulator


def make(k, n=100, **kw):
    return Simulator(SimParams(k=k, n_instances=n, **kw))


def test_query_count_formula():
    sim = make(4)
    res = coordinate_search(sim, s=10, max_iters=3, rng=np.random.default_rng(0))
    assert sim.queries == res.stats["iters"] * 5 * 4 * 10


def test_independent_of_m():
    costs = {}
    for k in (2, 7):
        sim = make(k)
        coordinate_search(sim, s=10, max_iters=1, rng=np.random.default_rng(0))
        costs[k] = sim.queries
    assert costs[2] == 5 * 2 * 10 and costs[7] == 5 * 7 * 10


def test_optimal_when_independent():
    ok = 0
    for seed in range(20):
        sim = make(3, n=100, seed=seed, rho=0.0, p_hi=1.0, p_lo=0.0)
        res = coordinate_search(sim, s=sim.N, max_iters=5, rng=np.random.default_rng(seed))
        ok += sim.expected_accuracy(res.best_config) >= sim.optimum()[1] - 1e-12
    assert ok >= 18


def test_max_iters_zero():
    sim = make(3)
    init = (1, 2, 0, 1, 2)
    res = coordinate_search(sim, s=5, max_iters=0, rng=np.random.default_rng(0), init=init)
    assert res.best_config == init and sim.queries == 0
