"""Escenas del video completo y la escena que las une

Renderizar todo el video en 1080p:
    manim -qh animacion/escenas_video.py VideoCompleto
"""
import sys
from pathlib import Path

from manim import *

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))
from escena_grafo import EscenaGrafo  # noqa: E402
from escena_kahn import EscenaCiclo, EscenaKahn, KahnBase, cargar_traza  # noqa: E402

TITULO = "Ordenamiento topológico: algoritmo de Kahn"
INTEGRANTES = ["Saúl Baltazar Palomino", "Francis Andres Huerta Roque"]
REPO = "github.com/SAULABP/kahn-topological-sort-animado"


def lineas(*textos, tam=30, color=WHITE):
    """Varias líneas de texto centradas, una debajo de otra."""
    grupo = VGroup(*[Text(t, font_size=tam, color=color) for t in textos])
    return grupo.arrange(DOWN, buff=0.3)


def crear_circulo(letra):
    return VGroup(Circle(radius=0.4, color=BLUE, fill_opacity=0.3), Text(letra, font_size=30))


class Intro(Scene):
    def construct(self):
        titulo = Text(TITULO, font_size=44)
        if titulo.width > 13:
            titulo.scale_to_fit_width(13)
        curso = Text("Proyecto 2 · CS2023 Algoritmos y Estructuras de Datos · UTEC 2026-2", font_size=24, color=GRAY_B)
        nombres = lineas(*INTEGRANTES, tam=28, color=YELLOW)
        bloque = VGroup(titulo, curso, nombres).arrange(DOWN, buff=0.6)
        self.play(Write(titulo), run_time=1.5)
        self.play(FadeIn(curso, shift=UP * 0.2))
        self.play(FadeIn(nombres, shift=UP * 0.2))
        self.wait(2.5)


class Motivacion(Scene):
    def construct(self):
        texto = lineas(
            "Para llevar un curso, primero hay que aprobar sus prerrequisitos.",
            "Si cada curso tiene los suyos...",
        )
        pregunta = Text("¿En qué orden se pueden llevar todos sin saltarse ninguno?", font_size=32, color=YELLOW)
        pregunta.next_to(texto, DOWN, buff=0.6)
        self.play(FadeIn(texto[0]))
        self.wait(2)
        self.play(FadeIn(texto[1]))
        self.wait(1.5)
        self.play(Write(pregunta), run_time=1.5)
        self.wait(2.5)
        self.play(FadeOut(texto), FadeOut(pregunta))

        # La malla real (escena de Francis): cada flecha va del prerrequisito al curso
        EscenaGrafo.construct(self)
        nota = Text("Cada flecha va del prerrequisito al curso que lo necesita", font_size=24)
        nota.to_edge(DOWN, buff=1.0)
        self.play(FadeIn(nota))
        self.wait(2.5)


