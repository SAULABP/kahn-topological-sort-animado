# Guion de narración

Cada número es un **punto de voz** del video: el audio `audio/NN.wav` suena justo cuando aparece ese texto en pantalla, y el texto siguiente espera a que termine la frase. La numeración la genera `VideoCompleto` en orden; si se agrega o quita un texto en las escenas, hay que renumerar los audios.

## Cómo se generó el audio

- Voz generada con ElevenLabs, modelo Eleven v4, una generación por bloque (A a G) con `[long pause]` entre frases.
- Cada bloque se cortó en sus frases usando esas pausas largas (las pausas internas de una frase son más cortas).
- Los clips se aceleraron un 4 % (`atempo=1.04`, sin cambiar el tono) y se subieron 6 dB para que el video dure menos de 5 minutos y se escuche bien.

## Bloque A: Intro y motivación

| # | En pantalla | Narración |
|---|---|---|
| 1 | (título, proyecto e integrantes) | ¿Alguna vez armaste tu matrícula sin saber qué curso llevar primero? Ese problema tiene nombre: ordenamiento topológico. Hoy veremos cómo resolverlo con el algoritmo de Kahn. |
| 2 | Para llevar algunos cursos, primero debemos aprobar sus prerrequisitos. | Para llevar algunos cursos, primero debemos aprobar sus prerrequisitos. Por ejemplo, esta es una parte de la malla de Ciencia de Datos. |
| 3 | Cada flecha va de un prerrequisito al curso que lo necesita: primero Programación II, después Programación III | Cada flecha va de un prerrequisito al curso que lo necesita. |
| 4 | El reto: poner los cursos en una lista donde cada uno aparezca después de todos sus prerrequisitos | El reto: ordenar los cursos de modo que cada uno vaya después de sus prerrequisitos. |
| 5 | ✗ Esta lista no sirve: ML aparece antes que su prerrequisito Estad. I | Esta lista no sirve: Machine Learning va antes que Estadística uno, su prerrequisito. |
| 6 | Buscamos un orden que respete todas las flechas. Ojo: no es un horario; no decide cuántos cursos llevar por ciclo | Ojo: no buscamos un horario, solo un orden que respete todas las flechas. |
| 7 | Con 7 cursos se puede probar a mano. Con una malla completa, ¿cómo podemos determinar ese orden automáticamente? | Con siete cursos se puede a mano. Con una malla completa, ¿cómo lo hacemos automáticamente? |
| 8 | Aquí entra en acción el algoritmo de Kahn | Aquí entra en acción el algoritmo de Kahn. |
| 9 | Para entender la idea, empecemos con solo 4 de estos cursos | Para entender la idea, quedémonos con solo cuatro cursos. |

## Bloque B: Conceptos: grafo, DAG y orden topológico

| # | En pantalla | Narración |
|---|---|---|
| 10 | Esto es un grafo: cada curso es un nodo (o vértice) y cada flecha, una arista dirigida | Esto es un grafo: cada curso es un nodo, y cada flecha, una arista dirigida. |
| 11 | Si al seguir las flechas nunca puedes volver al punto de partida, el grafo no tiene ciclos: es un DAG (grafo dirigido acíclico) | Si siguiendo las flechas nunca vuelves al inicio, no hay ciclos: es un grafo dirigido acíclico, o DAG. |
| 12 | Un orden topológico pone todos los nodos en fila de modo que cada flecha apunte hacia adelante | Un orden topológico los pone en fila con todas las flechas hacia adelante. |
| 13 | No siempre es único: Estad. I y Prog II no dependen entre sí, así que también pueden ir en el otro orden | Y no es único: Estadística uno y Programación dos no dependen entre sí. |

## Bloque C: La idea de Kahn con 4 cursos

| # | En pantalla | Narración |
|---|---|---|
| 14 | 1. Contamos las flechas que llegan a cada curso: su grado de entrada. Es la cantidad de prerrequisitos que todavía le faltan | Kahn empieza contando las flechas que llegan a cada curso: su grado de entrada, es decir, cuántos prerrequisitos le faltan. |
| 15 | 2. Un curso con grado 0 no espera a nadie: ya puede ir en el orden. Entra a la cola de disponibles | Un curso con grado cero no espera a nadie: entra a una cola de disponibles. |
| 16 | 3. Sacamos el primero de la cola y lo ponemos en el orden. Sus flechas se cumplen: cada curso que lo necesitaba baja su grado en 1 | Luego repite: saca el primero de la cola, lo pone en el orden, y cada curso que lo necesitaba baja su grado en uno. |
| 17 | Sale Prog I de la cola y pasa al orden | Sale Programación uno. |
| 18 | Se cumple Prog I → Prog II: a Prog II ya no le falta ningún prerrequisito. Grado 0: entra a la cola | Programación dos ya no tiene pendientes: grado cero, entra a la cola. |
| 19 | Se cumple Prog I → Estad. I: a Estad. I ya no le falta ningún prerrequisito. Grado 0: entra a la cola | Lo mismo pasa con Estadística uno. |
| 20 | Prog II y Estad. I están disponibles a la vez: cualquiera podría ir primero. Kahn toma el que llegó antes a la cola | Hay dos disponibles a la vez; cualquiera podría ir primero. Kahn toma el que llegó antes. |
| 21 | Sale Prog II de la cola y pasa al orden | Sale Programación dos. |
| 22 | Se cumple Prog II → ML, pero a ML todavía le falta Estad. I. Grado 1: aún no puede entrar | Machine Learning baja a uno: todavía le falta Estadística uno, así que no entra. |
| 23 | Sale Estad. I de la cola y pasa al orden | Sale Estadística uno. |
| 24 | Se cumple Estad. I → ML: a ML ya no le falta ningún prerrequisito. Grado 0: entra a la cola | Ahora sí: a Machine Learning ya no le falta nada, y entra. |
| 25 | Sale ML de la cola y pasa al orden | Sale Machine Learning, |
| 26 | Ningún curso depende de ML | y ningún curso depende de él. |
| 27 | La cola quedó vacía y salieron los 4 cursos: el orden de abajo es un orden topológico | La cola quedó vacía con los cuatro cursos ordenados: un orden topológico. |
| 28 | No es el único: Prog I, Estad. I, Prog II, ML también respeta todas las flechas | Intercambiar Programación dos y Estadística uno también valdría. |

