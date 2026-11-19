"""Escenas del video completo y la escena que las une.

Renderizar todo el video en 1080p:
    manim -qh animacion/escenas_video.py VideoCompleto
"""
import sys
import types
from pathlib import Path

from manim import *

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA))
from escena_kahn import (  # noqa: E402
    CENTRO_GRAFO,
    COLOR_CICLO,
    COLOR_COLA,
    COLOR_LISTO,
    CORTOS_MALLA,
    EJEMPLO_EN_MALLA,
    ESCALA_GRAFO,
    NOMBRES_MALLA,
    POSICIONES_MALLA,
    EscenaCiclo,
    EscenaIdeaKahn,
    EscenaKahn,
    KahnBase,
    Narrada,
    cargar_traza,
    crear_ficha,
    crear_flecha,
    texto_centrado,
    unir,
    violaciones,
)

TITULO = "Ordenamiento topológico: algoritmo de Kahn"
INTEGRANTES = ["Saúl Baltazar Palomino", "Francis Andres Huerta Roque"]
REPO = "github.com/SAULABP/kahn-topological-sort-animado"


class Intro(Narrada):
    def construct(self):
        self.punto_de_voz()  # presentación
        titulo = Text(TITULO, font_size=44)
        if titulo.width > 13:
            titulo.scale_to_fit_width(13)
        subtitulo = Text("Proyecto final AED - UTEC", font_size=28, color=GRAY_B)
        nombres = texto_centrado("\n".join(INTEGRANTES), 28, YELLOW)
        VGroup(titulo, subtitulo, nombres).arrange(DOWN, buff=0.6)
        self.play(Write(titulo), run_time=1.5)
        self.play(FadeIn(subtitulo, shift=UP * 0.2))
        self.play(FadeIn(nombres, shift=UP * 0.2))
        self.wait(2.5)


def caja_pequena(nombre, ancho=1.2, alto=0.62):
    """Caja chica para la malla completa: el nombre se reparte en líneas cortas."""
    palabras, lineas, actual = nombre.split(), [], ""
    for palabra in palabras:
        if actual and len(actual) + 1 + len(palabra) > 14:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    lineas.append(actual)
    caja = RoundedRectangle(width=ancho, height=alto, corner_radius=0.08, color=BLUE, fill_opacity=0.25, stroke_width=2)
    texto = VGroup(*[Text(l, font_size=12) for l in lineas]).arrange(DOWN, buff=0.03)
    if texto.width > ancho - 0.1:
        texto.scale_to_fit_width(ancho - 0.1)
    if texto.height > alto - 0.08:
        texto.scale_to_fit_height(alto - 0.08)
    return VGroup(caja, texto.move_to(caja))


