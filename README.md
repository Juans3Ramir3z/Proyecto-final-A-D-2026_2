# Optimizacion de configuraciones de prompt bajo presupuesto de consultas

Proyecto semestral 2026-2, Analisis y Diseno de Algoritmos. Todo es sintetico: un
simulador de "LLM" por cobertura de reglas, tres algoritmos de busqueda
(Backtracking con poda, Successive Halving, Coordinate Search) y el comparativo de
reparto de presupuesto (uniforme vs adaptativo).

Diseno: `docs/superpowers/specs/2026-11-17-optimizacion-prompts-design.md`.
Plan: `docs/superpowers/plans/2026-11-17-optimizacion-prompts.md`.

## Instalacion

```
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"   # Windows (en Linux/Mac: .venv/bin/python)
```

## Reproducir

```
python run_all.py --quick   # version reducida (k = 2, 3)
python run_all.py           # completa (k = 2..7, 5-20 semillas); genera results/*.csv y *.png
pytest                      # pruebas
```

El notebook `notebooks/reproducir.ipynb` hace lo mismo y muestra las graficas.
Las semillas son fijas (0..4 o 0..19 segun el experimento), por lo que los conteos
de consultas son deterministas; los tiempos varian segun la maquina.

## Estructura

- `src/promptopt/`: simulador, algoritmos, harness y graficas.
- `experiments/`: un script por experimento (conteo y tiempo, poda, barrido de rho, presupuesto).
- `results/`: CSV y PNG generados (no se versionan).
- `informe/`: generador del informe Word (`build_informe.py`) y los textos del equipo en `informe/texto/`.
