# 7. Conclusiones y limitaciones

## 7.1 Qué se demostró

- Formalización: el tamaño de entrada principal es n = m = k⁵ (con N como segundo parámetro) y el objetivo es maximizar la precisión esperada con a lo sumo B consultas.
- Dificultad: la versión con L categorías es NP-completa por reducción desde Cobertura Máxima. Con 5 categorías fijas el problema es polinomial, Θ(k⁵·N), y esa distinción es parte del resultado.
- Algoritmo exacto: el backtracking con poda tiene peor caso exacto m·N consultas (Θ(k⁵·N)), con una cota superior válida que nunca descarta una configuración estrictamente mejor. Sin ruido devuelve un óptimo.
- Successive Halving: costo exacto n₀·m·log₂ m cuando m es potencia de 2, independiente de N, y Θ(n₀·m·log m) en general. Cuando m no es potencia de 2 hay que ajustar n₀ para no exceder B.
- Coordinate Search: costo I·5·k·s, lineal en k = m^(1/5), pero sin garantía de aproximación: el óptimo local puede tener una fracción arbitrariamente pequeña de la precisión óptima.
- Los conteos medidos coinciden exactamente con las fórmulas en los 6 tamaños de n, y el tiempo medido sigue las curvas teóricas ajustadas con una constante.

## 7.2 Cuándo conviene cada algoritmo

- Backtracking con poda: cuando se conoce la estructura de cobertura y se requiere el óptimo. Con ruido puede podar por error, por lo que no es exacto sobre observaciones ruidosas.
- Successive Halving: cuando se quiere un buen candidato con presupuesto fijo y conocido, con garantía probabilística de identificar el mejor y costo independiente de N. Entre los algoritmos de caja negra fue el de menor regret en estos experimentos, a un costo en consultas mucho mayor que el de Coordinate Search.
- Coordinate Search: cuando el presupuesto es muy bajo (su costo crece lineal en k). Es la más barata, pero su calidad depende de la interacción entre instrucciones y puede quedar atrapada en óptimos locales.
- Reparto de presupuesto: el esquema adaptativo mejoró al uniforme con presupuestos escasos, y el uniforme lo superó con presupuestos holgados. Con 20 semillas estas diferencias no son estadísticamente firmes.

## 7.3 Limitaciones

- Los experimentos son sobre un simulador sintético; no se afirma nada sobre el comportamiento de modelos de lenguaje reales.
- Las deducciones de T(n) usadas para Halving, Coordinate Search y el reparto uniforme son del equipo, a partir de la mecánica descrita en el enunciado, ya que las fórmulas del enunciado no estaban legibles.
- La cota de Karnin, Koren y Somekh (2013) y la inaproximabilidad de Feige (1998) están citadas pero sus enunciados exactos deben verificarse en las fuentes.
- El criterio del reparto adaptativo es una decisión del equipo; el enunciado no lo fija.
- La validación temporal se apoya en 6 tamaños y 5 repeticiones; el conteo de consultas es la evidencia más sólida.

## 7.4 Trabajo futuro

Correr el mismo protocolo con un modelo de lenguaje real en un entorno con GPU, y evaluar las variantes que el enunciado propone: temperatura como decisión adicional (espacio de 3·k⁵ configuraciones), asignación adaptativa con UCB1 y metaheurísticas como recocido simulado o algoritmo genético.
