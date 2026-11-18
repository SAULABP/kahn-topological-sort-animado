"""Animación paso a paso del algoritmo de Kahn

qué curso sale, a quién le baja el grado,
quién entra a la cola  se lee de la traza que genera kahn.cpp
aca se decide como se ve
"""
import json
import sys
from pathlib import Path

from manim import *

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))
from escena_grafo import (  # noqa: E402
    ALTO_CAJA,
    ANCHO_CAJA,
    NOMBRES as NOMBRES_MALLA,
    POSICIONES as POSICIONES_MALLA,
)

DATA = CARPETA.parent / "data"

COLOR_NORMAL = BLUE
COLOR_COLA = YELLOW
COLOR_LISTO = GREEN
COLOR_BLOQUEADO = RED

ANCHO_FICHA = 1.4
ALTO_FICHA = 0.55


def cargar_traza(nombre_archivo):
    with open(DATA / nombre_archivo, encoding="utf-8") as archivo:
        return json.load(archivo)


def crear_nodo(nombre):
    """Caja con el nombre del curso (mismo estilo que escena_grafo.py)."""
    caja = RoundedRectangle(
        width=ANCHO_CAJA,
        height=ALTO_CAJA,
        corner_radius=0.2,
        color=COLOR_NORMAL,
        fill_opacity=0.3,
    )
    lineas = [Text(linea, font_size=22) for linea in nombre.split("\n")]
    texto = VGroup(*lineas).arrange(DOWN, buff=0.08)
    if texto.width > ANCHO_CAJA - 0.3:
        texto.scale_to_fit_width(ANCHO_CAJA - 0.3)
    texto.move_to(caja)
    return VGroup(caja, texto)


def crear_ficha(texto):
    """Ficha pequeña que representa a un curso dentro de la cola o del orden."""
    caja = RoundedRectangle(
        width=ANCHO_FICHA,
        height=ALTO_FICHA,
        corner_radius=0.1,
        color=COLOR_COLA,
        fill_opacity=0.25,
    )
    etiqueta = Text(texto, font_size=20).move_to(caja)
    return VGroup(caja, etiqueta)