## Bloque D: La malla completa

| # | En pantalla | Narración |
|---|---|---|
| 29 | Ahora la malla completa: vuelven Cálculo, Prog III y AED | Ahora volvamos a la malla completa. |
| 30 | Contamos otra vez los grados de entrada | Contamos de nuevo los grados de entrada. |
| 31 | Prog I y Cálculo no tienen prerrequisitos: entran a la cola | Programación uno y Cálculo no tienen prerrequisitos: los dos entran. |
| 32 | Sale Prog I: Prog II llega a 0 y entra · Estad. I aún espera a Cálculo | Sale Programación uno: libera a Programación dos, pero Estadística uno aún espera a Cálculo. |
| 33 | Sale Cálculo: Estad. I llega a 0 y entra | Sale Cálculo, y ahora Estadística uno sí puede entrar. |
| 34 | Sale Prog II: Prog III llega a 0 y entra · ML aún espera a Estad. I | El resto sigue la misma regla, hasta procesar los siete cursos. |
| 35 | Sale Estad. I: ML llega a 0 y entra | *(sin voz)* |
| 36 | Sale Prog III: AED llega a 0 y entra | *(sin voz)* |
| 37 | Sale ML: ningún curso depende de él | *(sin voz)* |
| 38 | Sale AED: ningún curso depende de él | *(sin voz)* |
| 39 | La cola quedó vacía y salieron los 7 cursos: el orden de abajo es un orden topológico | Cola vacía y siete de siete cursos: un orden válido para toda la malla. |

## Bloque E: Caso con ciclo

| # | En pantalla | Narración |
|---|---|---|
| 40 | ¿Y si hubiera un ciclo? Supongamos (caso inventado) que AED también exigiera haber aprobado ADA | ¿Y si hubiera un ciclo? Supongamos, en un caso inventado, que AED también exigiera ADA. |
| 41 | Aplicamos Kahn igual que antes | Aplicamos Kahn igual que antes. |
| 42 | Sale Prog III de la cola y pasa al orden | Sale Programación tres, |
| 43 | Se cumple Prog III → AED, pero a AED todavía le falta ADA. Grado 1: aún no puede entrar | y AED baja a uno, pero todavía le falta ADA. |
| 44 | La cola quedó vacía, pero solo salió 1 de 4 cursos | La cola se vació con solo uno de cuatro cursos procesados. |
| 45 | AED y ADA forman un ciclo: se esperan entre sí, así que su grado nunca llega a 0 | AED y ADA forman un ciclo: cada uno espera al otro, y su grado nunca llega a cero. |
| 46 | El curso Comp. Paralela no está en el ciclo, pero depende de él: queda bloqueado | Computación Paralela no está en el ciclo, pero depende de él: queda bloqueado. |
| 47 | Si salen menos cursos que los que tiene el grafo, hay un ciclo: no existe un orden topológico completo | Si salen menos cursos que los del grafo, hay un ciclo: no existe orden topológico completo. |

## Bloque F: Complejidad

| # | En pantalla | Narración |
|---|---|---|
| 48 | ¿Cuánto trabajo hace Kahn? Repetimos la malla y marcamos cada vez que se usa un vértice o una arista | ¿Cuánto trabajo hace Kahn? Marquemos cada vértice y cada arista que usa. |
| 49 | Cada vértice sale una sola vez: entra a la cola solo cuando su grado llega a 0, y el grado nunca vuelve a subir | Cada vértice sale una sola vez: entra solo cuando su grado llega a cero, y el grado nunca sube. |
| 50 | Cada arista u → v se examina una sola vez: cuando sale u, y u sale una sola vez | Y cada arista se examina una sola vez: cuando sale su origen. |
| 51 | Sumando todo el trabajo | *(sin voz)* |
| 52 | Las constantes no cambian el orden de crecimiento: V + E ≤ V + 2E ≤ 2(V + E), así que el costo es O(V + E) | En total: contar grados cuesta E, sacar vértices V y examinar aristas E: V más dos E. Las constantes no cambian el orden de crecimiento: Kahn es O de V más E. |
| 53 | Sin la cola, buscar cada vez un vértice con grado 0 revisando los V vértices costaría O(V) por paso: O(V² + E) en total | Sin la cola, buscar cada vez un vértice con grado cero costaría O de V al cuadrado. |
| 54 | La traza y la animación son solo para el video: no forman parte del costo del algoritmo | *(sin voz)* |

## Bloque G: Cierre

| # | En pantalla | Narración |
|---|---|---|
| 55 | (créditos) | En resumen, Kahn encuentra un orden que respeta todas las dependencias, o descubre que un ciclo lo impide. Y lo hace sin mirar nunca la malla entera: solo se pregunta, curso por curso, ¿todavía le falta algo? Gracias por ver. |
