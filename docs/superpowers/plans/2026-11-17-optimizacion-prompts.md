# Optimización de prompts bajo presupuesto: plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir un simulador de "LLM" y 3 algoritmos de búsqueda (más el comparativo de reparto de presupuesto), con experimentos reproducibles que comparen conteos y tiempos medidos contra T(n) teórico, y un generador de informe Word.

**Architecture:** Paquete Python `promptopt` con un simulador por cobertura de reglas (parámetros ρ de interacción y ruido), un contador de consultas global y un módulo por algoritmo. Los scripts de `experiments/` escriben CSV a `results/`; `plots.py` los grafica; un notebook y un script de informe consumen esos resultados.

**Tech Stack:** Python ≥ 3.10, numpy, pandas, matplotlib, pytest, python-docx, jupyter.

**Spec:** `docs/superpowers/specs/2026-11-17-optimizacion-prompts-design.md`

## Global Constraints

- 5 categorías; k opciones por categoría; **m = k^5** configuraciones; **N** instancias; **B** presupuesto de consultas.
- Tamaños de n principal (m): k ∈ {2, 3, 4, 5, 6, 7} → m ∈ {32, 243, 1024, 3125, 7776, 16807}.
- Todo reproducible con semilla fija; ningún resultado del informe se escribe a mano.
- Una consulta = `Simulator.query(config, i)`; superar el presupuesto lanza `BudgetExceeded`.
- Fórmulas teóricas (deducciones del equipo, confirmadas N para Halving):
  - Backtracking peor caso: m·N consultas.
  - Successive Halving: costo por ronda m·n₀, total m·n₀·log₂ m; con n₀ = B/(m·log₂ m) consume exactamente B, independiente de N.
  - Coordinate Search: I·5·k·s consultas para I iteraciones, independiente de m.
  - Reparto uniforme: B/m consultas por configuración, B en total.
- Solo simulador, sin LLM real ni GPU.

## Review Focus

- k = 1 (m = 1): todos los algoritmos devuelven la única configuración sin errores.
- B demasiado pequeño para el esquema (n₀ = 0 en Halving, B < m en uniforme): se lanza `ValueError` claro, no un resultado silencioso.
- m que no es potencia de 2 (243, 1024 sí; 243 no): Halving usa ⌈c/2⌉ sobrevivientes y su conteo coincide con la fórmula de suma por rondas y nunca supera B.
- Ronda de Halving con n₀·2^r > N: el muestreo es con reemplazo y el conteo sigue siendo exacto.
- Instancia sin reglas requeridas (R_i vacío): se resuelve con cualquier configuración; las cotas y el óptimo la cuentan correctamente.
- Mismas semillas, mismos resultados (determinismo) y semillas distintas, instancias distintas.

---

### Task 1: Andamiaje y simulador

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `src/promptopt/__init__.py`, `src/promptopt/simulator.py`, `src/promptopt/common.py`
- Test: `tests/test_simulator.py`

**Interfaces:**
- Produces (`simulator.py`):
  - `class BudgetExceeded(Exception)`
  - `@dataclass(frozen=True) SimParams(k: int, n_instances: int, n_rules: int = 12, rho: float = 0.0, p_hi: float = 0.95, p_lo: float = 0.05, seed: int = 0)`
  - `class Simulator(params: SimParams, budget: int | None = None)` con atributos `m: int`, `N: int`, `k: int`, `queries: int`, `cover: np.ndarray[bool] (5, k, r)`, `req: np.ndarray[bool] (N, r)` y métodos:
    - `query(config: tuple[int, ...], i: int) -> int` (0/1, incrementa `queries`)
    - `reset(budget: int | None = None) -> None`
    - `all_configs() -> Iterator[tuple[int, ...]]`
    - `coverage(config) -> np.ndarray[bool] (r)`
    - `solvable_mask(config) -> np.ndarray[bool] (N)` (verdad exacta, sin costo)
    - `expected_accuracy(config) -> float`
    - `optimum() -> tuple[tuple[int, ...], float]` (fuerza bruta sobre `expected_accuracy`, sin costo)
- Produces (`common.py`): `@dataclass SearchResult(best_config: tuple[int, ...], queries: int, stats: dict)`.

