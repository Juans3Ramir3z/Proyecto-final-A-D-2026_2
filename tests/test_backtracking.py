from promptopt.backtracking import backtracking
from promptopt.simulator import SimParams, Simulator


def make(k, n=60, **kw):
    return Simulator(SimParams(k=k, n_instances=n, **kw))


def test_no_prune_worst_case():
    sim = make(3)
    res = backtracking(sim, prune=False)
    assert sim.queries == sim.m * sim.N
    assert res.stats["leaves_evaluated"] == sim.m


def test_prune_never_exceeds_worst_case_and_is_exact_without_noise():
    sim = make(3, p_hi=1.0, p_lo=0.0)
    res = backtracking(sim)
    assert res.best_config == sim.optimum()[0] or (
        sim.expected_accuracy(res.best_config) == sim.optimum()[1]
    )
    assert sim.queries <= sim.m * sim.N


def test_pruning_reduces_queries():
    sim = make(4, rho=0.0)
    backtracking(sim)
    assert sim.queries < sim.m * sim.N


def test_k1_single_config():
    sim = make(1)
    res = backtracking(sim)
    assert res.best_config == (0, 0, 0, 0, 0)
    assert sim.queries == sim.N
