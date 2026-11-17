"""Reparto uniforme vs adaptativo con el mismo presupuesto B (multiplos de m)."""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from promptopt.budget import adaptive_allocation, uniform_allocation
from promptopt.simulator import SimParams, Simulator

K, N_INST, RHO = 3, 100, 0.5


def run(mults, seeds):
    rows = []
    for seed in seeds:
        sim = Simulator(SimParams(k=K, n_instances=N_INST, rho=RHO, seed=seed))
        opt = sim.optimum()[1]
        for mult in mults:
            B = mult * sim.m
            for algo, fn in (("uniform", uniform_allocation), ("adaptive", adaptive_allocation)):
                sim.reset()
                res = fn(sim, B, np.random.default_rng(seed))
                rows.append(dict(algo=algo, B=B, mult=mult, seed=seed, queries=res.queries,
                                 regret=opt - sim.expected_accuracy(res.best_config),
                                 accuracy=sim.expected_accuracy(res.best_config)))
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    mults = [2, 8] if a.quick else [2, 4, 8, 16, 32]
    seeds = list(range(3 if a.quick else 20))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    df = run(mults, seeds)
    df.to_csv(out / "budget.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for algo, g in df.groupby("algo"):
        s = g.groupby("mult")["regret"].agg(["mean", "std"]).fillna(0)
        axes[0].errorbar(s.index, s["mean"], yerr=s["std"] / np.sqrt(len(seeds)), marker="o", capsize=3, label=algo)
        axes[1].plot(s.index, s["std"] ** 2, marker="o", label=algo)
    axes[0].set_ylabel("regret medio")
    axes[1].set_ylabel("varianza del regret entre semillas")
    for ax in axes:
        ax.set_xlabel("B / m (consultas por configuracion)")
        ax.set_xscale("log", base=2)
        ax.legend()
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "budget_uniform_vs_adaptive.png", dpi=130)
    plt.close(fig)
    return df


if __name__ == "__main__":
    main()