- [ ] **Step 1: Escribir las pruebas que fallan** en `tests/test_simulator.py`:
  - `test_m_is_k_pow_5`: `Simulator(SimParams(k=3, n_instances=10)).m == 243`.
  - `test_query_counts_and_budget`: tras 3 `query` el atributo `queries == 3`; con `budget=2`, la tercera lanza `BudgetExceeded`.
  - `test_determinism`: dos simuladores con la misma `SimParams` producen el mismo `cover`, `req` y la misma secuencia de resultados de `query`; con distinta `seed`, `req` difiere.
  - `test_expected_accuracy_formula`: para una configuración con fracción `f = solvable_mask(c).mean()`, `expected_accuracy(c) == p_hi*f + p_lo*(1-f)`.
  - `test_empty_requirements_always_solvable`: una instancia con `req[i]` vacío tiene `solvable_mask[i] == True` para toda configuración (construir forzando `sim.req[0,:] = False`).
  - `test_optimum_matches_bruteforce_and_costs_nothing`: `optimum()` coincide con el máximo de `expected_accuracy` sobre `all_configs()` y deja `queries == 0`.
  - `test_rho_effect_on_structure`: con ρ = 0 cada regla la cubren solo opciones de una categoría "dueña" (la regla j pertenece a la categoría j % 5); con ρ = 1 existen reglas cubiertas por opciones de más de una categoría.
- [ ] **Step 2: Ejecutar** `pytest tests/test_simulator.py -v`. Esperado: FALLA por import.
- [ ] **Step 3: Implementar** `simulator.py` y `common.py`. `pyproject.toml` declara el paquete con layout `src/` y las dependencias de Tech Stack. El ruido de `query` usa un `np.random.Generator` aparte sembrado con `seed + 1`. Generación de `cover`/`req`: decisión del implementador, con estos requisitos: (a) con ρ = 0, bloques de reglas disjuntos por categoría y cada opción cubre un subconjunto aleatorio de su bloque; (b) a mayor ρ, cada opción cubre además reglas de otras categorías con probabilidad creciente en ρ; (c) cada `req[i]` es un subconjunto aleatorio de U de tamaño entre 2 y r // 2. Documentar la regla elegida en el docstring.
- [ ] **Step 4: Ejecutar** las pruebas. Esperado: PASS.
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: simulador por cobertura de reglas"`

---

### Task 2: Backtracking con poda por cota superior

**Files:**
- Create: `src/promptopt/backtracking.py`
- Test: `tests/test_backtracking.py`

**Interfaces:**
- Consumes: `Simulator` (Task 1), `SearchResult`.
- Produces: `backtracking(sim: Simulator, prune: bool = True) -> SearchResult`. `stats` incluye `nodes_visited`, `nodes_pruned`, `leaves_evaluated`. Decisión de diseño: la cota es **sin consultas** (solver de caja blanca sobre `sim.cover` y `sim.req`) y las hojas evaluadas cuestan exactamente N consultas cada una. Cota en un nodo con prefijo fijo: `ub = p_hi*f + p_lo*(1-f)` con `f` = fracción de instancias cuyas reglas están contenidas en (cobertura del prefijo ∪ unión de todas las opciones de las categorías restantes). Se poda si `ub ≤` mejor valor observado hasta ahora. Valor de una hoja = media de las N respuestas observadas. Documentar que el ruido puede provocar podas erróneas y registrar en `stats` si el resultado coincide con `sim.optimum()` (`found_optimum: bool`).

- [ ] **Step 1: Escribir las pruebas que fallan:**
  - `test_no_prune_worst_case`: con `prune=False`, `sim.queries == sim.m * sim.N` y `leaves_evaluated == sim.m`.
  - `test_prune_never_exceeds_worst_case_and_is_exact_without_noise`: con `p_hi=1.0, p_lo=0.0` y `k=3`, `backtracking(sim).best_config == sim.optimum()[0]` y `queries <= m*N`.
  - `test_pruning_reduces_queries`: en una instancia con ρ = 0 y `k=4`, `queries` con poda `<` `m*N`.
  - `test_k1_single_config`: con `k=1` devuelve `(0,0,0,0,0)` y `queries == N`.
