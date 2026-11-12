# Topological Sort (Kahn) — Animado

Prof. Luciano A. Romero Calla.

Video educativo que explica y demuestra el **algoritmo de Kahn** para obtener un
ordenamiento topológico de un grafo dirigido acíclico (DAG) en O(|V| + |E|).

> <https://drive.google.com/drive/folders/17Kxf36YbiPqlCSS6PIwCzpT4tV9Dyr6b>

## Integrantes

- Saúl Baltazar Palomino
- Francis Andres Huerta Roque

## Cómo ejecutar (por ahora)

Compilar y generar la traza del grafo de la malla (PowerShell):

```
g++ -std=c++17 cpp/kahn.cpp -o cpp/kahn
Get-Content data/malla.txt | ./cpp/kahn data/traza_malla.json
```

Formato de entrada: primera línea `n m` (nodos y aristas), luego `m` líneas `u v` (arista u → v).
