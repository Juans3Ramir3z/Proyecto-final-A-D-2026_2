import importlib


def test_run_all_quick_creates_all_artifacts(tmp_path):
    mod = importlib.import_module("run_all")
    mod.main(["--quick", "--out", str(tmp_path)])
    for name in ("counts_time.csv", "pruning.csv", "rho_sweep.csv", "budget.csv"):
        assert (tmp_path / name).exists(), name