def _malla_completa_a_siete(self):
    """Muestra la malla completa (data/malla_completa.json), resalta los 7 cursos del
    video y los lleva a la vista ampliada (mismas posiciones y estilo que escena_grafo.py).
    Devuelve los 7 nodos, sus flechas y las aristas de la malla de 7 cursos."""
    import json as _json

    from escena_kahn import DATA, crear_nodo

    with open(DATA / "malla_completa.json", encoding="utf-8") as archivo:
        cursos = _json.load(archivo)["cursos"]
    por_nivel = {}
    for curso in cursos:
        por_nivel.setdefault(curso["nivel"], []).append(curso["nombre"])
    cajas = {}
    for nivel, nombres in por_nivel.items():
        for fila, nombre in enumerate(nombres):
            cajas[nombre] = caja_pequena(nombre).move_to([-6.3 + (nivel - 1) * 1.4, 2.0 - fila * 0.95, 0])
    lineas = VGroup()
    pares = []
    for curso in cursos:
        for previo in curso["prerrequisitos"]:
            a, b = cajas[previo], cajas[curso["nombre"]]
            lineas.add(Arrow(a.get_right(), b.get_left(), buff=0.03, stroke_width=1.5, tip_length=0.08,
                             max_tip_length_to_length_ratio=0.2, color=GRAY_B))
            pares.append((previo, curso["nombre"]))
    titulo = Text("Malla de Ciencia de Datos · UTEC", font_size=26).to_edge(UP, buff=0.3)

    self.play(FadeIn(titulo), LaggedStart(*[FadeIn(cajas[n]) for n in por_nivel_orden(por_nivel)], lag_ratio=0.02), run_time=1.6)
    self.play(LaggedStart(*[GrowArrow(l) for l in lineas], lag_ratio=0.01), run_time=1.2)

    # Los 7 cursos del video: se comprueba que sus prerrequisitos son los de data/malla.txt
    nombres_siete = [n.replace("\n", " ") for n in NOMBRES_MALLA]
    aristas = [tuple(a) for a in cargar_traza("traza_malla.json")["aristas"]]
    entre_siete = {(nombres_siete.index(u), nombres_siete.index(v)) for u, v in pares if u in nombres_siete and v in nombres_siete}
    if entre_siete != set(aristas):
        raise RuntimeError("Los prerrequisitos de la malla completa no coinciden con data/malla.txt")

    resto = [c for n, c in cajas.items() if n not in nombres_siete]
    self.play(
        *[c.animate.set_opacity(0.12) for c in resto],
        lineas.animate.set_opacity(0.12),
        *[cajas[n][0].animate.set_stroke(YELLOW, width=3) for n in nombres_siete],
        run_time=0.8,
    )
    self.wait(0.4)

    # Los 7 cursos pasan a la vista ampliada
    nodos = [crear_nodo(nombre).move_to(pos) for nombre, pos in zip(NOMBRES_MALLA, POSICIONES_MALLA)]
    flecha_de = {(u, v): crear_flecha(nodos[u], nodos[v]) for u, v in aristas}
    self.play(
        FadeOut(titulo), FadeOut(lineas), *[FadeOut(c) for c in resto],
        *[ReplacementTransform(cajas[n], nodo) for n, nodo in zip(nombres_siete, nodos)],
        run_time=1.5,
    )
    self.play(*[GrowArrow(f) for f in flecha_de.values()], run_time=0.8)
    return nodos, flecha_de, aristas


def por_nivel_orden(por_nivel):
    return [nombre for nivel in sorted(por_nivel) for nombre in por_nivel[nivel]]


