# Segundo parcial
# 1. Perceptrón por Agentes

## Resumen
Proyecto que implementa y simula un perceptrón usando el paradigma de agentes.  
Cada punto es representado por un agente ligero (`PointAgent`) y el `PerceptronModel` contiene el perceptrón, los datos y la lógica de aprendizaje. Incluye una interfaz básica con `matplotlib` (sliders y botones) para ajustar tasa de aprendizaje y número de iteraciones y ver en tiempo real la frontera de decisión.

---

## Objetivo
- Modelar un perceptrón de 2 entradas + bias que aprenda a separar datos 2D linealmente separables.
- Visualizar entrenamiento en tiempo real, coloreando puntos acertados/errados.
- Evaluar el perceptrón en datos de prueba tras el entrenamiento.

---

## Diseño del sistema (arquitectura y agentes)
- **PointAgent**  
  - Tema: datos.  
  - Función: almacena posición `pos` y etiqueta `label` (1 o -1). Es un agente ligero (no hereda necesariamente de `mesa.Agent` para evitar incompatibilidades).
- **PerceptronModel**  
  - Tema: núcleo del perceptrón.  
  - Funciones:
    - Genera datos de entrenamiento y prueba usando una *línea verdadera* aleatoria \(ax + by + c = 0\) para etiquetar puntos.
    - Mantiene `weights` (vector), `bias` (float), `epoch` (contador).
    - `predict(x)`: aplica \(\operatorname{sign}(\mathbf{w}\cdot x + b)\).
    - `step()`: recorre puntos de entrenamiento y aplica la regla de actualización por cada error; incrementa `epoch`.
    - `train(epochs)`: ejecuta `step()` hasta `epochs` o hasta que no haya errores.
    - `evaluate()`: mide porcentaje de aciertos en conjunto de prueba.
- **Interfaz (matplotlib)**  
  - Sliders para `tasa_aprendizaje` y `iteraciones`.
  - Botones `iniciar` y `restablecer`.
  - Dibuja: puntos (verde = correctamente clasificado, rojo = incorrecto), línea verdadera (punteada) y frontera de decisión actual (línea continua).

---

## Flujo de ejecución (cómo funciona)
1. Se instancia `PerceptronModel` → se generan datos de entrenamiento y prueba y se inicializan pesos y bias aleatoriamente.
2. Usuario ajusta sliders (tasa de aprendizaje, número de iteraciones).
3. Al pulsar `iniciar`:
   - `PerceptronModel.train(iters)` ejecuta el entrenamiento.
   - Tras cada epoch (o cada `update_every`) se actualiza la visual: colores de puntos y frontera de decisión.
4. Al terminar el entrenamiento, se calcula la precisión con `evaluate()` y se muestra en pantalla.
5. `restablecer` regenera línea verdadera, datos y pesos.

---

## Implementación (puntos clave del código)
- **Generación de datos**: puntos uniformes en \([-1,1]^2\), etiqueta por signo de \(ax+by+c\).
- **Predicción**: `val = dot(weights, x) + bias`; `return 1 if val >= 0 else -1`.
- **Actualización**: `weights += learning_rate * y * x` y `bias += learning_rate * y`.
- **Visual**: `matplotlib.scatter` para puntos y `plot` para líneas; sliders y botones de `matplotlib.widgets`.

Archivo principal: contiene definición de `PointAgent`, `PerceptronModel`, función `make_plot(model)` con UI y un test headless `_test_headless()`.

---

## Resultados obtenidos (ejecución headless de ejemplo)
Se ejecutó una prueba headless con semilla fija para reproducibilidad (50 puntos de entrenamiento, 200 de prueba, tasa 0.1, max 50 epochs). Valores medidos:

- Pesos iniciales (ejemplo): `[-0.590879, 0.135450]`  
- Bias inicial: `0.095545`  
- Pesos finales tras entrenamiento: `[0.267341, -0.129740]`  
- Bias final: `-0.104455`  
- Epochs usados: `3`  
- Precisión en conjunto de prueba: `98.0%`

> Interpretación: el perceptrón convergió en pocas iteraciones (3 epochs) y alcanzó alta precisión en los puntos de prueba (98%), consistente con datos linealmente separables y una tasa de aprendizaje adecuada.

---
- **Ejemplos de uso**

<img width="2557" height="1428" alt="image" src="https://github.com/user-attachments/assets/24eecd8f-44be-4f53-830c-98f575114dbd" />
<img width="1280" height="695" alt="image" src="https://github.com/user-attachments/assets/c3335270-84c4-4e12-bf72-aa5bdf38df31" />


# 2. Implementación de una calculadora distribuida usando el paradigma de agentes (mesa).  
Cada operador (`+ - * / ^`) es un **agente** autónomo. Recibe la expresión, la transforma a RPN (postfija) y solicita las operaciones a los agentes mediante tareas. La comunicación se realiza con colas de tareas y un mailbox.

---

## Objetivo
- Cada operador es gestionado por un agente.
- Respetar precedencia y asociatividad (shunting-yard → RPN).
- Agentes se comunican por mensajes/tareas y devuelven resultados.
- IOAgent coordina, compone resultados y entrega la respuesta al usuario.

---

