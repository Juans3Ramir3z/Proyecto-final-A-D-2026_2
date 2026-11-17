"""Demo: ejecuta los algoritmos sobre una misma instancia y compara consultas y calidad.

Uso: python demo.py [--k 4] [--n 100] [--rho 0.5] [--seed 1] [--budget-mult 8]
  k: opciones por categoria (m = k^5)   n: instancias   rho: interaccion en [0, 1]
  budget-mult: presupuesto de los repartos = budget-mult * m
"""
from __future__ import annotations

import argparse

from promptopt.runner import build_runs
from promptopt.simulator import SimParams, Simulator


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--rho", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--budget-mult", type=int, default=8)
    a = ap.parse_args(argv)

    sim = Simulator(SimParams(k=a.k, n_instances=a.n, rho=a.rho, seed=a.seed))
    opt_cfg, opt_acc = sim.optimum()
    print(f"m = {sim.m} configuraciones, N = {sim.N} instancias, peor caso exacto m*N = {sim.m * sim.N}")
    print(f"Optimo verdadero: {opt_cfg}  precision esperada {opt_acc:.3f}\n")

    runs = build_runs(sim, a.seed, a.budget_mult)
    print(f"{'algoritmo':24}{'consultas':>10}  {'config elegida':16}{'precision':>10}{'regret':>8}")
    for name, fn in runs:
        sim.reset()
        res = fn()
        acc = sim.expected_accuracy(res.best_config)
        print(f"{name:24}{res.queries:>10}  {str(res.best_config):16}{acc:>10.3f}{opt_acc - acc:>8.3f}")


if __name__ == "__main__":
    main()