class Motivacion(Narrada):
    CONTINUA = True
    malla_completa_a_siete = _malla_completa_a_siete

    def construct(self):
        # «Para llevar algunos cursos...»: la voz sigue mientras aparece la malla
        if not self.punto_de_voz():
            frase = Text("Para llevar algunos cursos, primero debemos aprobar sus prerrequisitos.", font_size=30)
            if frase.width > 13:
                frase.scale_to_fit_width(13)
            self.play(FadeIn(frase, shift=UP * 0.2))
            self.wait(2.5)
            self.play(FadeOut(frase), run_time=0.5)

        # La malla completa de Ciencia de Datos y, de ella, los 7 cursos del video
        nodos, flecha_de, aristas = self.malla_completa_a_siete()

        # Qué significa una flecha
        ejemplo = flecha_de[(2, 4)]
        self.play(ejemplo.animate.set_color(YELLOW), Indicate(nodos[2], color=YELLOW), Indicate(nodos[4], color=YELLOW))
        self.cambiar_estado(
            "Cada flecha va de un prerrequisito al curso que lo necesita:\nprimero Programación II, después Programación III",
            apoyo="prerrequisito  →  curso",
        )
        self.play(ejemplo.animate.set_color(WHITE))

        # El reto, con una lista que no lo cumple
        self.cambiar_estado(
            "El reto: poner los cursos en una lista donde cada uno\naparezca después de todos sus prerrequisitos",
            apoyo="Reto: cada curso después de sus prerrequisitos",
        )
        candidata = [0, 2, 6, 1, 3, 4, 5]
        fichas = VGroup(*[crear_ficha(CORTOS_MALLA[v], WHITE) for v in candidata]).arrange(RIGHT, buff=0.15)
        fichas.move_to(DOWN * 2.9)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.2) for f in fichas], lag_ratio=0.1))

        # «Esta lista no sirve»: énfasis justo cuando la voz lo dice
        malas = violaciones(candidata, aristas)  # se calcula, no se escribe a mano
        u, v = malas[0]
        self.cambiar_estado(
            f"✗ Esta lista no sirve: {CORTOS_MALLA[v]} aparece antes que\nsu prerrequisito {CORTOS_MALLA[u]}",
            COLOR_CICLO,
            apoyo=f"{CORTOS_MALLA[v]} aparece antes que su prerrequisito {CORTOS_MALLA[u]}",
        )
        marco_lista = SurroundingRectangle(fichas, color=COLOR_CICLO, buff=0.15)
        cruz = Text("✗", font_size=72, color=COLOR_CICLO).next_to(marco_lista, LEFT, buff=0.25)
        self.play(Create(marco_lista), FadeIn(cruz, scale=1.6), fichas.animate.scale(1.05), run_time=0.7)
        atras = VGroup()
        for u, v in malas:
            ficha_u, ficha_v = fichas[candidata.index(u)], fichas[candidata.index(v)]
            # La flecha de dependencia apunta hacia atrás en la lista: eso la invalida
            atras.add(Arrow(ficha_u.get_top(), ficha_v.get_top(), path_arc=PI / 2, buff=0.05, color=COLOR_CICLO, stroke_width=5, tip_length=0.22))
            self.play(
                ficha_v[0].animate.set_stroke(COLOR_CICLO, width=5).set_fill(COLOR_CICLO, 0.4),
                ficha_u[0].animate.set_stroke(COLOR_CICLO, width=5),
                flecha_de[(u, v)].animate.set_color(COLOR_CICLO),
                run_time=0.5,
            )
            self.play(Create(atras[-1]), run_time=0.7)
        self.esperar_voz()
        self.play(FadeOut(fichas), FadeOut(marco_lista), FadeOut(cruz), FadeOut(atras), *[flecha_de[k].animate.set_color(WHITE) for k in malas])

        self.cambiar_estado(
            "Buscamos un orden que respete todas las flechas. Ojo: no es un\n"
            "horario; no decide cuántos cursos llevar por ciclo",
            apoyo="No es un horario: solo un orden válido",
        )
        self.cambiar_estado(
            "Con 7 cursos se puede probar a mano. Con una malla completa,\n¿cómo podemos determinar ese orden automáticamente?",
            YELLOW,
            apoyo="¿Cómo hacerlo automáticamente?",
        )
        self.cambiar_estado("Aquí entra en acción el algoritmo de Kahn", YELLOW, apoyo="Algoritmo de Kahn")

        # Transición: quedan solo 4 cursos, con la escala y el centro del resto del video
        ejemplo_nodos = set(EJEMPLO_EN_MALLA)
        self.cambiar_estado("Para entender la idea, empecemos con solo 4 de estos cursos")
        salen = [nodos[i] for i in range(len(nodos)) if i not in ejemplo_nodos]
        salen += [f for (u, v), f in flecha_de.items() if u not in ejemplo_nodos or v not in ejemplo_nodos]
        self.play(*[FadeOut(m) for m in salen])
        quedan = VGroup(
            *[nodos[i] for i in EJEMPLO_EN_MALLA],
            *[f for (u, v), f in flecha_de.items() if u in ejemplo_nodos and v in ejemplo_nodos],
        )
        self.play(quedan.animate.scale(ESCALA_GRAFO, about_point=ORIGIN).shift(CENTRO_GRAFO))
        self.quitar_estado()