- [ ] **Step 2: Ejecutar** `pytest tests/test_backtracking.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar** DFS por categorías en orden, con la cota anterior (precalcular la unión por sufijo de categorías).
- [ ] **Step 4: Ejecutar.** Esperado: PASS.
- [ ] **Step 5: Commit** `git commit -am "feat: backtracking con poda"` (con `git add` previo de los archivos nuevos).

---

### Task 3: Successive Halving

**Files:**
- Create: `src/promptopt/halving.py`
- Test: `tests/test_halving.py`

**Interfaces:**
- Consumes: `Simulator`, `SearchResult`.
- Produces:
  - `halving_cost(m: int, n0: int) -> int`: suma sobre rondas r = 0..R-1, con R = ⌈log₂ m⌉ (R = 0 si m = 1) y c_r candidatos (c_0 = m, c_{r+1} = ⌈c_r/2⌉), de `c_r * n0 * 2**r`.
  - `successive_halving(sim: Simulator, B: int, rng: np.random.Generator) -> SearchResult`. Calcula `n0 = B // (m * R)`; si `n0 < 1` lanza `ValueError`. En cada ronda evalúa cada candidato con `n0 * 2**r` instancias muestreadas con reemplazo, conserva los ⌈c/2⌉ mejores (desempate aleatorio). `stats` incluye `rounds`, `n0`, `cost_formula`.

- [ ] **Step 1: Escribir las pruebas que fallan:**
  - `test_exact_budget_for_power_of_two`: con `k=2` (m = 32, R = 5), `B = 32*n0*5` para `n0 = 4`: `sim.queries == B` exactamente y `== halving_cost(32, 4)`.
  - `test_matches_formula_non_power_of_two`: con `k=3` (m = 243), `queries == halving_cost(243, n0)` y `queries <= B`.
  - `test_independent_of_N`: mismo `k`, `B`, con `n_instances=50` y `n_instances=5000` dan el mismo `queries`.
  - `test_sampling_beyond_N`: con `n_instances=3` y `n0` grande, el conteo sigue igual a `halving_cost`.
  - `test_too_small_budget_raises`: `B < m*R` lanza `ValueError`.
  - `test_k1`: con `k=1` devuelve la única configuración y `queries == 0`.
- [ ] **Step 2: Ejecutar** `pytest tests/test_halving.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar** según la interfaz.
- [ ] **Step 4: Ejecutar.** Esperado: PASS.
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: successive halving"`

---

### Task 4: Coordinate Search

**Files:**
- Create: `src/promptopt/coordinate.py`
- Test: `tests/test_coordinate.py`

**Interfaces:**
- Consumes: `Simulator`, `SearchResult`.
- Produces: `coordinate_search(sim: Simulator, s: int, max_iters: int, rng: np.random.Generator, init: tuple[int, ...] | None = None) -> SearchResult`. `init` por defecto `(0,)*5`. Una pasada recorre las 5 categorías en orden; en cada una evalúa las k opciones con `s` instancias muestreadas y fija la mejor (desempate aleatorio). Termina al completar `max_iters` pasadas o cuando una pasada completa no cambia la configuración. `stats` incluye `iters`, `converged`. Una pasada cuesta exactamente `5*k*s` consultas (no hay caché).

- [ ] **Step 1: Escribir las pruebas que fallan:**
  - `test_query_count_formula`: `queries == stats["iters"] * 5 * k * s` para `k=4, s=10`.
  - `test_independent_of_m`: con el mismo `s` y `max_iters=1`, `k=2` y `k=7` cuestan `5*k*s` respectivamente, y el costo crece linealmente en k, no como k⁵.
  - `test_optimal_when_independent`: con ρ = 0, `p_hi=1.0, p_lo=0.0` y muestra `s = N`, el resultado alcanza `sim.optimum()[1]` en al menos 90% de 20 semillas.
  - `test_max_iters_zero`: devuelve `init` con `queries == 0`.
- [ ] **Step 2: Ejecutar** `pytest tests/test_coordinate.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar.**
- [ ] **Step 4: Ejecutar.** Esperado: PASS.
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: coordinate search"`

---

### Task 5: Reparto de presupuesto (Algoritmo 4)

**Files:**
- Create: `src/promptopt/budget.py`
- Test: `tests/test_budget.py`

**Interfaces:**
- Consumes: `Simulator`, `SearchResult`.
- Produces:
  - `uniform_allocation(sim, B: int, rng) -> SearchResult`: asigna `B // m` consultas a cada configuración (instancias muestreadas con reemplazo), elige la mejor media observada. Lanza `ValueError` si `B < m`.
  - `adaptive_allocation(sim, B: int, rng, delta: float = 0.05) -> SearchResult`: calentamiento de 1 consulta por configuración; luego, en pasos, 1 consulta a cada configuración viva; una configuración se elimina cuando su cota superior de Hoeffding `mean + sqrt(ln(2m/δ)/(2n))` es menor que la mayor cota inferior. Para al agotar B o al quedar una viva. Lanza `ValueError` si `B < m`. `stats` incluye `alive_history`.

