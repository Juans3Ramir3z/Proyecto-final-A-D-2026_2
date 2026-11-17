"""Barrido de rho: regret de Coordinate Search, Halving y Backtracking."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from promptopt.backtracking import backtracking
from promptopt.coordinate import coordinate_search
from promptopt.halving import halving_cost, successive_halving
from promptopt.simulator import SimParams, Simulator

K, N_INST, S, MAX_ITERS, N0 = 4, 100, 20, 10, 4


def run(rhos, seeds):
    rows = []
    for rho in rhos:
        for seed in seeds:
            sim = Simulator(SimParams(k=K, n_instances=N_INST, rho=rho, seed=seed))
            opt = sim.optimum()[1]
            runs = {
                "coordinate": lambda: coordinate_search(sim, S, MAX_ITERS, np.random.default_rng(seed)),
                "halving": lambda: successive_halving(sim, N0 * halving_cost(sim.m, 1), np.random.default_rng(seed)),
                "backtracking": lambda: backtracking(sim, prune=True),
            }
            for algo, fn in runs.items():
                sim.reset()
                res = fn()
                rows.append(dict(rho=rho, algo=algo, seed=seed, queries=res.queries,
                                 regret=opt - sim.expected_accuracy(res.best_config)))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    rhos = [0.0, 0.8] if a.quick else [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    seeds = list(range(3 if a.quick else 20))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    df = run(rhos, seeds)
    df.to_csv(out / "rho_sweep.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    for algo, g in df.groupby("algo"):
        s = g.groupby("rho")["regret"].agg(["mean", "std"]).fillna(0)
        ax.errorbar(s.index, s["mean"], yerr=s["std"] / np.sqrt(len(seeds)), marker="o", capsize=3, label=algo)
    ax.set_xlabel("rho (interaccion entre instrucciones)")
    ax.set_ylabel("regret medio (precision optima - lograda)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "regret_vs_rho.png", dpi=130)
    plt.close(fig)
    return df


if __name__ == "__main__":
    main()
