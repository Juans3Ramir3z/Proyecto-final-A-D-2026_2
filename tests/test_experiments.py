import importlib

import pandas as pd


def test_rho_sweep_smoke(tmp_path):
    importlib.import_module("experiments.exp_rho_sweep").main(["--quick", "--out", str(tmp_path)])
    df = pd.read_csv(tmp_path / "rho_sweep.csv")
    assert {"rho", "algo", "seed", "regret"} <= set(df.columns)
    assert {"coordinate", "halving", "backtracking"} <= set(df.algo)
    assert (df.regret >= -1e-9).all()


def test_budget_script_smoke(tmp_path):
    importlib.import_module("experiments.exp_budget").main(["--quick", "--out", str(tmp_path)])
    df = pd.read_csv(tmp_path / "budget.csv")
    assert {"algo", "B", "seed", "regret"} <= set(df.columns)
    assert {"uniform", "adaptive"} <= set(df.algo)
