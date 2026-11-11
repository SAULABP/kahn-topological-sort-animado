import json
from pathlib import Path

from manim import *

# Ruta a la traza generada por cpp/kahn.cpp con data/malla.txt (se calcula
# desde este archivo, así funciona sin importar desde qué carpeta se ejecute manim)
RUTA_TRAZA = Path(__file__).resolve().parent.parent / "data" / "traza_malla.json"

# Nombre de cada curso, en orden del nodo 0 al 6 (solo presentación).
# El "\n" parte el nombre en dos líneas para que quepa en la caja.
NOMBRES = [
    "Programación I",
    "Cálculo de\nuna variable",
    "Programación II",
    "Estadística y\nProbabilidades I",
    "Programación III",
    "Algoritmos y\nEstructuras de Datos",
    "Machine\nLearning",
]

# Posición de cada nodo en pantalla (solo presentación). Columnas de
# izquierda a derecha: cada curso queda a la derecha de sus prerrequisitos.
POSICIONES = [
    [-5.4, 1.3, 0],   # 0 Programación I
    [-5.4, -1.3, 0],  # 1 Cálculo de una variable
    [-1.8, 1.3, 0],   # 2 Programación II
    [-1.8, -1.3, 0],  # 3 Estadística y Probabilidades I
    [1.8, 1.3, 0],    # 4 Programación III
    [5.4, 1.3, 0],    # 5 Algoritmos y Estructuras de Datos
    [1.8, -1.3, 0],   # 6 Machine Learning
]

ANCHO_CAJA = 2.6
ALTO_CAJA = 1.1


class EscenaGrafo(Scene):
    def construct(self):
        # 1. Leer la traza
        with open(RUTA_TRAZA, encoding="utf-8") as archivo:
            traza = json.load(archivo)

        n = traza["n"]
        aristas = traza["aristas"]
        grados = traza["grado_inicial"]

        # Los nombres y posiciones están pensados para este grafo de 7 nodos
        if n != len(NOMBRES):
            raise ValueError(f"La traza tiene {n} nodos, pero hay {len(NOMBRES)} nombres")

        # 2. Título
        titulo = Text("Malla curricular", font_size=40).to_edge(UP)
        self.play(Write(titulo))

        # 3. Nodos: una caja con el nombre del curso
        nodos = []
        for i in range(n):
            caja = RoundedRectangle(
                width=ANCHO_CAJA,
                height=ALTO_CAJA,
                corner_radius=0.2,
                color=BLUE,
                fill_opacity=0.3,
            )
            caja.move_to(POSICIONES[i])
            lineas = [Text(linea, font_size=22) for linea in NOMBRES[i].split("\n")]
            texto = VGroup(*lineas).arrange(DOWN, buff=0.08)
            if texto.width > ANCHO_CAJA - 0.3:  # si el nombre no cabe, se achica
                texto.scale_to_fit_width(ANCHO_CAJA - 0.3)
            texto.move_to(caja)
            nodos.append(VGroup(caja, texto))

        self.play(LaggedStart(*[FadeIn(nodo, scale=0.8) for nodo in nodos], lag_ratio=0.15))

        # 4. Aristas: una flecha dirigida de u hacia v, del borde derecho
        # de la caja u al borde izquierdo de la caja v
        flechas = []
        for u, v in aristas:
            flecha = Arrow(
                start=nodos[u].get_right(),
                end=nodos[v].get_left(),
                buff=0.1,
                stroke_width=4,
                tip_length=0.2,
                max_tip_length_to_length_ratio=0.5,
            )
            flechas.append(flecha)

        self.play(LaggedStart(*[GrowArrow(f) for f in flechas], lag_ratio=0.15))

        # 5. Grado de entrada encima de cada nodo
        etiquetas_grado = []
        for i in range(n):
            etiqueta = Text(str(grados[i]), font_size=28, color=YELLOW)
            etiqueta.next_to(nodos[i], UP, buff=0.12)
            etiquetas_grado.append(etiqueta)

        leyenda = Text("amarillo = grado de entrada (prerrequisitos)", font_size=24, color=YELLOW)
        leyenda.to_edge(DOWN)

        self.play(*[FadeIn(e, shift=DOWN * 0.2) for e in etiquetas_grado], FadeIn(leyenda))
        self.wait(2)
