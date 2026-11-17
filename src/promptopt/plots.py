from __future__ import annotations

from pathlib import Path
from typing import Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .harness import fit_constant


def plot_time_vs_n(df: pd.DataFrame, shape_fn: Callable, label: str, path) -> None:
    """Tiempo medido (media y dispersion por m) contra c * shape(m) con c ajustada."""
    g = df.groupby("m")["seconds"].agg(["mean", "std"]).reset_index().sort_values("m")
    c = fit_constant(g["m"].to_numpy(), g["mean"].to_numpy(), shape_fn)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(g["m"], g["mean"], yerr=g["std"].fillna(0), fmt="o", capsize=3, label="medido")
    xs = np.linspace(g["m"].min(), g["m"].max(), 200)
    ax.plot(xs, c * shape_fn(xs), "-", label=f"teorico ({label}), c={c:.2e}")
    ax.set_xlabel("n = m (configuraciones)")
    ax.set_ylabel("tiempo (s)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot_counts_vs_formula(df: pd.DataFrame, path) -> None:
    fig, ax = plt.subplots(figsize=(5.5, 5))
    for algo, g in df.groupby("algo"):
        ax.scatter(g["queries_theory"], g["queries"], s=18, label=algo)
    lo = max(1, min(df["queries_theory"].min(), df["queries"].min()))
    hi = max(df["queries_theory"].max(), df["queries"].max())
    ax.plot([lo, hi], [lo, hi], "k--", lw=1, label="y = x")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("consultas teoricas")
    ax.set_ylabel("consultas medidas")
    ax.legend(fontsize=7)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130)
    plt.close(fig)
