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

El algoritmo está implementado en C++ (`cpp/kahn.cpp`). Además de imprimir el orden,
guarda cada paso de la ejecución (qué nodo sale, a quién le baja el grado de entrada,
cómo queda la cola) en un archivo JSON. Las escenas de Manim leen ese archivo, así que
la animación sale de la ejecución real del algoritmo.

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
   Get-Content data/malla.txt | ./cpp/kahn data/traza_malla.json
   Get-Content data/malla_ciclo.txt | ./cpp/kahn data/traza_malla_ciclo.json
   ```

   En Linux o macOS: `./cpp/kahn data/traza_malla.json < data/malla.txt` (igual para el ciclo).

3. Renderizar el video completo en 1080p:

   ```
   manim -qh animacion/escenas_video.py VideoCompleto
   ```

   El video queda en `media/videos/escenas_video/1080p60/VideoCompleto.mp4`.
   Para una vista previa rápida, usar `-ql` en lugar de `-qh`.

Formato de entrada: primera línea `n m` (nodos y aristas), luego `m` líneas `u v` (arista u → v).

## Archivos

| Archivo | Contenido |
|---|---|
| `cpp/kahn.cpp` | Algoritmo de Kahn y generación de la traza |
| `data/malla.txt` | Grafo de 7 cursos de la malla |
| `data/malla_ciclo.txt` | Caso de borde: ciclo entre AED y ADA (inventado) |
| `animacion/escena_grafo.py` | Dibujo del grafo de la malla |
| `animacion/escena_kahn.py` | Animación paso a paso y caso con ciclo |
| `animacion/escenas_video.py` | Intro, concepto, complejidad, créditos y video completo |