## Flujo de ejecución (cómo funciona)
1. El usuario ingresa la expresión completa en la CLI (o GUI).
2. IOAgent tokeniza la expresión (números, operadores, paréntesis).
3. IOAgent aplica shunting-yard → genera RPN respetando precedencia y `right-assoc` para `^`.
4. IOAgent evalúa la RPN:
   1. Si el token es número → push en pila.
   2. Si el token es operador → pop `b`, pop `a`, `request_operation(op, a, b)` → devuelve `task_id`.
   3. IOAgent ejecuta `wait_for_result(task_id)`, que llama `model.step()` en loop hasta obtener resultado o timeout.
   4. Si result ok → push `value` en pila; si error → propaga excepción.
5. Al terminar RPN, la pila debe tener exactamente 1 valor → resultado final.
6. IOAgent muestra el resultado al usuario.

---

## Agentes (tema / función)
- **IOAgent**
  - Tema: interfaz y coordinación.
  - Función: parseo, conversión a RPN, creación de tareas, recolección de resultados.
  - Métodos clave: `tokenize()`, `to_rpn()`, `evaluate_rpn()`, `request_operation()`, `wait_for_result()`.

- **OperationAgent (por operador)**
  - Tema: ejecución de una operación aritmética.
  - Función: mantener `queue`, procesar tarea en `step()`, escribir resultado en `model.results`.
  - Propiedades: `op` (símbolo), `func` (lambda o función).

---
- **Ejemplo de uso**
<img width="1210" height="591" alt="image" src="https://github.com/user-attachments/assets/5b9e92c7-7171-47c1-8c19-8f96732f79c8" />

# 3. Calculadora Científica (Kotlin)

**Resumen**  
Proyecto: calculadora científica en Kotlin con interfaz gráfica (Swing). Soporta operaciones aritméticas básicas, funciones científicas (trigonometría, potencias, raíces, logaritmos, exponenciales), evaluación de expresiones completas (shunting-yard → RPN) y memoria (M+, M-, MR, MC).

---
# Diagrama UML

<img width="2293" height="3162" alt="calculadorakotlin" src="https://github.com/user-attachments/assets/910822b1-0565-432d-ac5d-ae96e11ccbb2" />

---
# El codigo se encuentra adjunto al repositorio con el nombre "calculadoracientifica"
---
# Ejemplos del funcionamiento
1. Ejemplo basico
  - <img width="310" height="404" alt="image" src="https://github.com/user-attachments/assets/4f47185e-ee54-4ac2-86ed-b13fd6e5e56e" />
2. Ejemplo avanzado
  - <img width="311" height="404" alt="image" src="https://github.com/user-attachments/assets/4652ef25-b01a-4363-8291-7a1fe5fb85c7" />
3. Caso de error
  - <img width="312" height="402" alt="image" src="https://github.com/user-attachments/assets/f816aec5-372c-49e8-bef5-7248fcefcd09" />

---

## Principios de Programación Orientada a Objetos aplicados

### Encapsulamiento
- Los estados internos están protegidos mediante atributos privados y métodos públicos.
- Ej.: `Memoria` expone `sumarMemoria`, `restarMemoria`, `leerMemoria`, `limpiarMemoria` y no deja acceder directamente a `valorMemoria`.

### Herencia
- `Calculadora` contiene operaciones básicas: `sumar`, `restar`, `multiplicar`, `dividir`.
- `CalculadoraCientifica` hereda de `Calculadora` y extiende con trigonometría, potencias, raíces, logaritmos y exponenciales.

### Polimorfismo
- Sobrecarga de métodos en `Calculadora` para `Int` y `Double`.
- Interfaz coherente: funciones avanzadas en `CalculadoraCientifica` mantienen la misma semántica para la UI y el evaluador.

---

## Estructura de ficheros (en `src/`)
- `calculadora.kt` — clase `Calculadora` (operaciones básicas).
- `calculadoracientifica.kt` — clase `CalculadoraCientifica` (extensiones científicas).
- `memoria.kt` — clase `Memoria` (M+, M-, MR, MC).
- `solver.kt` — objeto `Solver` (evaluador: shunting-yard → RPN y evaluación).
- `calcular.kt` — clase `Calcular` (GUI con Swing, botones, pantalla).
- `Main.kt` — punto de entrada (inicia GUI o pruebas con `--test`).

---

## Flujo de ejecución (cómo funciona)
1. El usuario introduce una expresión en la GUI (o construye con botones).
2. `Calcular` solicita a `Solver` la evaluación de la expresión.
3. `Solver` convierte la expresión infija a RPN (shunting-yard), teniendo en cuenta precedencia, funciones y constantes (`pi`, `e`).
4. `Solver` evalúa la RPN; para operadores y funciones invoca métodos de `CalculadoraCientifica` (respeta modo Grados/Radianes).
5. Resultado devuelto a `Calcular`, que actualiza la UI y guarda `ANS` si corresponde.
6. Memoria gestionada por `Memoria` y accesible desde la UI (`M+`, `M-`, `MR`, `MC`).

---

## Manejo de errores / validaciones
- División por cero → `ArithmeticException`.
- Raíz de número negativo → excepción.
- Logaritmo (≤ 0) → excepción.
- `Solver` valida tokens, paréntesis, aridad de funciones; errores se muestran claramente en la UI.

---

## Interfaz de usuario
- Implementada con **Swing**.
- Botones para dígitos, operadores, funciones científicas, memoria y control.
- Checkbox o indicador para alternar Grados/Radianes.
- Resultado y errores se presentan en etiqueta de estado y cuadros de diálogo.

---
