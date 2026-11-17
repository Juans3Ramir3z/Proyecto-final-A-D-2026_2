# 1. Formalización del problema

## 1.1 Escenario

Un sistema conversacional debe responder solicitudes cumpliendo reglas de formato y restricciones de contenido. Para mejorar su tasa de éxito sin reentrenar el modelo se antepone texto instruccional organizado en 5 categorías discretas: Rol, Estrategia, Formato, Verificación y Recordatorio. Cada categoría ofrece k opciones de instrucción, y una configuración elige exactamente una opción por categoría. Evaluar una configuración sobre una solicitud requiere una consulta al modelo, que consume tiempo de GPU. El problema consiste en encontrar la mejor configuración minimizando el número total de consultas.

## 1.2 Definiciones

Sea C = {1, …, 5} el conjunto de categorías y O_c = {1, …, k} las opciones de la categoría c. Una configuración es una tupla x = (x_1, …, x_5) con x_c ∈ O_c. El conjunto de configuraciones candidatas tiene tamaño

> m = |𝒳| = k⁵

Sea Q = {q_1, …, q_N} el conjunto de instancias de prueba (solicitudes) disponibles para la búsqueda, y sea B ∈ ℕ el presupuesto máximo de consultas al modelo. Una consulta es un par (x, q) y devuelve un valor aleatorio Y(x, q) ∈ {0, 1}, donde 1 significa que la respuesta cumplió todas las reglas de la solicitud (evaluación todo-o-nada).

La precisión esperada de una configuración es

> acc(x) = (1/N) · Σ_{i=1..N} P[ Y(x, q_i) = 1 ]

## 1.3 Tamaño de la entrada

El tamaño de entrada principal es n = m = k⁵, el número de configuraciones candidatas, que es la cantidad que crece cuando el problema se vuelve más grande y la que determina el costo de una búsqueda exhaustiva. El segundo parámetro es N, el número de instancias de prueba. El presupuesto B es un dato del problema, no una medida de su tamaño.

Observación sobre la representación. La entrada se puede describir con 5·k opciones y N instancias, que es un tamaño polinomial en k, mientras que el espacio de búsqueda es k⁵. Con exactamente 5 categorías, k⁵ es un polinomio en k; la explosión exponencial aparece cuando el número de categorías L forma parte de la entrada, porque entonces m = k^L. Esta distinción se retoma en la Sección 3, donde la NP-dificultad se demuestra para la generalización con L categorías.

## 1.4 Entrada, salida y objetivo

- Entrada: el conjunto de configuraciones 𝒳, el conjunto de instancias Q y el presupuesto B.
- Salida: una asignación de consultas b : 𝒳 → ℕ con Σ_x b(x) ≤ B, y la selección de una configuración ganadora x* ∈ 𝒳.
- Objetivo: maximizar la precisión esperada de la configuración elegida sin exceder el presupuesto:

> maximizar acc(x*)   sujeto a   Σ_{x∈𝒳} b(x) ≤ B

Como acc(x) no se conoce y solo se estima con consultas ruidosas, la calidad de un algoritmo se mide con el regret acc(x_opt) − acc(x*), donde x_opt es el óptimo verdadero (conocido en el simulador).