class Concepto(KahnBase):
    """Vocabulario mínimo: nodo, arista, DAG y orden topológico (no único)."""

    ARCHIVO = "traza_ejemplo.json"
    NOMBRES = EscenaIdeaKahn.NOMBRES
    CORTOS = EscenaIdeaKahn.CORTOS
    POSICIONES = EscenaIdeaKahn.POSICIONES
    CONTINUA = True

    def construct(self):
        traza = self.preparar()
        self.add(self.construir_grafo())  # misma imagen con la que termina Motivacion
        en_grafo = [nodo.get_center() for nodo in self.nodos]
        flechas = list(self.flechas.values())

        # Nodo y arista
        self.cambiar_estado("Esto es un grafo: cada curso es un nodo (o vértice)\ny cada flecha, una arista dirigida")
        # Etiquetas a la izquierda: la flecha diagonal (Prog I → Estad. I) es la más larga y se ve mejor
        nodo0, flecha0 = self.nodos[0], self.flechas[self.aristas[1]]
        etiqueta_nodo = Text("nodo", font_size=26, color=YELLOW).next_to(nodo0, LEFT, buff=0.2)
        etiqueta_arista = Text("arista", font_size=26, color=YELLOW).next_to(flecha0, LEFT, buff=0.2)
        self.play(FadeIn(etiqueta_nodo), FadeIn(etiqueta_arista), nodo0[0].animate.set_stroke(YELLOW), flecha0.animate.set_color(YELLOW))
        self.wait(1.5)
        self.play(FadeOut(etiqueta_nodo), FadeOut(etiqueta_arista), nodo0[0].animate.set_stroke(BLUE), flecha0.animate.set_color(WHITE))

        # DAG: siguiendo las flechas nunca se vuelve al inicio
        self.cambiar_estado(
            "Si al seguir las flechas nunca puedes volver al punto de partida,\nel grafo no tiene ciclos: es un DAG (grafo dirigido acíclico)",
            apoyo="DAG: grafo dirigido acíclico",
        )
        recorridos = []
        for f in flechas:
            brillo = f.copy().set_color(YELLOW).set_stroke(width=8)
            recorridos.append(ShowPassingFlash(brillo, time_width=0.6))
        self.play(LaggedStart(*recorridos, lag_ratio=0.35), run_time=2.5)

        # Orden topológico: en fila, todas las flechas hacia adelante
        self.cambiar_estado(
            "Un orden topológico pone todos los nodos en fila\nde modo que cada flecha apunte hacia adelante",
            apoyo="Orden topológico: todas las flechas hacia adelante",
        )
        orden = traza["orden"]
        fila = self.en_fila(orden, flechas)
        self.wait(1.5)

        # No es único
        alternativo = self.otro_orden(orden)
        if alternativo:
            x, y = [v for a, v in zip(orden, alternativo) if a != v]
            self.cambiar_estado(
                f"No siempre es único: {self.CORTOS[x]} y {self.CORTOS[y]} no dependen entre sí,\n"
                "así que también pueden ir en el otro orden",
                COLOR_LISTO,
                apoyo="No es único",
            )
            self.play(FadeOut(fila))
            fila = self.en_fila(alternativo, [])
            self.wait(1.5)

        # Vuelta al grafo (imagen inicial de la escena siguiente)
        self.quitar_estado()
        self.play(FadeOut(fila))
        self.play(*[nodo.animate.move_to(p) for nodo, p in zip(self.nodos, en_grafo)])
        self.play(*[FadeIn(f) for f in flechas])

    def en_fila(self, orden, flechas_a_quitar):
        """Mueve los nodos a una fila según el orden y dibuja las flechas hacia adelante."""
        xs = [-4.8, -1.6, 1.6, 4.8]
        animaciones = [FadeOut(f) for f in flechas_a_quitar]
        animaciones += [self.nodos[v].animate.move_to([xs[i], 0.3, 0]) for i, v in enumerate(orden)]
        self.play(*animaciones, run_time=1.2)
        posicion = {v: i for i, v in enumerate(orden)}
        fila = VGroup()
        for u, v in self.aristas:
            if posicion[v] - posicion[u] == 1:  # vecinos en la fila: flecha recta
                fila.add(Arrow(self.nodos[u].get_right(), self.nodos[v].get_left(), buff=0.1, stroke_width=4, tip_length=0.2))
            else:  # más lejos: flecha curva por arriba
                fila.add(Arrow(self.nodos[u].get_top(), self.nodos[v].get_top(), buff=0.1, stroke_width=4, tip_length=0.2, path_arc=-PI / 2))
        self.play(LaggedStart(*[GrowArrow(f) for f in fila], lag_ratio=0.2))
        return fila

    def otro_orden(self, orden):
        """Intercambia dos nodos vecinos en el orden si el resultado sigue siendo válido."""
        for i in range(len(orden) - 1):
            candidato = list(orden)
            candidato[i], candidato[i + 1] = candidato[i + 1], candidato[i]
            if not violaciones(candidato, self.aristas):
                return candidato
        return None