class KahnBase(Scene):
    """Lógica común: cada escena hija solo indica qué traza leer y cómo dibujarla."""

    ARCHIVO = ""
    NOMBRES = []
    CORTOS = []
    POSICIONES = []
    ESCALA = 0.78
    DESPLAZAMIENTO = UP * 0.9
    INTRO = ""
    PAUSA = 0.6 # segs para leer  cada texto de estado

    def construct(self):
        traza = cargar_traza(self.ARCHIVO)
        self.n = traza["n"]
        if self.n != len(self.NOMBRES):
            raise ValueError(f"La traza tiene {self.n} nodos, pero hay {len(self.NOMBRES)} nombres")

        self.estado = None
        self.cola = []  # fichas que están en la cola, en orden
        self.ids_cola = []  # número de nodo de cada ficha de la cola
        self.orden = []  # fichas que ya salieron

        if self.INTRO:
            self.cambiar_estado(self.INTRO)
            self.wait(1.5)
        self.dibujar_grafo(traza)
        self.dibujar_paneles()

        self.cambiar_estado("Entran a la cola los cursos con grado 0")
        for v in traza["cola_inicial"]:
            self.encolar(v)
        self.wait(0.5)

        for paso in traza["pasos"]:
            self.ejecutar_paso(paso)
            # Control: la cola que se ve en pantalla debe ser igual a la de la traza
            if self.ids_cola != paso["cola"]:
                raise RuntimeError(f"Cola animada {self.ids_cola} distinta de la traza {paso['cola']}")

        self.final(traza)

    # ---------- Dibujo inicial ----------

    def dibujar_grafo(self, traza):
        self.nodos = [crear_nodo(nombre) for nombre in self.NOMBRES]
        for nodo, posicion in zip(self.nodos, self.POSICIONES):
            nodo.move_to(posicion)

        pares = {tuple(arista) for arista in traza["aristas"]}
        self.flechas = {}
        for u, v in traza["aristas"]:
            self.flechas[(u, v)] = self.crear_flecha(u, v, (v, u) in pares)

        grafo = VGroup(*self.nodos, *self.flechas.values())
        grafo.scale(self.ESCALA).shift(self.DESPLAZAMIENTO)

        self.grados = []
        for i in range(self.n):
            grado = Text(str(traza["grado_inicial"][i]), font_size=28, color=YELLOW)
            grado.next_to(self.nodos[i], UP, buff=0.1).align_to(self.nodos[i], LEFT).shift(RIGHT * 0.15)
            self.grados.append(grado)

        self.play(FadeIn(grafo), *[FadeIn(g) for g in self.grados], run_time=1)

    def crear_flecha(self, u, v, ida_y_vuelta):
        origen, destino = self.nodos[u], self.nodos[v]
        estilo = dict(buff=0.1, stroke_width=4, tip_length=0.2, max_tip_length_to_length_ratio=0.5)
        if not ida_y_vuelta:
            return Arrow(origen.get_right(), destino.get_left(), **estilo)
        # Si hay flechas en los dos sentidos, una va por arriba y la otra por abajo
        if u < v:
            return Arrow(origen.get_top(), destino.get_top(), path_arc=-PI / 2, **estilo)
        return Arrow(origen.get_bottom(), destino.get_bottom(), path_arc=-PI / 2, **estilo)

    def dibujar_paneles(self):
        etiqueta_cola = Text("Cola", font_size=26, color=COLOR_COLA).move_to([-6.1, -2.35, 0])
        etiqueta_orden = Text("Orden", font_size=26, color=COLOR_LISTO).move_to([-6.1, -3.3, 0])
        self.play(FadeIn(etiqueta_cola), FadeIn(etiqueta_orden), run_time=0.5)

    def pos_cola(self, k):
        return np.array([-4.7 + k * 1.6, -2.35, 0])

    def pos_orden(self, k):
        return np.array([-4.7 + k * 1.55, -3.3, 0])

    # ---------- Pasos del algoritmo ----------

    def cambiar_estado(self, texto, color=WHITE):
        nuevo = Text(texto, font_size=28, color=color)
        if nuevo.width > 13:
            nuevo.scale_to_fit_width(13)
        nuevo.to_edge(UP, buff=0.35)
        if self.estado is None:
            self.play(FadeIn(nuevo), run_time=0.5)
        else:
            self.play(FadeOut(self.estado, shift=UP * 0.2), FadeIn(nuevo, shift=UP * 0.2), run_time=0.6)
        self.estado = nuevo
        self.wait(self.PAUSA)

    def encolar(self, v):
        ficha = crear_ficha(self.CORTOS[v]).move_to(self.nodos[v])
        destino = self.pos_cola(len(self.cola))
        self.cola.append(ficha)
        self.ids_cola.append(v)
        self.play(
            self.nodos[v][0].animate.set_stroke(COLOR_COLA, width=6),
            FadeIn(ficha, scale=0.6),
            run_time=0.4,
        )
        self.play(ficha.animate.move_to(destino), run_time=0.7)

    def ejecutar_paso(self, paso):
        actual = paso["sale"]
        nombre = self.NOMBRES[actual].replace("\n", " ")
        self.cambiar_estado(f"Sale de la cola: {nombre}")

        # La ficha del frente pasa al orden y el resto de la cola avanza
        ficha = self.cola.pop(0)
        self.ids_cola.pop(0)
        ficha.generate_target()
        ficha.target.move_to(self.pos_orden(len(self.orden)))
        ficha.target[0].set_stroke(COLOR_LISTO).set_fill(COLOR_LISTO, opacity=0.25)
        self.orden.append(ficha)
        self.play(
            MoveToTarget(ficha),
            self.nodos[actual][0].animate.set_stroke(COLOR_LISTO, width=6).set_fill(COLOR_LISTO, opacity=0.45),
            *[f.animate.move_to(self.pos_cola(k)) for k, f in enumerate(self.cola)],
            run_time=0.9,
        )

        # Se "tachan" sus flechas: a cada vecino le baja el grado en 1
        for cambio in paso["cambios"]:
            v = cambio["nodo"]
            grado = cambio["grado"]
            flecha = self.flechas[(actual, v)]
            nuevo_grado = Text(str(grado), font_size=28, color=YELLOW).move_to(self.grados[v])
            self.play(flecha.animate.set_color(RED), run_time=0.4)
            self.play(Transform(self.grados[v], nuevo_grado), flecha.animate.set_opacity(0.15), run_time=0.6)
            if cambio["entra"]:
                self.cambiar_estado(f"{self.CORTOS[v]} llega a grado 0: entra a la cola", COLOR_COLA)
                self.encolar(v)
            else:
                self.cambiar_estado(f"{self.CORTOS[v]} baja a {grado}: todavía no entra")
        self.wait(0.3)

    def final(self, traza):
        salieron = len(traza["orden"])
        verbo = "salió" if salieron == 1 else "salieron"
        if not traza["hay_ciclo"]:
            self.cambiar_estado(
                f"Cola vacía: {verbo} {salieron} de {self.n} cursos. No hay ciclo", COLOR_LISTO
            )
            marco = SurroundingRectangle(VGroup(*self.orden), color=COLOR_LISTO, buff=0.12)
            self.play(Create(marco))
        else:
            self.cambiar_estado(
                f"Cola vacía, pero solo {verbo} {salieron} de {self.n}: hay un ciclo", COLOR_BLOQUEADO
            )
            bloqueados = [i for i in range(self.n) if i not in traza["orden"]]
            self.play(
                *[
                    self.nodos[i][0].animate.set_stroke(COLOR_BLOQUEADO, width=6).set_fill(COLOR_BLOQUEADO, opacity=0.35)
                    for i in bloqueados
                ]
            )
        self.wait(2)


class EscenaKahn(KahnBase):
    """Kahn sobre los 7 cursos de la malla."""

    ARCHIVO = "traza_malla.json"
    NOMBRES = NOMBRES_MALLA
    CORTOS = ["Prog I", "Cálculo", "Prog II", "Estad. I", "Prog III", "AED", "ML"]
    POSICIONES = POSICIONES_MALLA


class EscenaCiclo(KahnBase):
    """Caso de borde: un ciclo inventado entre AED y ADA."""

    ARCHIVO = "traza_malla_ciclo.json"
    NOMBRES = ["Programación III", "Algoritmos y\nEstructuras de Datos", "Análisis y\nDiseño de Algoritmos"]
    CORTOS = ["Prog III", "AED", "ADA"]
    POSICIONES = [[-4.5, 0, 0], [0, 0, 0], [4.5, 0, 0]]
    ESCALA = 1
    DESPLAZAMIENTO = UP * 0.8
    INTRO = "¿Y si AED y ADA fueran prerrequisito una de la otra? (caso inventado)"