"""Demo interactivo en consola: elegir parametros, correr algoritmos y ver la poda paso a paso.

Uso: python demo_interactivo.py [--k 3] [--n 100] [--rho 0.5] [--seed 1]
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, replace

import numpy as np

from promptopt.backtracking import backtracking
from promptopt.runner import NAMES, build_runs
from promptopt.simulator import N_CATEGORIES, SimParams, Simulator

MAX_K = 7


@dataclass
class State:
    k: int = 3
    n: int = 100
    rho: float = 0.5
    seed: int = 1
    noise: bool = True
    budget_mult: int = 8

    def sim_params(self, seed: int | None = None) -> SimParams:
        hi, lo = (0.95, 0.05) if self.noise else (1.0, 0.0)
        return SimParams(k=self.k, n_instances=self.n, rho=self.rho,
                         seed=self.seed if seed is None else seed, p_hi=hi, p_lo=lo)

    def describe(self) -> str:
        return (f"Parametros: k={self.k} (m={self.k ** N_CATEGORIES}) N={self.n} rho={self.rho} "
                f"semilla={self.seed} ruido={'si' if self.noise else 'no'} presupuesto={self.budget_mult}m")


class Abort(Exception):
    pass


class Demo:
    def __init__(self, state: State, input_fn, out, live: bool):
        self.st, self.ask_fn, self.out, self.live = state, input_fn, out, live

    def ask(self, prompt: str) -> str:
        return self.ask_fn(prompt).strip()

    # -- utilidades -------------------------------------------------------
    def new_sim(self, seed: int | None = None) -> Simulator:
        return Simulator(self.st.sim_params(seed))

    def with_progress(self, sim: Simulator, fn):
        """Ejecuta fn() mostrando una barra con las consultas gastadas frente a m*N."""
        if not self.live:
            return fn()
        ref = sim.m * sim.N
        step = max(1, ref // 60)
        orig = sim.query

        def query(cfg, i):
            r = orig(cfg, i)
            if sim.queries % step == 0:
                frac = min(1.0, sim.queries / ref)
                bar = "#" * int(frac * 30)
                sys.stdout.write(f"\r  [{bar:<30}] {sim.queries:>9,} consultas (referencia m*N = {ref:,})")
                sys.stdout.flush()
            return r

        sim.query = query
        try:
            return fn()
        finally:
            del sim.query  # vuelve al metodo de la clase
            sys.stdout.write("\r" + " " * 90 + "\r")
            sys.stdout.flush()

    def run_one(self, sim: Simulator, name: str, fn):
        sim.reset()
        res = self.with_progress(sim, fn)
        opt = sim.optimum()[1]
        acc = sim.expected_accuracy(res.best_config)
        return res, acc, opt - acc

    # -- acciones ----------------------------------------------------------
    def change_params(self) -> None:
        st = self.st

        def prompt(label, cur, cast, ok):
            raw = self.ask(f"  {label} [{cur}]: ")
            if not raw:
                return cur
            try:
                v = cast(raw)
            except ValueError:
                self.out("  Valor no valido, se mantiene el actual.")
                return cur
            if not ok(v):
                self.out("  Fuera de rango, se mantiene el actual.")
                return cur
            return v

        st.k = prompt(f"k, opciones por categoria (1..{MAX_K})", st.k, int, lambda v: 1 <= v <= MAX_K)
        st.n = prompt("N, numero de instancias", st.n, int, lambda v: v >= 1)
        st.rho = prompt("rho, interaccion entre instrucciones (0..1)", st.rho, float, lambda v: 0 <= v <= 1)
        st.seed = prompt("semilla", st.seed, int, lambda v: True)
        raw = self.ask(f"  ruido en las consultas (s/n) [{'s' if st.noise else 'n'}]: ").lower()
        if raw in ("s", "n"):
            st.noise = raw == "s"

    def header(self, sim: Simulator) -> None:
        cfg, acc = sim.optimum()
        self.out(f"m = {sim.m} configuraciones, N = {sim.N}, peor caso exacto m*N = {sim.m * sim.N:,}")
        self.out(f"Optimo verdadero: {cfg}  precision esperada {acc:.3f}")

    def run_all(self) -> None:
        sim = self.new_sim()
        self.header(sim)
        self.out(f"{'algoritmo':24}{'consultas':>12}  {'config elegida':16}{'precision':>10}{'regret':>8}")
        for name, fn in build_runs(sim, self.st.seed, self.st.budget_mult):
            res, acc, regret = self.run_one(sim, name, fn)
            self.out(f"{name:24}{res.queries:>12,}  {str(res.best_config):16}{acc:>10.3f}{regret:>8.3f}")

    def run_single(self) -> None:
        for i, name in enumerate(NAMES, 1):
            self.out(f"  {i}) {name}")
        raw = self.ask("Algoritmo (1-6): ")
        if not raw.isdigit() or not 1 <= int(raw) <= len(NAMES):
            self.out("Opcion no valida.")
            return
        sim = self.new_sim()
        self.header(sim)
        name, fn = build_runs(sim, self.st.seed, self.st.budget_mult)[int(raw) - 1]
        res, acc, regret = self.run_one(sim, name, fn)
        self.out(f"{name}: {res.queries:,} consultas, configuracion {res.best_config}, "
                 f"precision {acc:.3f}, regret {regret:.3f}")
        for k, v in res.stats.items():
            if not isinstance(v, list):
                self.out(f"  {k} = {v}")

    def step_by_step(self) -> None:
        sim = self.new_sim()
        self.header(sim)
        if sim.m > 1024:
            self.out("Aviso: con m grande hay muchos eventos; use 'c' o 's' para avanzar mas rapido.")
        self.out("Enter = siguiente evento | c = continuar sin pausas | s = saltar al final | q = cancelar")
        mode = {"pause": True, "silent": False}
        saved = {"leaves": 0}
        k, N = sim.k, sim.N

        def on_event(e):
            ev = e["event"]
            best_txt = "ninguno" if e["best"] < 0 else f"{e['best']:.3f}"
            if ev == "prune":
                n_leaves = k ** (N_CATEGORIES - e["depth"])
                saved["leaves"] += n_leaves
                line = (f"{'  ' * e['depth']}PODA {e['prefix']}  cota={e['ub']:.3f} <= mejor={best_txt}"
                        f"  -> se evitan {n_leaves} hojas ({n_leaves * N:,} consultas)")
            elif ev == "descend":
                line = (f"{'  ' * e['depth']}BAJA {e['prefix']}  cota={e['ub']:.3f} > mejor={best_txt}")
            else:
                line = (f"{'  ' * N_CATEGORIES}HOJA {e['cfg']}  valor={e['value']:.3f} "
                        f"({N} consultas)  mejor={best_txt}")
            if mode["silent"]:
                return
            self.out(line)
            if mode["pause"]:
                ans = self.ask("   > ").lower()
                if ans == "c":
                    mode["pause"] = False
                elif ans == "s":
                    mode["pause"], mode["silent"] = False, True
                elif ans == "q":
                    raise Abort

        sim.reset()
        try:
            res = backtracking(sim, prune=True, trace=on_event)
        except Abort:
            self.out("Recorrido interrumpido.")
            return
        acc = sim.expected_accuracy(res.best_config)
        self.out(f"Resultado: {res.best_config}  precision {acc:.3f}  consultas gastadas {res.queries:,} "
                 f"de {sim.m * sim.N:,} del peor caso; hojas evitadas por la poda: {saved['leaves']:,}")

    def multi_seed(self) -> None:
        raw = self.ask("Cuantas semillas (Enter = 5): ")
        count = int(raw) if raw.isdigit() and int(raw) >= 1 else 5
        acc_q = {name: [] for name in NAMES}
        acc_r = {name: [] for name in NAMES}
        for j in range(count):
            seed = self.st.seed + j
            sim = self.new_sim(seed)
            self.out(f"  semilla {seed}...")
            for name, fn in build_runs(sim, seed, self.st.budget_mult):
                res, _, regret = self.run_one(sim, name, fn)
                acc_q[name].append(res.queries)
                acc_r[name].append(regret)
        self.out(f"Promedio sobre {count} semillas (desde la semilla {self.st.seed}):")
        self.out(f"{'algoritmo':24}{'consultas (media)':>18}{'regret medio':>14}{'% con regret>0.01':>20}")
        for name in NAMES:
            r = np.array(acc_r[name])
            self.out(f"{name:24}{np.mean(acc_q[name]):>18,.0f}"
                     f"{r.mean():>14.3f}{100 * (r > 0.01).mean():>19.0f}%")

    # -- bucle principal ------------------------------------------------------
    def loop(self) -> None:
        actions = {"1": self.change_params, "2": self.run_single, "3": self.run_all,
                   "4": self.step_by_step, "5": self.multi_seed}
        while True:
            self.out("")
            self.out("=== Demo interactivo: optimizacion de prompts bajo presupuesto ===")
            self.out(self.st.describe())
            self.out("1) Cambiar parametros   2) Ejecutar un algoritmo   3) Ejecutar todos y comparar")
            self.out("4) Backtracking paso a paso (poda)   5) Repetir en varias semillas   0) Salir")
            choice = self.ask("Opcion: ")
            if choice == "0":
                self.out("Hasta luego.")
                return
            action = actions.get(choice)
            if action is None:
                self.out("Opcion no valida.")
                continue
            action()


def main(argv=None, input_fn=input, out=print, live: bool | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    d = State()
    ap.add_argument("--k", type=int, default=d.k)
    ap.add_argument("--n", type=int, default=d.n)
    ap.add_argument("--rho", type=float, default=d.rho)
    ap.add_argument("--seed", type=int, default=d.seed)
    ap.add_argument("--sin-ruido", action="store_true")
    a = ap.parse_args(argv)
    state = replace(d, k=a.k, n=a.n, rho=a.rho, seed=a.seed, noise=not a.sin_ruido)
    if live is None:
        live = sys.stdout.isatty()
    try:
        Demo(state, input_fn, out, live).loop()
    except (EOFError, KeyboardInterrupt):
        out("\nFin de la entrada.")


if __name__ == "__main__":
    main()