- [ ] **Step 1: Escribir las pruebas que fallan:**
  - `test_uniform_cost`: `queries == (B // m) * m` y `<= B`.
  - `test_adaptive_never_exceeds_budget`: `queries <= B`.
  - `test_adaptive_spends_less_on_losers`: en una instancia con `k=3`, la configuración más mala (por `expected_accuracy`) recibe menos consultas que la mejor (exponer `stats["per_config_queries"]`).
  - `test_small_budget_raises`: `B < m` lanza `ValueError` en ambos.
- [ ] **Step 2: Ejecutar** `pytest tests/test_budget.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar.**
- [ ] **Step 4: Ejecutar.** Esperado: PASS.
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: reparto uniforme y adaptativo"`

---

### Task 6: Experimentos de conteo, tiempo y poda

**Files:**
- Create: `src/promptopt/harness.py`, `src/promptopt/plots.py`, `experiments/exp_counts_time.py`, `experiments/exp_pruning.py`
- Test: `tests/test_harness.py`

**Interfaces:**
- Consumes: todos los algoritmos y `Simulator`.
- Produces:
  - `harness.timed(fn: Callable[[], SearchResult]) -> tuple[SearchResult, float]` (segundos, `time.perf_counter`).
  - `harness.fit_constant(ns: np.ndarray, times: np.ndarray, shape: Callable[[np.ndarray], np.ndarray]) -> float` (mínimos cuadrados para c en `times ≈ c * shape(ns)`).
  - `plots.plot_time_vs_n(df, shape_fn, label, path)` y `plots.plot_counts_vs_formula(df, path)` (guardan PNG).
  - Scripts que escriben `results/counts_time.csv` (columnas `algo, k, m, N, B, seed, queries, queries_theory, seconds`) y `results/pruning.csv` (`rho, k, seed, queries, worst_case, nodes_pruned_frac, found_optimum`), y los PNG en `results/`. Usan `k ∈ {2..7}`, al menos 5 semillas, y se ejecutan con `python experiments/<nombre>.py`.

- [ ] **Step 1: Escribir las pruebas que fallan** en `tests/test_harness.py`:
  - `test_timed_returns_seconds_positive`.
  - `test_fit_constant_recovers_known_slope`: para `times = 3*ns**2` y `shape = lambda n: n**2` devuelve ≈ 3 (tolerancia 1e-9).
  - `test_counts_script_smoke`: ejecutar el script con un flag `--quick` (k ∈ {2,3}, 2 semillas) crea el CSV con las columnas listadas y, para cada fila de Halving con m potencia de 2 y de Coordinate, `queries == queries_theory`.
