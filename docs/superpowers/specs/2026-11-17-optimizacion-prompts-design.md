# Diseño: Optimización de configuraciones de prompt bajo presupuesto de consultas

Proyecto semestral 2026-2, Análisis y Diseño de Algoritmos.

## 1. Intención y por qué

El curso evalúa la demostración formal de eficiencia (T(n), cotas, NP-dureza, validación experimental contra la teoría). Que el código corra no basta. Un 45% de la nota es la sustentación, donde el equipo debe defender sin notas la deducción de T(n) del algoritmo exacto.

El proyecto busca la mejor combinación de 5 instrucciones (Rol, Estrategia, Formato, Verificación, Recordatorio) gastando el menor número de consultas a un "LLM". Las instancias son sintéticas y el LLM es un **simulador**. Cada consulta tiene costo contable, así que los conteos medidos se pueden comparar exactamente con las fórmulas.

## 2. Objetivos, no-objetivos, anti-objetivos

**Objetivos**
- Implementar 3 algoritmos (más el comparativo del Algoritmo 4):
  - Backtracking con poda por cota superior (exacto).
  - Successive Halving.
  - Coordinate Search.
  - Comparativo de reparto uniforme vs. adaptativo del presupuesto.
- Deducir T(n) de cada uno y compararlo con el conteo empírico de consultas y con el tiempo medido.
- Demostrar la reducción polinomial desde Cobertura Máxima.
- Generar instancias de al menos 5 tamaños de n, medir tiempos y graficar.
- Producir un informe en Word con deducciones y gráficas reales.

**No-objetivos**
- No se corre un LLM real ni se usa GPU (queda como extensión futura).
- No se implementan UCB1, recocido simulado ni algoritmo genético (extras opcionales, solo si sobra tiempo).

**Anti-objetivos (fracaso aunque el código corra)**
- Reportar "tardó X segundos" sin T(n) formal.
- Resultados escritos a mano en el informe, o curvas teóricas ajustadas a los datos en lugar de deducidas.
- Un simulador en el que Coordinate Search siempre sea óptimo (volvería vacío el análisis de óptimos locales).

## 3. Restricciones

- Python, ejecución local o en Colab.
- Todo reproducible con semilla fija.
- El informe final va en Word (.docx).
- Fecha de entrega final: semana 9 del cronograma.

## 4. Enfoques considerados

| Enfoque | Descripción | Veredicto |
|---|---|---|
| A. Cobertura de reglas | Cada opción cubre un subconjunto de reglas. Una instancia se resuelve si la unión cubre sus reglas. | Fiel a la reducción de Max Coverage. |
| B. Probabilidades independientes | Efectos aditivos por opción. | Descartado: la poda y los óptimos locales quedan sin contenido. |
| **C. A + parámetros de independencia y ruido** | A, más ρ (solapamiento/interacción entre opciones) y ruido. | **Elegido por el equipo.** Permite barrer ρ y mostrar el mejor y el peor caso. |

## 5. Diseño

### 5.1 Definiciones (tamaño de la entrada)

- 5 categorías; la categoría c tiene k_c opciones. Se usa k_c = k para todas, así que **m = k^5** (número de configuraciones).
- **N**: número de instancias de búsqueda.
- **B**: presupuesto máximo de consultas.
- **n principal = m**, con k ∈ {2, 3, 4, 5, 6, 7}, es decir m ∈ {32, 243, 1024, 3125, 7776, 16807}. N se reporta como segundo eje.

### 5.2 Simulador

- Universo de reglas U de tamaño r.
- Cada instancia i exige un subconjunto R_i ⊆ U.
- Cada opción o de la categoría c cubre un subconjunto S_o ⊆ U.
- Una configuración cubre la unión de las S_o de sus 5 opciones.
- Una consulta (configuración, instancia) devuelve un Bernoulli:
  - probabilidad p_alto si R_i ⊆ cobertura de la configuración;
  - probabilidad p_bajo (ruido) en caso contrario.
- Cada consulta incrementa un contador global. Superar B lanza un error.
- **ρ ∈ [0,1]** controla la interacción:
  - ρ = 0: cada categoría es dueña de un bloque disjunto de reglas. Las instrucciones son independientes y Coordinate Search es óptimo.
  - ρ alto: las reglas solo se cubren con combinaciones entre categorías, lo que produce óptimos locales.
- **Requisito de aceptación:** para algún ρ del barrido, Coordinate Search debe quedar estrictamente por debajo del óptimo con frecuencia medible.
- El óptimo verdadero se calcula por fuerza bruta sobre la tabla de cobertura, sin ruido. Sirve solo como referencia para medir calidad y nunca cuenta como consulta.

