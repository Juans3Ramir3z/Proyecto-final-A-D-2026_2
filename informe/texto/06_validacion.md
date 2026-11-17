# 6. Validación experimental

## 6.1 Protocolo

Todos los experimentos usan el simulador de la Sección 2 con semillas fijas y se regeneran con el comando python run_all.py. Hay cuatro experimentos.

- Conteo y tiempo: k ∈ {2, 3, 4, 5, 6, 7}, es decir, n = m ∈ {32, 243, 1024, 3125, 7776, 16807}, con N = 50 instancias, ρ = 0.5 y 5 semillas. Parámetros: Halving con n₀ = 4 (B = 4·T(m, 1)); Coordinate Search con s = 10 y máximo 3 pasadas; reparto uniforme y adaptativo con B = 8·m.
- Poda: k ∈ {3, 4, 5, 6}, ρ ∈ {0, 0.25, 0.5, 0.75, 1}, N = 50 y 5 semillas.
- Barrido de ρ: k = 4 (m = 1024), N = 100, ρ ∈ {0, 0.2, …, 1} y 20 semillas, con Coordinate Search (s = 20, hasta 10 pasadas), Halving (n₀ = 4) y backtracking con poda.
- Presupuesto: k = 3 (m = 243), N = 100, ρ = 0.5, B ∈ {2, 4, 8, 16, 32}·m y 20 semillas, comparando reparto uniforme y adaptativo.

El tiempo se mide con un reloj de alta resolución (perf_counter) y excluye la construcción del simulador. Las máscaras de resolución de cada configuración se calculan en su primera consulta y ese costo sí está incluido en el tiempo.

[[RESULTADOS]]

## 6.2 Consultas medidas frente a la función teórica

Los conteos de consultas son deterministas, por lo que se comparan exactamente con las fórmulas deducidas (tabla y figura anteriores). En las 30 corridas por algoritmo (6 tamaños por 5 semillas):

- Backtracking sin poda: el conteo medido es igual a m·N en todas las corridas, por ejemplo 840350 consultas con m = 16807 y N = 50.
- Successive Halving: el conteo medido es igual a T(m, n₀) = n₀·Σ_r 2^r·⌈m/2^r⌉ en todas las corridas.
- Coordinate Search: el conteo medido es igual a I·5·k·s en todas las corridas, y crece de forma lineal en k (de 280 consultas con m = 32 a 1050 con m = 16807, en promedio), no en m.
- Reparto uniforme: el conteo medido es igual a ⌊B/m⌋·m en todas las corridas. El adaptativo consume exactamente B en todas las corridas de este experimento, es decir, el criterio de eliminación no logró detenerse antes de agotar el presupuesto.
- Backtracking con poda: gasta entre 90 consultas (m = 32) y unos 430 (m = 7776) en promedio, frente a un peor caso de 1600 a 840350, y nunca supera m·N.

La coincidencia exacta es la evidencia más sólida de la validación, porque no depende de la máquina ni del ruido.

## 6.3 Tiempo medido frente al crecimiento teórico

Para cada algoritmo se ajustó por mínimos cuadrados una sola constante c en tiempo ≈ c·f(m), donde f es la función de la deducción, y se graficó la curva ajustada contra el tiempo medido (figuras time_*).

- Backtracking sin poda, f = m·N: c = 4.2·10⁻⁶ s por par (configuración, instancia), R² = 0.996. Es decir, unos 4 µs por consulta simulada.
- Halving, f = m·log₂ m: c = 1.6·10⁻⁵, R² = 0.9993.
- Reparto uniforme, f = m: c = 4.2·10⁻⁵, R² = 0.994.
- Coordinate Search, f = k = m^(1/5): c = 7.0·10⁻⁴, R² = 0.994, con tiempos de milisegundos.

Los errores relativos del ajuste son menores a 16% en todos los puntos. Las curvas ajustadas con la forma teórica siguen los datos; el tiempo crece como el número de consultas porque cada consulta simulada cuesta un tiempo casi constante.