- [ ] **Step 2: Ejecutar** `pytest tests/test_harness.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar** módulos y scripts (con `--quick`). `queries_theory` por algoritmo: backtracking `m*N`, halving `halving_cost`, coordinate `iters*5*k*s`, uniforme `(B//m)*m`.
- [ ] **Step 4: Ejecutar** las pruebas y luego `python experiments/exp_counts_time.py --quick`. Esperado: PASS y CSV/PNG creados en `results/`.
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: experimentos de conteo, tiempo y poda"` (sin los CSV/PNG grandes si `.gitignore` los excluye).

---

### Task 7: Barrido de ρ, reparto de presupuesto y calibración

**Files:**
- Create: `experiments/exp_rho_sweep.py`, `experiments/exp_budget.py`
- Modify: `src/promptopt/simulator.py` (solo parámetros por defecto si hace falta calibrar)
- Test: `tests/test_calibration.py`

**Interfaces:**
- Consumes: `coordinate_search`, `successive_halving`, `backtracking`, `uniform_allocation`, `adaptive_allocation`, `Simulator.optimum`.
- Produces: `results/rho_sweep.csv` (`rho, algo, seed, regret` con `regret = optimum_accuracy - expected_accuracy(best_config)`), `results/budget.csv` (`algo, B, seed, regret`) y sus gráficas (precisión del ganador y varianza contra B, para uniforme vs adaptativo; regret contra ρ para Coordinate Search y Halving).

- [ ] **Step 1: Escribir la prueba de aceptación que falla** en `tests/test_calibration.py`: `test_coordinate_search_fails_when_interacting`: con `k=4, n_instances=200`, 40 semillas, `s = N`, `p_hi=1.0, p_lo=0.0`, el `regret` medio de Coordinate Search con ρ = 0.8 es estrictamente mayor que con ρ = 0, y en al menos el 20% de las semillas con ρ = 0.8 el regret es > 0.
- [ ] **Step 2: Ejecutar** `pytest tests/test_calibration.py -v`. Esperado: FALLA (o PASA si el diseño inicial ya lo cumple; en ese caso pasar al Step 4).
- [ ] **Step 3: Calibrar** la generación de `cover`/`req` y los valores por defecto (r, tamaño de `req[i]`, probabilidades de cobertura cruzada) hasta que pase la prueba, sin romper las pruebas de la Task 1. Registrar los valores finales en el docstring de `simulator.py`.
- [ ] **Step 4: Escribir y ejecutar** los dos scripts de experimentos (con `--quick`). Esperado: CSV y PNG creados; en `budget.csv` el reparto adaptativo no tiene peor regret medio que el uniforme para B pequeño (`B = 2*m`); si ocurre lo contrario, reportarlo tal cual (no ajustar para forzar el resultado).
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: barrido de rho y comparativo de presupuesto"`

---

### Task 8: Notebook reproducible y README

**Files:**
- Create: `notebooks/reproducir.ipynb`, `README.md`, `Makefile` (o `run_all.py`)
- Test: `tests/test_run_all.py`

**Interfaces:**
- Consumes: scripts de Tasks 6 y 7.
- Produces: `run_all.py --quick` ejecuta todos los experimentos y regenera `results/`; el notebook los invoca y muestra las gráficas; el README documenta instalación, semillas y cómo reproducir.

- [ ] **Step 1: Escribir la prueba que falla:** `test_run_all_quick_creates_all_artifacts` verifica que tras `run_all.py --quick` existen `counts_time.csv`, `pruning.csv`, `rho_sweep.csv`, `budget.csv`.
- [ ] **Step 2: Ejecutar** `pytest tests/test_run_all.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar** `run_all.py`, el notebook (celdas que llaman a `run_all`, leen los CSV y muestran PNG) y el README.
- [ ] **Step 4: Ejecutar** la prueba. Esperado: PASS.
- [ ] **Step 5: Ejecutar la corrida completa** `python run_all.py` (sin `--quick`) y confirmar que termina y que las gráficas muestran los 6 tamaños de m.
- [ ] **Step 6: Commit** `git add . && git commit -m "feat: notebook y reproducción completa"`

---

### Task 9: Generador del informe Word

**Files:**
- Create: `informe/build_informe.py`, `informe/texto/` (secciones de texto en Markdown/plain que redacta el equipo)
- Test: `tests/test_informe.py`

**Interfaces:**
- Consumes: CSV y PNG de `results/`.
- Produces: `build_informe(results_dir: Path, text_dir: Path, out_path: Path) -> None` genera un `.docx` con python-docx: portada, sección de formalización, deducción de T(n), reducción desde Max Coverage, algoritmos heurísticos, validación experimental (figuras y tablas insertadas desde `results/`). El texto matemático lo redacta el equipo en `informe/texto/`; el script solo lo ensambla y no inventa cifras.

- [ ] **Step 1: Escribir la prueba que falla:** `test_build_informe_embeds_figures`: con un `results/` y `texto/` mínimos de prueba (tmp_path), el `.docx` se crea, contiene los títulos de sección esperados y tantas imágenes como PNG en `results/`.
- [ ] **Step 2: Ejecutar** `pytest tests/test_informe.py -v`. Esperado: FALLA.
- [ ] **Step 3: Implementar** `build_informe` con python-docx (`add_heading`, `add_paragraph`, `add_picture`, tablas desde los CSV).
- [ ] **Step 4: Ejecutar** la prueba. Esperado: PASS.
- [ ] **Step 5: Commit** `git add . && git commit -m "feat: generador del informe Word"`

---

## Autorrevisión

- **Cobertura del diseño:** simulador con ρ y ruido (T1); backtracking con cota derivada y medición de poda (T2, T6); Halving con costo exacto e independencia de N (T3); Coordinate Search con costo I·5·k·s (T4); uniforme vs adaptativo (T5, T7); ≥ 5 tamaños de n con tiempos y gráficas (T6); barrido de ρ y requisito de aceptación (T7); reproducibilidad (T8); informe Word (T9).
- **Fuera de este plan (el equipo lo redacta):** la demostración de la reducción desde Max Coverage y las deducciones de T(n), que van como texto del informe en `informe/texto/`. El código solo aporta los datos. Variantes opcionales (UCB1, recocido, temperatura) quedan fuera.
- **Pendiente de confirmación con el profesor:** el criterio exacto del reparto adaptativo (T5 usa eliminación por cotas de Hoeffding como decisión nuestra).
