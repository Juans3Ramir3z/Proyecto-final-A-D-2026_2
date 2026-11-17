# 5. Algoritmos heurísticos y reparto del presupuesto

## 5.1 Successive Halving (divide y vencerás por rondas)

Descripción. La búsqueda se organiza en R = ⌈log₂ m⌉ rondas. En la ronda r (r = 0, …, R−1) quedan c_r candidatos, con c_0 = m y c_{r+1} = ⌈c_r / 2⌉, y cada uno se evalúa con n₀·2^r consultas sobre instancias muestreadas con reemplazo. Al final de la ronda se conserva la mitad mejor evaluada, usando solo las muestras de esa ronda. Tras R rondas queda un candidato, el ganador.

Deducción del costo cuando m es potencia de 2. Si m = 2^R, entonces c_r = m / 2^r y el costo de la ronda r es

> c_r · n₀ · 2^r = (m / 2^r) · n₀ · 2^r = m · n₀

El costo por ronda es constante, igual a m·n₀. Con R = log₂ m rondas el costo total exacto es

> T(m, n₀) = Σ_{r=0..R−1} m · n₀ = n₀ · m · log₂ m

Presupuesto exacto. Fijando n₀ = B / (m · log₂ m), el algoritmo consume exactamente

> n₀ · m · log₂ m = B

consultas. El costo no depende de N: las instancias se muestrean con reemplazo, así que N solo afecta la calidad de la estimación y no el número de consultas. Esto confirma la complejidad independiente de N que exige el enunciado.

Caso general (m no potencia de 2). Por inducción se verifica que c_r = ⌈m / 2^r⌉. El costo es

> T(m, n₀) = n₀ · Σ_{r=0..R−1} 2^r · ⌈m / 2^r⌉

Como ⌈m / 2^r⌉ < m / 2^r + 1, se cumple

> n₀ · m · R ≤ T(m, n₀) < n₀ · (m · R + 2^R) < n₀ · m · (R + 2)

porque 2^R < 2m. Luego T = Θ(n₀ · m · log m). La fórmula n₀ = B/(m log₂ m) puede exceder B en este caso: con m = 243 (R = 8) el costo con n₀ = 1 es 243 + 244 + 244 + 248 + 4·256 = 2003 (no 243·8 = 1944), y con B = 20000 la fórmula daría n₀ = 10 y un costo de 20030 > 20000. La implementación usa n₀ = ⌊B / T(m, 1)⌋, que nunca excede B y coincide con n₀ = B/(m log₂ m) cuando m es potencia de 2. En los experimentos el conteo medido coincide con T(m, n₀) en todos los tamaños.

Garantía. Si las recompensas de cada configuración son independientes y acotadas en [0, 1] (aquí, Bernoulli con media acc(x)), Karnin, Koren y Somekh (2013) acotan la probabilidad de que Successive Halving no devuelva la mejor opción en función del presupuesto y de la dificultad de la instancia (la cantidad H₂ = max_i i / Δ_(i)², con Δ_(i) la brecha entre la i-ésima mejor opción y la mejor). La cota decrece exponencialmente en B / (H₂ · log₂ m). Esta referencia debe verificarse (enunciado exacto y constantes) antes de citarla en la entrega final. La garantía es probabilística sobre identificar la mejor configuración, no una razón de aproximación determinista.

## 5.2 Coordinate Search (búsqueda local por descenso de coordenadas)

Descripción. Parte de una configuración inicial. Para cada categoría, en orden, evalúa las k opciones con una muestra de s instancias (la misma muestra para las k opciones), fija la mejor y pasa a la siguiente. Termina tras I pasadas o cuando una pasada completa no cambia la configuración.

Deducción del costo. En una categoría se evalúan k opciones con s consultas cada una: k·s consultas. Una pasada recorre 5 categorías: 5·k·s consultas. Para I pasadas:

> T(k, s, I) = I · 5 · k · s

El costo es lineal en k = m^(1/5), no en m = k⁵, y no depende de N ni de B. Es una reducción drástica frente a las m·N consultas del exacto. El conteo medido coincide con esta fórmula en todos los tamaños.

