# 3. Dificultad computacional: reducción desde Cobertura Máxima

## 3.1 Generalización a L categorías

Con exactamente 5 categorías, una búsqueda exhaustiva cuesta Θ(k⁵·N), que es polinomial en k y en N. La dificultad computacional aparece cuando el número de categorías L es parte de la entrada, porque el espacio crece como k^L. Por eso la demostración se hace sobre la generalización con L categorías, que contiene al problema original como el caso L = 5. Esta aclaración evita afirmar algo falso: con L fijo el problema se resuelve en tiempo polinomial.

## 3.2 Problema de decisión

PROMPT-OPT. Entrada: un universo de reglas R; L categorías, cada una con un conjunto de opciones y una cobertura Cov(c, o) ⊆ R por opción; instancias q_1, …, q_N con requisitos Req(q_i) ⊆ R; y un umbral τ ∈ ℕ. Pregunta: ¿existe una configuración x (una opción por categoría) que resuelva al menos τ instancias, es decir, tal que |{ i : Req(q_i) ⊆ Cov(x) }| ≥ τ?

Es el caso sin ruido (p_alto = 1, p_bajo = 0) con presupuesto B ≥ m·N, que no limita nada. Como es un caso particular del problema de optimización con presupuesto, su dificultad se hereda al problema general.

## 3.3 Pertenencia a NP

Dada una configuración x, calcular Cov(x) cuesta O(L·|R|) y comprobar Req(q_i) ⊆ Cov(x) para las N instancias cuesta O(N·|R|). El certificado se verifica en tiempo polinomial, luego PROMPT-OPT ∈ NP.

## 3.4 Cobertura Máxima

COBERTURA MÁXIMA (decisión). Entrada: un universo U, una colección de subconjuntos S_1, …, S_t ⊆ U, un entero K ≤ t y un umbral τ. Pregunta: ¿existen K subconjuntos cuya unión tenga al menos τ elementos? Es NP-completo (se obtiene de Cobertura de Conjuntos, uno de los 21 problemas de Karp, 1972).

## 3.5 La reducción

Dada una instancia (U, S_1..S_t, K, τ) de Cobertura Máxima se construye en tiempo polinomial la siguiente instancia de PROMPT-OPT:

- Reglas: una regla r_u por cada elemento u ∈ U, de modo que R = { r_u : u ∈ U }.
- Instancias de prueba: una instancia q_u por cada elemento u ∈ U, con Req(q_u) = { r_u }. Así N = |U|.
- Categorías: L = K categorías idénticas. Cada categoría tiene t opciones, una por subconjunto, y la opción j cubre Cov(c, j) = { r_u : u ∈ S_j }.
- Umbral: el mismo τ.

El tamaño de la construcción es polinomial: K·t opciones, |U| reglas y |U| instancias.

## 3.6 Corrección

Una configuración x elige una opción por categoría, es decir, una lista de K subconjuntos (posiblemente con repeticiones). Su cobertura es Cov(x) = { r_u : u ∈ S_{x_1} ∪ … ∪ S_{x_K} }. La instancia q_u se resuelve si y solo si r_u ∈ Cov(x), es decir, si y solo si u pertenece a la unión de los subconjuntos elegidos. Por lo tanto, el número de instancias que x resuelve es exactamente |S_{x_1} ∪ … ∪ S_{x_K}|.

(⇒) Si existen K subconjuntos con unión de tamaño ≥ τ, la configuración que elige esos subconjuntos en las K categorías resuelve ≥ τ instancias.

(⇐) Si una configuración resuelve ≥ τ instancias, los K subconjuntos que elige (con repeticiones, que solo reducen la unión) cubren ≥ τ elementos. Si hubiera repeticiones, se completan con subconjuntos cualesquiera sin disminuir la unión, porque K ≤ t.

Luego Cobertura Máxima ≤ₚ PROMPT-OPT, y como Cobertura Máxima es NP-completo, PROMPT-OPT es NP-completo y el problema de optimización es NP-difícil.

## 3.7 Relación con el planteamiento del enunciado

El enunciado propone tomar las reglas de formato como el universo a cubrir y cada opción de instrucción como un subconjunto de reglas. La construcción anterior es un caso particular de ese esquema en el que cada instancia exige una sola regla, lo que hace exacta la correspondencia entre instancias resueltas y elementos cubiertos. Con instancias que exigen varias reglas el objetivo es la cantidad de instancias cuyas reglas quedan todas cubiertas, que es una función de cobertura más general, y el problema sigue siendo al menos tan difícil.

## 3.8 Consecuencias

Si P ≠ NP, no existe un algoritmo exacto con tiempo polinomial en L, k y N para el problema con L variable. Esto justifica el uso de heurísticas. También se sabe que Cobertura Máxima no admite aproximación mejor que 1 − 1/e salvo que P = NP (Feige, 1998), un resultado que limita lo que se puede garantizar para la versión con estructura conocida.