class Concepto(Scene):
    def construct(self):
        # 1. Un DAG pequeño
        titulo = Text("Grafo dirigido acíclico (DAG)", font_size=36).to_edge(UP)
        posiciones = {"A": [-2, 0, 0], "B": [0, 1.3, 0], "C": [0, -1.3, 0], "D": [2, 0, 0]}
        nodos = {k: crear_circulo(k).move_to(p) for k, p in posiciones.items()}
        aristas = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
        flechas = VGroup(*[Arrow(nodos[u].get_center(), nodos[v].get_center(), buff=0.45) for u, v in aristas])
        nota = Text("Dirigido: las flechas tienen sentido.  Acíclico: siguiéndolas nunca vuelves al inicio.", font_size=24)
        nota.to_edge(DOWN, buff=0.8)
        self.play(Write(titulo))
        self.play(*[FadeIn(n) for n in nodos.values()], *[GrowArrow(f) for f in flechas])
        self.play(FadeIn(nota))
        self.wait(3)

        # 2. Orden topológico: todas las flechas apuntan hacia adelante
        titulo2 = Text("Orden topológico", font_size=36).to_edge(UP)
        fila = {"A": [-4.5, 0, 0], "B": [-1.5, 0, 0], "C": [1.5, 0, 0], "D": [4.5, 0, 0]}
        self.play(FadeOut(flechas), FadeOut(nota), Transform(titulo, titulo2))
        self.play(*[nodos[k].animate.move_to(p) for k, p in fila.items()])
        flechas_fila = VGroup()
        for u, v in aristas:
            if abs(fila[u][0] - fila[v][0]) < 3.1:  # vecinos en la fila: flecha recta
                flechas_fila.add(Arrow(nodos[u].get_right(), nodos[v].get_left(), buff=0.1))
            else:  # más lejos: flecha curva por arriba
                flechas_fila.add(Arrow(nodos[u].get_top(), nodos[v].get_top(), buff=0.1, path_arc=-PI / 2))
        self.play(*[GrowArrow(f) for f in flechas_fila])
        nota2 = lineas(
            "Una fila con todos los nodos donde cada flecha apunta hacia adelante.",
            "A, B, C, D es un orden topológico (A, C, B, D también).",
            tam=24,
        ).to_edge(DOWN, buff=0.8)
        self.play(FadeIn(nota2))
        self.wait(3.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

        # 3. La idea de Kahn
        titulo3 = Text("La idea de Kahn (1962)", font_size=36).to_edge(UP)
        pasos = VGroup(
            Text("1. Contar el grado de entrada de cada nodo: cuántas flechas le llegan.", font_size=26),
            Text("2. Los nodos con grado 0 no dependen de nadie: entran a una cola.", font_size=26),
            Text("3. Sale un nodo de la cola y se tachan sus flechas:", font_size=26),
            Text("    a cada vecino le baja el grado en 1, y si llega a 0, entra a la cola.", font_size=26),
            Text("4. Si al final salieron menos nodos que los del grafo, hay un ciclo.", font_size=26, color=RED_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        pasos[3].shift(RIGHT * 0.45)  # continuación del paso 3, con sangría
        if pasos.width > 13:
            pasos.scale_to_fit_width(13)
        self.play(Write(titulo3))
        for paso in pasos:
            self.play(FadeIn(paso, shift=RIGHT * 0.2), run_time=0.7)
            self.wait(1.8)
        self.wait(1.5)


class Complejidad(Scene):
    def construct(self):
        traza = cargar_traza("traza_malla.json")
        v = traza["n"]
        e = len(traza["aristas"])
        salidas = len(traza["pasos"])
        revisadas = sum(len(paso["cambios"]) for paso in traza["pasos"])

        titulo = Text("¿Cuánto cuesta?", font_size=40).to_edge(UP)
        filas = VGroup(
            Text("Cada nodo entra y sale de la cola una sola vez  →  O(V)", font_size=28),
            Text("Cada flecha se revisa una sola vez, cuando sale su origen  →  O(E)", font_size=28),
            Text("Calcular los grados al leer las aristas  →  O(E)", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        if filas.width > 13:
            filas.scale_to_fit_width(13)
        total = Text("Total: O(V + E)", font_size=44, color=YELLOW).next_to(filas, DOWN, buff=0.7)

        self.play(Write(titulo))
        for fila in filas:
            self.play(FadeIn(fila, shift=RIGHT * 0.2), run_time=0.7)
            self.wait(2)
        self.play(Write(total))
        self.wait(2)

        # Comprobación con la ejecución real sobre la malla
        datos = Text(
            f"En la malla: V = {v} cursos, E = {e} prerrequisitos  →  "
            f"{salidas} salidas de la cola y {revisadas} flechas revisadas",
            font_size=24,
            color=GRAY_B,
        )
        if datos.width > 13:
            datos.scale_to_fit_width(13)
        memoria = Text("Memoria: lista de adyacencia + grados + cola  →  O(V + E)", font_size=24, color=GRAY_B)
        VGroup(datos, memoria).arrange(DOWN, buff=0.25).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(datos))
        self.wait(2.5)
        self.play(FadeIn(memoria))
        self.wait(3)


class Creditos(Scene):
    def construct(self):
        titulo = Text(TITULO, font_size=34)
        if titulo.width > 13:
            titulo.scale_to_fit_width(13)
        bloque = VGroup(
            titulo,
            lineas("Integrantes", *INTEGRANTES, tam=28),
            lineas(
                "CS2023 Algoritmos y Estructuras de Datos · Prof. Luciano A. Romero Calla",
                "Implementación: C++ (cpp/kahn.cpp)  ·  Animación: Manim Community",
                REPO,
                tam=22,
                color=GRAY_B,
            ),
        ).arrange(DOWN, buff=0.7)
        bloque[1][0].set_color(YELLOW)
        self.play(FadeIn(bloque, shift=UP * 0.3))
        self.wait(4)


class VideoCompleto(KahnBase):
    """Une todas las secciones en un solo video, en el orden de la escaleta."""

    def construct(self):
        secciones = [Intro, Motivacion, Concepto, EscenaKahn, EscenaCiclo, Complejidad, Creditos]
        for seccion in secciones:
            if issubclass(seccion, KahnBase):
                # Las escenas de Kahn leen su configuración (traza, nombres, posiciones) de la clase
                for atributo in ["ARCHIVO", "NOMBRES", "CORTOS", "POSICIONES", "ESCALA", "DESPLAZAMIENTO", "INTRO"]:
                    setattr(self, atributo, getattr(seccion, atributo))
            seccion.construct(self)
            self.limpiar()

    def limpiar(self):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.wait(0.3)