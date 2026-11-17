# 2. Modelo del simulador

Como el enunciado pide instancias sintéticas, el modelo de lenguaje se reemplaza por un simulador cuyo único propósito es dar a cada consulta un costo contable exacto y un comportamiento aleatorio controlado. Los resultados describen el comportamiento de los algoritmos de búsqueda, no el de un modelo de lenguaje real.

## 2.1 Cobertura de reglas

Existe un universo de r reglas de formato. Cada instancia q_i exige un subconjunto Req(q_i) de esas reglas, de tamaño aleatorio entre 2 y r/2. Cada opción o de la categoría c cubre un subconjunto Cov(c, o) de reglas. Una configuración x cubre la unión de las coberturas de sus 5 opciones:

> Cov(x) = Cov(1, x_1) ∪ … ∪ Cov(5, x_5)

La configuración x resuelve q_i si Req(q_i) ⊆ Cov(x), es decir, si cumple el 100% de sus reglas. Sea f(x) la fracción de instancias que x resuelve.

## 2.2 Ruido de la consulta

Una consulta (x, q_i) devuelve 1 con probabilidad p_alto si x resuelve q_i y con probabilidad p_bajo en caso contrario. Con p_alto = 0.95 y p_bajo = 0.05 por defecto, la precisión esperada es

> acc(x) = p_bajo + (p_alto − p_bajo) · f(x)

que es creciente en f(x). Esta relación monótona se usa en la demostración de la cota del backtracking (Sección 4).

## 2.3 Parámetro de interacción ρ

Cada regla j tiene una categoría dueña (j mod 5). Una opción cubre cada regla de su propia categoría con probabilidad 0.3 y cada regla de otra categoría con probabilidad 0.3·ρ, con ρ ∈ [0, 1]. Con ρ = 0 los bloques de reglas de cada categoría son disjuntos; al aumentar ρ las reglas pueden cubrirse desde varias categorías, lo que crea redundancia y complementariedad entre instrucciones.

Incluso con ρ = 0 las instancias exigen reglas de varias categorías a la vez (una conjunción), por lo que el objetivo no es exactamente separable por categoría. Por eso, con ρ = 0 Coordinate Search puede quedar en un óptimo local con poca frecuencia y poco regret, mientras que con ρ alto esto ocurre mucho más (Sección 5 y Sección 6).

## 2.4 Contador de consultas y verdad exacta

Cada llamada a la consulta incrementa un contador global y, si se fija un presupuesto, lanzar una consulta de más produce un error. El simulador también puede calcular, sin costo, la precisión esperada exacta de cualquier configuración y el óptimo verdadero por fuerza bruta. Estas dos funciones solo se usan para medir el regret y comprobar la correctitud; los algoritmos no las llaman, salvo el backtracking, que usa la estructura de cobertura para calcular su cota (Sección 4).

## 2.5 Reproducibilidad

Todos los generadores usan semilla fija. Los conteos de consultas son deterministas; los tiempos dependen de la máquina.
