"""Regenera todos los resultados (CSV y PNG) en results/.

Uso: python run_all.py [--quick] [--out results]
"""
from __future__ import annotations

import argparse

from experiments import exp_budget, exp_counts_time, exp_pruning, exp_rho_sweep


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="version reducida para pruebas")
    ap.add_argument("--out", default="results")
    a = ap.parse_args(argv)
    args = ["--out", a.out] + (["--quick"] if a.quick else [])
    for mod in (exp_counts_time, exp_pruning, exp_rho_sweep, exp_budget):
        print("ejecutando", mod.__name__, flush=True)
        mod.main(args)


if __name__ == "__main__":
    main()
