"""Conteo de consultas y tiempo medido contra la funcion teorica, k = 2..7.

Uso: python experiments/exp_counts_time.py [--quick] [--out results]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from promptopt.backtracking import backtracking
from promptopt.budget import adaptive_allocation, uniform_allocation
from promptopt.coordinate import coordinate_search
from promptopt.halving import halving_cost, successive_halving
from promptopt.harness import timed
from promptopt.plots import plot_counts_vs_formula, plot_time_vs_n
from promptopt.simulator import SimParams, Simulator

N_INST = 50
RHO = 0.5
S = 10
MAX_ITERS = 3
N0 = 4  # n0 fijo en Halving: B = N0 * halving_cost(m, 1)
U_PER = 8  # consultas por configuracion en el reparto uniforme/adaptativo


def run(ks, seeds):
    rows = []
    for k in ks:
        for seed in seeds:
            sim = Simulator(SimParams(k=k, n_instances=N_INST, rho=RHO, seed=seed))
            m = sim.m
            B_h = N0 * halving_cost(m, 1)
            B_u = U_PER * m

            def row(algo, res, sec, theory, B):
                rows.append(dict(algo=algo, k=k, m=m, N=N_INST, B=B, seed=seed,
                                 queries=res.queries, queries_theory=theory, seconds=sec))

            sim.reset()
            res, sec = timed(lambda: backtracking(sim, prune=False))
            row("backtracking_noprune", res, sec, m * N_INST, 0)
            sim.reset()
            res, sec = timed(lambda: backtracking(sim, prune=True))
            row("backtracking", res, sec, m * N_INST, 0)
            sim.reset()
            rng = np.random.default_rng(seed)
            res, sec = timed(lambda: successive_halving(sim, B_h, rng))
            row("halving", res, sec, halving_cost(m, res.stats["n0"]), B_h)
            sim.reset()
            rng = np.random.default_rng(seed)
            res, sec = timed(lambda: coordinate_search(sim, S, MAX_ITERS, rng))
            row("coordinate", res, sec, res.stats["iters"] * 5 * k * S, 0)
            sim.reset()
            rng = np.random.default_rng(seed)
            res, sec = timed(lambda: uniform_allocation(sim, B_u, rng))
            row("uniform", res, sec, (B_u // m) * m, B_u)
            sim.reset()
            rng = np.random.default_rng(seed)
            res, sec = timed(lambda: adaptive_allocation(sim, B_u, rng))
            row("adaptive", res, sec, B_u, B_u)
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    ks = [2, 3] if a.quick else [2, 3, 4, 5, 6, 7]
    seeds = [0, 1] if a.quick else list(range(5))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    df = run(ks, seeds)
    df.to_csv(out / "counts_time.csv", index=False)
    plot_counts_vs_formula(df, out / "counts_vs_formula.png")
    shapes = {
        "backtracking_noprune": (lambda m: m * N_INST, "c*m*N"),
        "halving": (lambda m: m * np.log2(m), "c*m*log2(m)"),
        "coordinate": (lambda m: m ** 0.2, "c*k = c*m^(1/5)"),
        "uniform": (lambda m: m, "c*m"),
    }
    for algo, (fn, label) in shapes.items():
        plot_time_vs_n(df[df.algo == algo], fn, label, out / f"time_{algo}.png")
    return df


if __name__ == "__main__":
    main()
