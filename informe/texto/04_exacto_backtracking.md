# 4. Algoritmo exacto: backtracking con poda por cota superior

## 4.1 Descripción

El algoritmo recorre un árbol de profundidad 5. En el nivel d (d = 1..5) se fija la opción de la categoría d. Una hoja es una configuración completa y se evalúa con exactamente N consultas, una por instancia; su valor es la proporción de éxitos observados. En cada nodo interno el algoritmo calcula una cota superior optimista de la precisión que puede alcanzar cualquier hoja de su subárbol y descarta la rama si la cota no supera el mejor valor encontrado hasta el momento.

## 4.2 Cota superior y demostración de validez

Sea π un prefijo de d categorías ya fijadas, y sea U_d la unión de las coberturas de todas las opciones de las categorías d+1..5:

> U_d = ∪_{c > d} ∪_{o ∈ O_c} Cov(c, o)

Sea F_π el número de instancias q con Req(q) ⊆ Cov(π) ∪ U_d, y sea f_π = F_π / N. La cota es

> ub(π) = p_bajo + (p_alto − p_bajo) · f_π

Lema. Para toda configuración x que extiende a π se cumple acc(x) ≤ ub(π).

Demostración. Sea x una extensión de π. Su cobertura es Cov(x) = Cov(π) ∪ ∪_{c>d} Cov(c, x_c), y como cada Cov(c, x_c) ⊆ ∪_{o} Cov(c, o), se tiene Cov(x) ⊆ Cov(π) ∪ U_d. Si x resuelve la instancia q, entonces Req(q) ⊆ Cov(x) ⊆ Cov(π) ∪ U_d, de modo que q es una de las F_π instancias contadas. Luego f(x) ≤ f_π. Como acc(x) = p_bajo + (p_alto − p_bajo)·f(x) es creciente en f (porque p_alto > p_bajo), se concluye acc(x) ≤ ub(π). ∎

Corolario. Podar un nodo con ub(π) ≤ v, donde v es la mejor precisión esperada ya encontrada, no descarta ninguna configuración estrictamente mejor que v. Sin ruido (p_alto = 1, p_bajo = 0) el algoritmo devuelve un óptimo.

Observación sobre el ruido. El valor de una hoja es una media observada y por lo tanto aleatoria, mientras que la cota es sobre la precisión esperada. Con ruido la poda puede descartar por error una rama; la implementación registra si el resultado coincide con el óptimo verdadero (found_optimum) y esa tasa se informa en la validación experimental.

La cota no usa consultas: calcula uniones de conjuntos sobre la estructura de cobertura (algoritmo de referencia con conocimiento de la estructura). Las únicas consultas se gastan en las hojas.

## 4.3 Deducción de T(n)

Conteo de nodos. En el nivel d hay k^d nodos. El número total de nodos es

> Σ_{d=0..5} k^d = (k⁶ − 1)/(k − 1) = Θ(k⁵) = Θ(m)

porque la suma geométrica está dominada por su último término.

Conteo de consultas en el peor caso. En el peor caso la poda no descarta ninguna rama y se evalúan las m = k⁵ hojas. Cada hoja gasta N consultas, así que

> T_consultas(m, N) = m · N = k⁵ · N

Esta igualdad es exacta cuando la poda está desactivada y es una cota superior cuando está activa. En la validación experimental el conteo medido sin poda coincide con m·N en todos los tamaños.

Costo de las cotas. Cada nodo (excepto la raíz) calcula una cota: unir dos subconjuntos de R cuesta O(|R|) y contar las instancias con Req(q) ⊆ Cov cuesta O(N·|R|). Hay Θ(m) nodos, luego las cotas cuestan O(m·N·|R|) operaciones. Con |R| constante, el tiempo total en el peor caso es

> T(m, N) = Θ(m · N)

Como función del tamaño de entrada n = m, T(n) = Θ(n) para N fijo, y Θ(n·N) si se considera también N. En términos de L categorías, m = k^L y el peor caso es Θ(k^L · N), exponencial en L, que es coherente con la NP-dificultad de la Sección 3.

## 4.4 Comportamiento de la poda

La cota es válida pero su eficacia depende de la estructura de las instancias. Cuando las coberturas de las opciones restantes son optimistas respecto a lo que una elección concreta alcanza, la cota casi no corta ramas y el costo se acerca al peor caso m·N. Cuando la cota es ajustada, la poda elimina casi todo el árbol.

El experimento de poda mide, para k ∈ {3, 4, 5, 6}, ρ ∈ {0, 0.25, 0.5, 0.75, 1} y 5 semillas, la fracción de hojas que no se evalúan y las consultas gastadas frente al peor caso m·N (Figura pruning vs rho). En las corridas realizadas la poda descarta más del 98% de las hojas para todos los valores de ρ, y la fracción descartada crece con k (entre 98% y 99% con k = 3 y más de 99.9% con k = 6), de modo que las consultas gastadas son una fracción muy pequeña de m·N. No se observa una tendencia clara de la poda con ρ en estas instancias.

Esto describe estas instancias sintéticas, en las que las precisiones máximas son bajas y la cota se ajusta rápido; no implica que el peor caso sea improbable en otras familias de instancias. El peor caso m·N se mide directamente con la poda desactivada.

Con ruido (p_alto = 0.95, p_bajo = 0.05) el backtracking con poda halló el óptimo verdadero en el 75% al 80% de las corridas con ρ ≤ 0.5 y en el 100% con ρ ≥ 0.75. El resto son podas erróneas causadas por el ruido de las hojas observadas, que la cota esperada no contempla. Este es un costo real de usar valores observados: el algoritmo es exacto sin ruido, no con ruido.
