"""Comportamiento empirico de la poda frente al peor caso m*N, barrido de rho."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from promptopt.backtracking import backtracking
from promptopt.simulator import SimParams, Simulator

N_INST = 50


def run(ks, rhos, seeds):
    rows = []
    for k in ks:
        for rho in rhos:
            for seed in seeds:
                sim = Simulator(SimParams(k=k, n_instances=N_INST, rho=rho, seed=seed))
                res = backtracking(sim, prune=True, check_optimum=True)
                rows.append(dict(
                    rho=rho, k=k, seed=seed, queries=res.queries, worst_case=sim.m * N_INST,
                    # fraccion de hojas NO evaluadas = 1 - hojas_evaluadas / m
                    nodes_pruned_frac=1 - res.stats["leaves_evaluated"] / sim.m,
                    found_optimum=res.stats["found_optimum"]))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    ks = [2, 3] if a.quick else [3, 4, 5, 6]
    rhos = [0.0, 1.0] if a.quick else [0.0, 0.25, 0.5, 0.75, 1.0]
    seeds = [0, 1] if a.quick else list(range(5))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    df = run(ks, rhos, seeds)
    df.to_csv(out / "pruning.csv", index=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    for k, g in df.groupby("k"):
        s = g.groupby("rho")["nodes_pruned_frac"].mean()
        ax.plot(s.index, s.values, "o-", label=f"k={k}")
    ax.set_xlabel("rho")
    ax.set_ylabel("fraccion de hojas podadas")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "pruning_vs_rho.png", dpi=130)
    plt.close(fig)
    return df


if __name__ == "__main__":
    main()
