import numpy as np

from promptopt.coordinate import coordinate_search
from promptopt.simulator import SimParams, Simulator


def regrets(rho, n_seeds=40, k=4, n=200):
    out = []
    for seed in range(n_seeds):
        sim = Simulator(SimParams(k=k, n_instances=n, rho=rho, p_hi=1.0, p_lo=0.0, seed=seed))
        res = coordinate_search(sim, s=n, max_iters=10, rng=np.random.default_rng(seed))
        out.append(sim.optimum()[1] - sim.expected_accuracy(res.best_config))
    return np.array(out)


def test_coordinate_search_fails_when_interacting():
    r0, r8 = regrets(0.0), regrets(0.8)
    assert r8.mean() > r0.mean()
    assert (r8 > 1e-12).mean() >= 0.20
