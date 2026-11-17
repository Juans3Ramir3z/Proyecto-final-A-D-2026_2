import importlib

import numpy as np
import pandas as pd

from promptopt.common import SearchResult
from promptopt.harness import fit_constant, timed


def test_timed_returns_seconds_positive():
    res, sec = timed(lambda: SearchResult((0,) * 5, 0))
    assert res.queries == 0 and sec >= 0.0


def test_fit_constant_recovers_known_slope():
    ns = np.array([1.0, 2.0, 3.0, 4.0])
    c = fit_constant(ns, 3 * ns**2, lambda n: n**2)
    assert abs(c - 3) < 1e-9


def test_counts_script_smoke(tmp_path):
    mod = importlib.import_module("experiments.exp_counts_time")
    mod.main(["--quick", "--out", str(tmp_path)])
    df = pd.read_csv(tmp_path / "counts_time.csv")
    cols = {"algo", "k", "m", "N", "B", "seed", "queries", "queries_theory", "seconds"}
    assert cols <= set(df.columns)
    exact = df[df.algo.isin(["halving", "coordinate", "backtracking_noprune", "uniform"])]
    assert len(exact) > 0
    assert (exact.queries == exact.queries_theory).all()
    pr = df[df.algo == "backtracking"]
    assert (pr.queries <= pr.queries_theory).all()


def test_pruning_script_smoke(tmp_path):
    mod = importlib.import_module("experiments.exp_pruning")
    mod.main(["--quick", "--out", str(tmp_path)])
    df = pd.read_csv(tmp_path / "pruning.csv")
    cols = {"rho", "k", "seed", "queries", "worst_case", "nodes_pruned_frac", "found_optimum"}
    assert cols <= set(df.columns)
    assert (df.queries <= df.worst_case).all()