Riesgo de óptimos locales. Una configuración es un óptimo local si ninguna modificación de una sola categoría mejora la precisión. La búsqueda por coordenadas puede detenerse ahí aunque exista una configuración mucho mejor.

Ejemplo. Dos categorías A y B con dos opciones cada una y reglas {a, b, c}. Las opciones cubren A1 = {c}, A2 = {a}, B1 = {c}, B2 = {b}. Hay N − 1 instancias que exigen {a, b} y una instancia que exige {c}. La configuración (A1, B1) cubre {c} y resuelve 1 instancia. Cambiar solo A a A2 cubre {a, c} y resuelve 1; cambiar solo B a B2 cubre {b, c} y resuelve 1; ninguna mejora, por lo que (A1, B1) es un óptimo local con precisión 1/N. La configuración (A2, B2) cubre {a, b} y resuelve N − 1, con precisión (N − 1)/N. La razón entre el óptimo local y el óptimo es 1/(N − 1), que tiende a 0, de modo que Coordinate Search no admite ninguna razón de aproximación constante cuando las instrucciones no son independientes.

Caso independiente. Si las reglas que exige cada instancia dependen de una sola categoría, la precisión se descompone como suma de términos, uno por categoría, y optimizar cada categoría por separado alcanza el óptimo en una pasada (sin ruido y con s = N). En el simulador esto no se cumple exactamente ni con ρ = 0, porque las instancias exigen reglas de varias categorías; por eso aparecen óptimos locales ocasionales incluso con ρ = 0.

Evidencia experimental. En una prueba sin ruido (p_alto = 1, p_bajo = 0), con k = 4, N = 200, s = N y 30 semillas, Coordinate Search queda en un óptimo local en cerca de 17% de las semillas con ρ = 0 y en cerca de 63% con ρ = 0.8, con regret medio de 0.002 y 0.16 respectivamente. En el barrido de ρ con ruido y s = 20 consultas por evaluación el efecto de ρ no se distingue con claridad, porque el ruido de muestreo domina; para observarlo se necesita una muestra grande o ausencia de ruido. Esto se informa tal cual en la validación experimental.

## 5.3 Reparto del presupuesto: uniforme frente a adaptativo

Reparto uniforme. Asigna B/m consultas a cada una de las m configuraciones (⌊B/m⌋ en la implementación), de modo que el costo total es ⌊B/m⌋·m ≤ B, es decir, T = O(B). Cada estimación de acc(x) es una media de n = B/m variables de Bernoulli, con varianza p(1 − p)/n. Si n es pequeño la varianza es alta y, por la evaluación todo-o-nada, la probabilidad de observar 0 éxitos en n consultas es (1 − p)^n, lo que hace que configuraciones buenas parezcan tener 0% por ruido. Por ejemplo, con p = 0.1 y n = 2 esa probabilidad es 0.81.

Reparto adaptativo. Da una consulta de calentamiento a cada configuración y luego una consulta por paso a cada configuración aún viva. Una configuración se elimina cuando su cota superior de Hoeffding, media + √(ln(2m/δ) / (2n)), queda por debajo de la mayor cota inferior entre las vivas. Así concentra las consultas en las configuraciones que muestran potencial y deja de gastar en las claramente deficientes. Por construcción nunca excede B. Este esquema es una decisión del equipo; el enunciado no fija el criterio adaptativo.

Resultado experimental. Con k = 3 (m = 243), ρ = 0.5, N = 100 y 20 semillas, el adaptativo logra menor regret medio que el uniforme con presupuestos pequeños (B = 2m y B = 4m), y el uniforme lo supera con presupuestos grandes (B ≥ 8m, con la mayor diferencia en B = 32m). Una explicación plausible, que no se ha verificado con un experimento aparte, es que la cota de Hoeffding con unión sobre m configuraciones es conservadora y puede eliminar por error a la mejor configuración con ruido, mientras que con presupuesto grande el uniforme ya estima bien todas las configuraciones. La conclusión es que ningún esquema domina: el adaptativo conviene cuando el presupuesto es escaso, y esto se respalda con la gráfica de regret contra B y su varianza entre semillas.
