import numpy as np
import pytest

from promptopt.simulator import BudgetExceeded, SimParams, Simulator


def make(k=3, n=10, **kw):
    return Simulator(SimParams(k=k, n_instances=n, **kw))


def test_m_is_k_pow_5():
    assert make(k=3).m == 243


def test_query_counts_and_budget():
    sim = make()
    c = (0, 0, 0, 0, 0)
    for i in range(3):
        sim.query(c, i)
    assert sim.queries == 3
    sim = make()
    sim.reset(budget=2)
    sim.query(c, 0)
    sim.query(c, 1)
    with pytest.raises(BudgetExceeded):
        sim.query(c, 2)


def test_determinism():
    a, b = make(seed=7), make(seed=7)
    assert (a.cover == b.cover).all() and (a.req == b.req).all()
    c = (1, 2, 0, 1, 2)
    assert [a.query(c, i) for i in range(10)] == [b.query(c, i) for i in range(10)]
    assert not (make(seed=8).req == a.req).all()


def test_expected_accuracy_formula():
    sim = make(p_hi=0.9, p_lo=0.1)
    c = (1, 0, 2, 1, 0)
    f = sim.solvable_mask(c).mean()
    assert sim.expected_accuracy(c) == pytest.approx(0.9 * f + 0.1 * (1 - f))


def test_empty_requirements_always_solvable():
    sim = make()
    sim.req[0, :] = False
    assert all(sim.solvable_mask(c)[0] for c in sim.all_configs())


def test_optimum_matches_bruteforce_and_costs_nothing():
    sim = make(k=2)
    best = max(sim.expected_accuracy(c) for c in sim.all_configs())
    cfg, acc = sim.optimum()
    assert acc == pytest.approx(best)
    assert sim.expected_accuracy(cfg) == pytest.approx(best)
    assert sim.queries == 0


def test_rho_effect_on_structure():
    def owners_per_rule(sim):
        # numero de categorias distintas cuyas opciones cubren cada regla
        return (sim.cover.any(axis=1)).sum(axis=0)

    s0 = make(k=4, rho=0.0)
    assert (owners_per_rule(s0) <= 1).all()
    r = s0.cover.shape[2]
    for j in range(r):
        cats = np.where(s0.cover[:, :, j].any(axis=1))[0]
        assert all(c == j % 5 for c in cats)
    s1 = make(k=4, rho=1.0)
    assert (owners_per_rule(s1) > 1).any()