Alcance de esta evidencia. Hay solo 6 tamaños y 5 repeticiones por punto. Para Halving, un ajuste lineal en m también da un R² alto (0.996 frente a 0.9993 de m·log₂ m), por lo que el rango de m utilizado distingue claramente de un crecimiento cuadrático (R² = 0.93) pero no separa de forma contundente m·log m de m. Los tiempos de Coordinate Search son de pocos milisegundos y están cerca de la resolución práctica del experimento. Por estas razones, la forma del crecimiento se respalda principalmente con el conteo exacto de consultas (Sección 6.2) y el tiempo se presenta como confirmación coherente, no como prueba independiente.

## 6.4 Poda del backtracking

Ver la Sección 4.4. La poda descarta más del 98% de las hojas en todos los valores de ρ y la fracción descartada aumenta con k. Con ruido, el backtracking halló el óptimo verdadero en el 75% al 80% de las corridas con ρ ≤ 0.5 y en el 100% con ρ ≥ 0.75.

## 6.5 Calidad de la solución y barrido de ρ

Con k = 4 y 20 semillas por valor de ρ, el regret medio (precisión del óptimo menos la de la configuración elegida) fue: backtracking con poda 0.0023, Halving 0.0041 y Coordinate Search 0.070. El gasto medio de consultas fue de unas 420 consultas (backtracking), 2700 (Coordinate Search) y 40960 (Halving).

Por valor de ρ, el regret de backtracking y de Halving baja de 0.005 y 0.007 con ρ = 0 a prácticamente 0 con ρ ≥ 0.8. El de Coordinate Search no muestra una tendencia clara (entre 0.05 y 0.09 para todos los ρ) porque con s = 20 el ruido de muestreo domina sobre el efecto de la interacción. El efecto de ρ sobre los óptimos locales de Coordinate Search sí es visible sin ruido y con s = N (Sección 5.2).

Atención al comparar el costo del backtracking con los otros: calcula su cota con la estructura de cobertura del simulador, sin gastar consultas, mientras que Halving y Coordinate Search solo ven las respuestas del modelo. Su bajo número de consultas no es comparable de forma directa con el de los algoritmos de caja negra.

## 6.6 Reparto del presupuesto: uniforme frente a adaptativo

Regret medio con k = 3, ρ = 0.5 y 20 semillas (adaptativo / uniforme):

- B = 2m: 0.186 / 0.214
- B = 4m: 0.124 / 0.173
- B = 8m: 0.127 / 0.115
- B = 16m: 0.090 / 0.070
- B = 32m: 0.070 / 0.036

El adaptativo es mejor con presupuesto escaso (hasta 4m) y el uniforme lo supera con presupuesto holgado (desde 8m). Las desviaciones estándar entre semillas son comparables a las diferencias en los presupuestos pequeños (por ejemplo 0.147 y 0.142 con B = 2m), así que con 20 semillas la ventaja del adaptativo en B = 2m no es estadísticamente firme; la del uniforme con B = 32m (0.036 frente a 0.070, con desviaciones de 0.053 y 0.070) tampoco es contundente. Para afirmar un ganador por presupuesto harían falta más semillas.

## 6.7 Limitaciones de la validación

- Los resultados son del simulador, no de un modelo de lenguaje real.
- La precisión óptima del simulador depende fuertemente de ρ: en promedio unas 0.12 con ρ = 0, 0.43 con ρ = 0.5 y 0.95 con ρ = 1 (con k = 4 y N = 100). Con ρ alto casi todas las configuraciones son buenas y el regret de todos los algoritmos se aproxima a cero, lo que hace menos informativa esa parte del barrido.
- Solo hay 6 tamaños de n, 5 a 20 semillas por experimento y una sola máquina.
- Las decisiones de diseño (valores de p_alto, p_bajo, número de reglas y probabilidades de cobertura) afectan los valores absolutos; las comparaciones entre algoritmos se hicieron con los mismos parámetros.