class Complejidad(KahnBase):
    """Por qué Kahn es O(V + E): se repite la ejecución de la malla marcando
    cada vértice que sale de la cola y cada arista que se examina."""

    ARCHIVO = "traza_malla.json"
    NOMBRES = NOMBRES_MALLA
    CORTOS = CORTOS_MALLA
    POSICIONES = POSICIONES_MALLA
    ESCALA = 0.55
    DESPLAZAMIENTO = UP * 1.3

    def construct(self):
        traza = self.preparar()
        v_total, e_total = self.n, len(self.aristas)
        self.cambiar_estado("¿Cuánto trabajo hace Kahn? Repetimos la malla\ny marcamos cada vez que se usa un vértice o una arista")
        self.play(FadeIn(self.construir_grafo()))

        # Una casilla por vértice y una por arista
        casillas_v = VGroup(*[Square(0.38, color=COLOR_LISTO) for _ in range(v_total)]).arrange(RIGHT, buff=0.12)
        casillas_e = VGroup(*[Square(0.38, color=COLOR_COLA) for _ in range(e_total)]).arrange(RIGHT, buff=0.12)
        etiqueta_v = Text("Vértices que salen de la cola", font_size=24)
        etiqueta_e = Text("Aristas examinadas", font_size=24)
        contador_v, contador_e = Text("0", font_size=30), Text("0", font_size=30)
        total_v = Text(f"/ {v_total}", font_size=30)
        total_e = Text(f"/ {e_total}", font_size=30)
        filas = VGroup()
        for etiqueta, casillas, contador, total, y in [
            (etiqueta_v, casillas_v, contador_v, total_v, -0.55),
            (etiqueta_e, casillas_e, contador_e, total_e, -1.35),
        ]:
            etiqueta.move_to([-4.2, y, 0])
            casillas.move_to([1.0, y, 0])
            contador.move_to([3.9, y, 0])
            total.next_to(contador, RIGHT, buff=0.15)
            filas.add(etiqueta, casillas, contador, total)
        self.play(FadeIn(filas))

        indice = {arista: i for i, arista in enumerate(self.aristas)}
        marcadas = set()
        salidas = 0
        for paso in traza["pasos"]:
            u = paso["sale"]
            self.play(
                self.nodos[u][0].animate.set_fill(COLOR_LISTO, opacity=0.5),
                casillas_v[salidas].animate.set_fill(COLOR_LISTO, opacity=0.8),
                Transform(contador_v, Text(str(salidas + 1), font_size=30).move_to(contador_v)),
                run_time=0.35,
            )
            salidas += 1
            for c in paso["cambios"]:
                k = indice[(u, c["nodo"])]
                if k in marcadas:
                    raise RuntimeError("Una arista se examinó dos veces")
                marcadas.add(k)
                self.play(
                    self.flechas[(u, c["nodo"])].animate.set_color(COLOR_COLA),
                    casillas_e[k].animate.set_fill(COLOR_COLA, opacity=0.8),
                    Transform(contador_e, Text(str(len(marcadas)), font_size=30).move_to(contador_e)),
                    run_time=0.25,
                )

        self.cambiar_estado(
            "Cada vértice sale una sola vez: entra a la cola solo cuando\nsu grado llega a 0, y el grado nunca vuelve a subir",
            apoyo="Cada vértice: una sola vez",
        )
        self.play(Indicate(casillas_v, color=COLOR_LISTO))
        self.cambiar_estado("Cada arista u → v se examina una sola vez:\ncuando sale u, y u sale una sola vez", apoyo="Cada arista: una sola vez")
        self.play(Indicate(casillas_e, color=COLOR_COLA))

        suma = Text("contar grados: E   +   sacar vértices: V   +   examinar aristas: E   =   V + 2E", font_size=24)
        resultado = Text("V + 2E  →  O(V + E)", font_size=44, color=YELLOW)
        VGroup(suma, resultado).arrange(DOWN, buff=0.3).move_to(DOWN * 2.6)
        self.cambiar_estado("Sumando todo el trabajo", espera=0.3)
        self.play(FadeIn(suma, shift=UP * 0.2))
        self.wait(0.8)
        self.cambiar_estado(
            "Las constantes no cambian el orden de crecimiento:\nV + E ≤ V + 2E ≤ 2(V + E), así que el costo es O(V + E)",
            apoyo="V + E  ≤  V + 2E  ≤  2(V + E)",
        )
        self.play(Write(resultado))
        self.wait(2)

        self.cambiar_estado(
            "Sin la cola, buscar cada vez un vértice con grado 0 revisando\nlos V vértices costaría O(V) por paso: O(V² + E) en total",
            GRAY_B,
            apoyo="Sin la cola: O(V² + E)",
        )
        self.cambiar_estado(
            "La traza y la animación son solo para el video:\nno forman parte del costo del algoritmo",
            GRAY_B,
            espera=1.5,
        )


