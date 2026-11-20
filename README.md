# Topological Sort (Kahn) — Animado

Proyecto 2 del curso CS2023 Algoritmos y Estructuras de Datos (UTEC, 2026-2).
Prof. Luciano A. Romero Calla.

Video educativo que explica y demuestra el **algoritmo de Kahn** para obtener un
ordenamiento topológico de un grafo dirigido acíclico (DAG) en O(|V| + |E|).
El ejemplo usa cursos reales de la malla de Ciencia de Datos y sus prerrequisitos.

**Video:** <https://drive.google.com/drive/folders/17Kxf36YbiPqlCSS6PIwCzpT4tV9Dyr6b>

## Integrantes

- Saúl Baltazar Palomino
- Francis Andres Huerta Roque

## Cómo funciona

El algoritmo está implementado en C++ (`cpp/kahn.cpp`). Si se le pasa una ruta como
argumento, además de imprimir el orden guarda los eventos de la ejecución (qué nodo sale
de la cola, a quién le baja el grado de entrada y quién entra) en un archivo JSON. Las
escenas de Manim leen ese archivo, así que la animación sale de la ejecución real del
algoritmo. Sin argumento, el programa solo ejecuta el algoritmo.

```
data/malla.txt → cpp/kahn.cpp → data/traza_malla.json → animacion/ (Manim) → video
```

## Software requerido

- g++ con soporte C++17
- Python 3.10 o superior
- Manim Community: `pip install manim`

## Cómo reproducir el video

Desde la raíz del repositorio.

1. Compilar:

   ```
   g++ -std=c++17 cpp/kahn.cpp -o cpp/kahn
   ```

2. Generar las trazas (PowerShell):

   ```
   Get-Content data/ejemplo.txt | ./cpp/kahn data/traza_ejemplo.json
   Get-Content data/malla.txt | ./cpp/kahn data/traza_malla.json
   Get-Content data/malla_ciclo.txt | ./cpp/kahn data/traza_malla_ciclo.json
   ```

   En Linux o macOS: `./cpp/kahn data/traza_malla.json < data/malla.txt` (igual para los demás).

3. Renderizar el video completo en 1080p:

   ```
   manim -qh animacion/escenas_video.py VideoCompleto
   ```

   El video queda en `media/videos/escenas_video/1080p60/VideoCompleto.mp4`.
   La narración (`audio/01.wav`, `audio/02.wav`, ...) se incluye sincronizada con los textos
   del video; sin la carpeta `audio/`, el video se genera sin voz. Ver `docs/guion.md`.
   Para una vista previa rápida, usar `-ql` en lugar de `-qh`.

Formato de entrada: primera línea `n m` (nodos y aristas), luego `m` líneas `u v` (arista u → v).

## Archivos

| Archivo | Contenido |
|---|---|
| `cpp/kahn.cpp` | Algoritmo de Kahn y generación de la traza |
| `data/malla_completa.json` | Malla completa de Ciencia de Datos (UTEC), usada en la motivación |
| `data/ejemplo.txt` | 4 cursos de la malla para explicar la idea del algoritmo |
| `data/malla.txt` | Grafo de 7 cursos de la malla |
| `data/malla_ciclo.txt` | Caso de borde: ciclo inventado entre AED y ADA, con Computación Paralela y Distribuida bloqueada por depender de él |
| `animacion/escena_grafo.py` | Dibujo del grafo de la malla |
| `animacion/escena_kahn.py` | Idea de Kahn con 4 cursos, ejecución sobre la malla y caso con ciclo |
| `animacion/escenas_video.py` | Intro, motivación, concepto, complejidad, créditos y video completo |
| `docs/guion.md` | Guion de narración, numerado según los puntos de voz del video |