### 5.3 Algoritmos y análisis esperado

1. **Backtracking con poda.**
   - Árbol de profundidad 5.
   - Cota superior optimista en un nodo: instancias ya resolubles más instancias que aún podrían resolverse con la cobertura máxima posible de las categorías restantes.
   - Peor caso: Θ(m · N) consultas, es decir Θ(k^5 · N).
   - Se debe derivar la cota y medir empíricamente la fracción de nodos podados frente a ese peor caso.
2. **Successive Halving.**
   - R = log₂ m rondas; la ronda r tiene m/2^r candidatos.
   - El costo por ronda queda constante, por lo que se debe demostrar el total exacto.
   - Con n₀ preguntas en la primera ronda y duplicando cada ronda, el costo por ronda es (m/2^r)·(n₀·2^r) = m·n₀. El total es T = m·n₀·log₂ m. Fijando n₀ = B/(m·log₂ m) consume exactamente B consultas.
   - La "independencia" que exige el enunciado debe ser de N (el tamaño del conjunto de instancias): el costo solo depende de m, n₀ y B. Esto es una **deducción nuestra**, porque el símbolo no aparece en el texto del profesor.
3. **Coordinate Search.**
   - Cada pasada hace 5·k·s evaluaciones (s = muestra por evaluación).
   - Para I iteraciones: T = I·5·k·s.
   - Análisis analítico del riesgo de óptimos locales, respaldado por el barrido de ρ.
4. **Reparto de presupuesto (Algoritmo 4).** Uniforme (B/m por configuración) frente a adaptativo, sobre el mismo B, con gráficas empíricas de precisión del ganador elegido y varianza.

### 5.4 Reducción formal

Max Coverage ≤ₚ nuestro problema. Universo ↔ reglas, subconjuntos ↔ opciones de instrucción, k ↔ número de categorías y presupuesto. Se redacta como demostración en el informe.

**Cuidado a resolver en la redacción:** el problema tiene 5 categorías con una opción por categoría, mientras que Max Coverage elige k subconjuntos libres. La reducción debe mostrar la construcción exacta, usando una categoría por subconjunto elegible y una opción "vacía" para no elegir.

### 5.5 Estructura del repositorio

```
src/promptopt/   simulator.py, backtracking.py, halving.py, coordinate.py, budget.py
experiments/     scripts por experimento (conteo, tiempo, poda, barrido ρ, uniforme vs adaptativo)
notebooks/       reproduce todas las gráficas
results/         CSV y PNG generados (no se escriben a mano)
informe/         informe .docx
tests/           pruebas de conteo de consultas y correctitud
docs/superpowers/specs/   este documento
```

### 5.6 Experimentos y validación

- Para cada algoritmo se compara el conteo medido de consultas con la fórmula teórica; el conteo debe coincidir con la fórmula, salvo variaciones con explicación.
- Tiempo medido contra n en 6 tamaños, superpuesto con la curva T(n) deducida (ajustando solo la constante).
- Barrido de ρ y de ruido.
- Repeticiones con varias semillas para obtener intervalos de confianza.

## 6. Entregables (según el enunciado)

Informe técnico en Word, código reproducible con gráficas de tiempo contra n (≥5 tamaños), sustentación grupal de 15 a 20 minutos y sustentación individual.

## 7. Cronograma resumido

- Semana 1: formalización escrita, sin código.
- Semanas 2 a 4: exacto y deducción de su T(n).
- Semanas 6 a 7: heurísticas y cotas.
- Semana 8: experimentación.
- Semana 9: entrega y sustentación.

## 8. Decisiones del autor que el equipo debe revisar

- Elección de p_alto, p_bajo, r y la forma exacta en que ρ solapa las reglas (a calibrar hasta cumplir el requisito de aceptación de 5.2).
- n principal = m con k ∈ {2,…,7}.
- Estructura de carpetas.
- Versión inicial de la cota superior del backtracking, que se refinará al derivarla formalmente.

## 9. Pendientes abiertos

- Las fórmulas del enunciado salen en blanco en las imágenes y en el texto pegado (T de backtracking, costo de Successive Halving, T de Coordinate Search, T del reparto uniforme). Las usadas aquí son deducciones a partir de la mecánica descrita; confirmar con el Word/PDF original o con el profesor, sobre todo de qué variable debe ser independiente Successive Halving.
- Deducciones usadas hasta confirmar: backtracking peor caso Θ(m·N); Coordinate Search I·5·k·s por I iteraciones, independiente de m = k^5; reparto uniforme B (B/m por configuración).
- Definir el criterio de adaptabilidad del Algoritmo 4 (por ejemplo, Successive Halving como esquema adaptativo, o un esquema de umbral).