class Creditos(Narrada):
    def construct(self):
        self.punto_de_voz()  # despedida
        titulo = Text(TITULO, font_size=34)
        if titulo.width > 13:
            titulo.scale_to_fit_width(13)
        integrantes = texto_centrado("Integrantes\n" + "\n".join(INTEGRANTES), 28)
        integrantes[0].set_color(YELLOW)
        datos = texto_centrado(
            "Proyecto final AED - UTEC · Prof. Luciano A. Romero Calla\n"
            "Implementación: C++ (cpp/kahn.cpp) · Animación: Manim Community\n"
            "Narración: voz generada con ElevenLabs\n" + REPO,
            22,
            GRAY_B,
        )
        self.play(FadeIn(VGroup(titulo, integrantes, datos).arrange(DOWN, buff=0.7), shift=UP * 0.3))
        self.wait(3)


class VideoCompleto(KahnBase):
    """Une todas las secciones en un solo video, en el orden de la narrativa."""

    def construct(self):
        secciones = [Intro, Motivacion, Concepto, EscenaIdeaKahn, EscenaKahn, EscenaCiclo, Complejidad, Creditos]
        for seccion in secciones:
            # Cada sección lee su configuración (traza, nombres, posiciones...) de su clase
            for atributo in dir(seccion):
                if atributo.isupper():
                    setattr(self, atributo, getattr(seccion, atributo))
            # y usa sus propios métodos de apoyo (por ejemplo Concepto.en_fila)
            for nombre, valor in vars(seccion).items():
                if callable(valor) and nombre != "construct" and not nombre.startswith("__"):
                    setattr(self, nombre, types.MethodType(valor, self))
            seccion.construct(self)
            self.esperar_voz()  # no cortar una frase al cambiar de sección
            if getattr(seccion, "CONTINUA", False):
                # La sección siguiente empieza con la misma imagen: se cambia sin transición
                self.clear()
                self.estado = None
            else:
                self.limpiar()

    def limpiar(self):
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.estado = None
        self.wait(0.3)
