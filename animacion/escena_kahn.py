"""Animación paso a paso del algoritmo de Kahn

qué curso sale, a quién le baja el grado,
quién entra a la cola  se lee de la traza que genera kahn.cpp
aca se decide como se ve
"""
import json
import sys
import wave
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
AUDIO = CARPETA.parent / "audio"  # narración: audio/01.wav, audio/02.wav, ... (ver docs/guion.md)

COLOR_NORMAL = BLUE
COLOR_COLA = YELLOW
COLOR_LISTO = GREEN
COLOR_CICLO = RED
COLOR_BLOQUEADO = ORANGE

# Todos los grafos se dibujan con la misma escala y centro, así una escena
# puede terminar exactamente con la imagen con la que empieza la siguiente.
ESCALA_GRAFO = 0.78
CENTRO_GRAFO = UP * 0.9

CORTOS_MALLA = ["Prog I", "Cálculo", "Prog II", "Estad. I", "Prog III", "AED", "ML"]

# El ejemplo pequeño (data/ejemplo.txt) son 4 cursos de la misma malla:
# nodo 0, 1, 2, 3 del ejemplo = nodo 0 (Prog I), 2 (Prog II), 3 (Estad. I) y 6 (ML) de la malla
EJEMPLO_EN_MALLA = [0, 2, 3, 6]


# ---------- Funciones de apoyo ----------

def cargar_traza(nombre_archivo):
    with open(DATA / nombre_archivo, encoding="utf-8") as archivo:
        return json.load(archivo)


def texto_centrado(texto, tam=28, color=WHITE):
    """Texto de una o varias líneas (separadas por \\n), cada línea centrada."""
    lineas = VGroup(*[Text(linea, font_size=tam, color=color) for linea in texto.split("\n")])
    return lineas.arrange(DOWN, buff=0.15)


def crear_nodo(nombre, ancho=ANCHO_CAJA, alto=ALTO_CAJA, fuente=22):
    """Caja con el nombre del curso (mismo estilo que escena_grafo.py)."""
    caja = RoundedRectangle(width=ancho, height=alto, corner_radius=0.2, color=COLOR_NORMAL, fill_opacity=0.3)
    lineas = [Text(linea, font_size=fuente) for linea in nombre.split("\n")]
    texto = VGroup(*lineas).arrange(DOWN, buff=0.08)
    if texto.width > ancho - 0.3:
        texto.scale_to_fit_width(ancho - 0.3)
    texto.move_to(caja)
    return VGroup(caja, texto)


def crear_flecha(origen, destino, ida_y_vuelta=False, por_arriba=True):
    """Flecha de origen a destino (mismo estilo que escena_grafo.py).
    Si hay flechas en los dos sentidos, una va por arriba y la otra por abajo."""
    estilo = dict(buff=0.1, stroke_width=4, tip_length=0.2, max_tip_length_to_length_ratio=0.5)
    if not ida_y_vuelta:
        return Arrow(origen.get_right(), destino.get_left(), **estilo)
    if por_arriba:
        return Arrow(origen.get_top(), destino.get_top(), path_arc=-PI / 2, **estilo)
    return Arrow(origen.get_bottom(), destino.get_bottom(), path_arc=-PI / 2, **estilo)


def crear_ficha(texto, color=COLOR_COLA):
    """Ficha pequeña que representa a un curso dentro de la cola o del orden."""
    caja = RoundedRectangle(width=1.4, height=0.55, corner_radius=0.1, color=color, fill_opacity=0.25)
    etiqueta = Text(texto, font_size=20).move_to(caja)
    if etiqueta.width > 1.25:
        etiqueta.scale_to_fit_width(1.25)
    return VGroup(caja, etiqueta)


def violaciones(orden, aristas):
    """Aristas u -> v que el orden no respeta (v aparece antes que u)."""
    posicion = {v: i for i, v in enumerate(orden)}
    return [(u, v) for u, v in aristas if posicion[u] > posicion[v]]


def nodos_en_ciclo(pendientes, aristas):
    """Entre los nodos que no salieron de la cola, los que pueden volver a sí mismos
    siguiendo flechas. Solo se usa para colorear el caso de ciclo: Kahn detecta que
    hay un ciclo, pero no dice qué nodos lo forman."""
    ady = {v: [] for v in pendientes}
    for u, v in aristas:
        if u in ady and v in ady:
            ady[u].append(v)
    en_ciclo = set()
    for inicio in pendientes:
        vistos, pila = set(), list(ady[inicio])
        while pila:
            x = pila.pop()
            if x == inicio:
                en_ciclo.add(inicio)
                break
            if x not in vistos:
                vistos.add(x)
                pila.extend(ady[x])
    return en_ciclo


def unir(nombres):
    """['A'] -> 'A' ; ['A', 'B'] -> 'A y B' ; ['A', 'B', 'C'] -> 'A, B y C'"""
    if len(nombres) <= 1:
        return "".join(nombres)
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


# ---------- Escenas ----------

class Narrada(Scene):
    """Escena con una línea de texto arriba que va contando lo que pasa,
    y con la narración (si existe la carpeta audio/) sincronizada con esos textos."""

    PAUSA = 0.6
    CONTINUA = False  # True: la escena termina con la imagen con la que empieza la siguiente

    # ----- Narración -----
    # Cada texto de cambiar_estado (y algunos puntos marcados con punto_de_voz) es un
    # "punto de voz" numerado en orden: 1, 2, 3... Si existe audio/NN.wav, se reproduce ahí.
    # Las animaciones siguen mientras se habla; el siguiente punto espera a que termine la frase.

    def punto_de_voz(self):
        """Avanza al siguiente punto de voz y reproduce su audio, si existe. Devuelve True si hubo audio."""
        self.numero_voz = getattr(self, "numero_voz", 0) + 1
        self.esperar_voz()
        archivo = AUDIO / f"{self.numero_voz:02d}.wav"
        if not archivo.exists():
            return False
        with wave.open(str(archivo)) as w:
            duracion = w.getnframes() / w.getframerate()
        self.add_sound(str(archivo))
        self.voz_hasta = self.renderer.time + duracion + 0.25
        return True

    def esperar_voz(self):
        """Espera a que termine la frase que se está diciendo."""
        restante = getattr(self, "voz_hasta", 0) - self.renderer.time
        if restante > 0.05:
            self.wait(restante)

    def cambiar_estado(self, texto, color=WHITE, espera=None, apoyo=None):
        """Si hay voz para este punto, en pantalla va solo la frase corta de apoyo
        (o nada, si apoyo es None). Sin voz, se muestra el texto completo."""
        con_voz = self.punto_de_voz()
        mostrar = apoyo if con_voz else texto
        anterior = getattr(self, "estado", None)
        if not mostrar:
            if anterior is not None:
                self.play(FadeOut(anterior, shift=UP * 0.2), run_time=0.4)
            self.estado = None
            self.wait(0.2 if con_voz else (espera if espera is not None else self.PAUSA))
            return
        nuevo = texto_centrado(mostrar, 32 if con_voz else 28, color)
        if nuevo.width > 13:
            nuevo.scale_to_fit_width(13)
        nuevo.to_edge(UP, buff=0.3)
        if anterior is None:
            self.play(FadeIn(nuevo), run_time=0.5)
        else:
            self.play(FadeOut(anterior, shift=UP * 0.2), FadeIn(nuevo, shift=UP * 0.2), run_time=0.6)
        self.estado = nuevo
        if con_voz:
            self.wait(0.3)  # el resto del tiempo lo marca la voz
        else:
            # Sin audio: tiempo de lectura según el largo del texto
            self.wait(espera if espera is not None else self.PAUSA + len(texto) / 38)

    def quitar_estado(self):
        if getattr(self, "estado", None) is not None:
            self.play(FadeOut(self.estado), run_time=0.4)
        self.estado = None


class KahnBase(Narrada):
    """Lógica común: cada escena hija indica qué traza leer y cómo dibujarla."""

    ARCHIVO = ""
    NOMBRES = []
    CORTOS = []
    POSICIONES = []
    ESCALA = ESCALA_GRAFO
    DESPLAZAMIENTO = CENTRO_GRAFO
    ANCHO = ANCHO_CAJA
    ALTO = ALTO_CAJA
    FUENTE = 22
    DETALLADO = True  # True: se explica cada flecha; False: un resumen por paso

    # ----- Preparación y dibujo -----

    def preparar(self):
        traza = cargar_traza(self.ARCHIVO)
        self.n = traza["n"]
        if self.n != len(self.NOMBRES):
            raise ValueError(f"La traza tiene {self.n} nodos, pero hay {len(self.NOMBRES)} nombres")
        self.aristas = [tuple(a) for a in traza["aristas"]]
        self.estado = getattr(self, "estado", None)
        self.cola = []  # fichas que están en la cola, en orden
        self.ids_cola = []  # número de nodo de cada ficha de la cola
        self.orden = []  # fichas que ya salieron
        self.ids_orden = []  # número de nodo de cada ficha del orden
        self.procesados = set()
        self.par_disponible = None  # dos nodos que estuvieron en la cola a la vez
        return traza

    def construir_grafo(self):
        """Crea nodos y flechas (sin mostrarlos) con la escala y el centro comunes."""
        self.nodos = [
            crear_nodo(nombre, self.ANCHO, self.ALTO, self.FUENTE).move_to(pos)
            for nombre, pos in zip(self.NOMBRES, self.POSICIONES)
        ]
        pares = set(self.aristas)
        self.flechas = {
            (u, v): crear_flecha(self.nodos[u], self.nodos[v], (v, u) in pares, por_arriba=u < v)
            for u, v in self.aristas
        }
        grafo = VGroup(*self.nodos, *self.flechas.values())
        grafo.scale(self.ESCALA, about_point=ORIGIN).shift(self.DESPLAZAMIENTO)
        # Copias del aspecto original para poder restaurarlo al final
        self.nodos_originales = [nodo.copy() for nodo in self.nodos]
        self.flechas_originales = {k: f.copy() for k, f in self.flechas.items()}
        return grafo

    def crear_grados(self, grados):
        self.grados = []
        for i, g in enumerate(grados):
            etiqueta = Text(str(g), font_size=28, color=YELLOW)
            etiqueta.next_to(self.nodos[i], UP, buff=0.1).align_to(self.nodos[i], LEFT).shift(RIGHT * 0.15)
            self.grados.append(etiqueta)

    def contar_grados(self):
        """Para cada nodo se iluminan las flechas que le llegan y aparece su grado."""
        for v in range(self.n):
            entrantes = [f for (u, w), f in self.flechas.items() if w == v]
            if entrantes:
                self.play(*[f.animate.set_color(YELLOW) for f in entrantes], run_time=0.4)
            self.play(FadeIn(self.grados[v], scale=1.6), run_time=0.35)
            if entrantes:
                self.play(*[f.animate.set_color(WHITE) for f in entrantes], run_time=0.25)

    def dibujar_paneles(self):
        self.paneles = VGroup(
            Text("Cola", font_size=26, color=COLOR_COLA).move_to([-6.1, -2.35, 0]),
            Text("Orden", font_size=26, color=COLOR_LISTO).move_to([-6.1, -3.3, 0]),
        )
        self.play(FadeIn(self.paneles), run_time=0.5)

    def pos_cola(self, k):
        return np.array([-4.7 + k * 1.6, -2.35, 0])

    def pos_orden(self, k):
        return np.array([-4.7 + k * 1.55, -3.3, 0])

    # ----- Operaciones de la cola -----

    def encolar(self, v):
        ficha = crear_ficha(self.CORTOS[v]).move_to(self.nodos[v])
        self.cola.append(ficha)
        self.ids_cola.append(v)
        self.play(self.nodos[v][0].animate.set_stroke(COLOR_COLA, width=6), FadeIn(ficha, scale=0.6), run_time=0.35)
        self.play(ficha.animate.move_to(self.pos_cola(len(self.cola) - 1)), run_time=0.6)

    def encolar_iniciales(self, traza):
        for v in traza["cola_inicial"]:
            self.encolar(v)
        self.anotar_disponibles()

    def sacar(self, actual):
        # Control: la traza solo dice qué nodo salió; debe ser el frente de la cola dibujada
        if not self.ids_cola or self.ids_cola[0] != actual:
            raise RuntimeError(f"La traza dice que sale {actual}, pero el frente de la cola es {self.ids_cola[:1]}")
        ficha = self.cola.pop(0)
        self.ids_cola.pop(0)
        ficha.generate_target()
        ficha.target.move_to(self.pos_orden(len(self.orden)))
        ficha.target[0].set_stroke(COLOR_LISTO).set_fill(COLOR_LISTO, opacity=0.25)
        self.orden.append(ficha)
        self.ids_orden.append(actual)
        self.procesados.add(actual)
        self.play(
            MoveToTarget(ficha),
            self.nodos[actual][0].animate.set_stroke(COLOR_LISTO, width=6).set_fill(COLOR_LISTO, opacity=0.45),
            *[f.animate.move_to(self.pos_cola(k)) for k, f in enumerate(self.cola)],
            run_time=0.8,
        )

    def faltan(self, v):
        """Prerrequisitos de v que todavía no salieron de la cola."""
        return [self.CORTOS[u] for (u, w) in self.aristas if w == v and u not in self.procesados]

    def anotar_disponibles(self):
        """La primera vez que hay dos nodos en la cola, se explica que el orden no es único
        (solo en la versión detallada, para no repetirlo en la malla)."""
        if self.DETALLADO and self.par_disponible is None and len(self.ids_cola) >= 2:
            self.par_disponible = tuple(self.ids_cola[:2])
            a, b = (self.CORTOS[i] for i in self.par_disponible)
            self.cambiar_estado(
                f"{a} y {b} están disponibles a la vez: cualquiera\n"
                "podría ir primero. Kahn toma el que llegó antes a la cola",
                COLOR_COLA,
                apoyo=f"{a} y {b}: disponibles a la vez",
            )

    # ----- Un paso del algoritmo -----

    def ejecutar_pasos(self, traza):
        for paso in traza["pasos"]:
            self.ejecutar_paso(paso)
        # Control final: el orden dibujado debe ser el que calculó kahn.cpp
        if self.ids_orden != traza["orden"]:
            raise RuntimeError(f"Orden animado {self.ids_orden} distinto de la traza {traza['orden']}")

    def ejecutar_paso(self, paso):
        actual = paso["sale"]
        a = self.CORTOS[actual]
        if self.DETALLADO:
            self.cambiar_estado(f"Sale {a} de la cola y pasa al orden")
        self.sacar(actual)

        cambios = paso["cambios"]
        if not cambios:
            mensaje = f"Ningún curso depende de {a}" if self.DETALLADO else f"Sale {a}: ningún curso depende de él"
            self.cambiar_estado(mensaje, espera=0.8)
            return

        for cambio in cambios:
            # Control: el grado nuevo debe coincidir con los prerrequisitos que faltan
            if len(self.faltan(cambio["nodo"])) != cambio["grado"]:
                raise RuntimeError(f"Grado de {cambio['nodo']} no coincide con sus prerrequisitos pendientes")

        if self.DETALLADO:
            for cambio in cambios:
                self.cumplir_flecha(actual, cambio)
        else:
            self.cumplir_flechas_juntas(actual, cambios)
        self.anotar_disponibles()

    def nuevo_grado(self, v, grado):
        return Text(str(grado), font_size=28, color=YELLOW).move_to(self.grados[v])

    def cumplir_flecha(self, actual, cambio):
        """Versión detallada: una flecha a la vez, diciendo qué dependencia se cumplió."""
        v, grado = cambio["nodo"], cambio["grado"]
        a, b = self.CORTOS[actual], self.CORTOS[v]
        flecha = self.flechas[(actual, v)]
        self.play(flecha.animate.set_color(COLOR_LISTO), run_time=0.4)
        self.play(Transform(self.grados[v], self.nuevo_grado(v, grado)), run_time=0.5)
        if cambio["entra"]:
            self.cambiar_estado(
                f"Se cumple {a} → {b}: a {b} ya no le falta ningún\nprerrequisito. Grado 0: entra a la cola",
                COLOR_COLA,
                apoyo=f"{b}: grado 0 → entra a la cola",
            )
            self.encolar(v)
        else:
            self.cambiar_estado(
                f"Se cumple {a} → {b}, pero a {b} todavía le falta\n{unir(self.faltan(v))}. Grado {grado}: aún no puede entrar",
                apoyo=f"{b}: grado {grado} → aún le falta {unir(self.faltan(v))}",
            )
        self.play(flecha.animate.set_color(GRAY).set_opacity(0.25), run_time=0.3)

    def cumplir_flechas_juntas(self, actual, cambios):
        """Versión resumida: todas las flechas del nodo a la vez y un texto con el resultado."""
        flechas = [self.flechas[(actual, c["nodo"])] for c in cambios]
        self.play(*[f.animate.set_color(COLOR_LISTO) for f in flechas], run_time=0.4)
        self.play(*[Transform(self.grados[c["nodo"]], self.nuevo_grado(c["nodo"], c["grado"])) for c in cambios], run_time=0.5)
        partes = []
        for c in cambios:
            b = self.CORTOS[c["nodo"]]
            partes.append(f"{b} llega a 0 y entra" if c["entra"] else f"{b} aún espera a {unir(self.faltan(c['nodo']))}")
        a = self.CORTOS[actual]
        cortas = [f"{self.CORTOS[c['nodo']]} entra" if c["entra"] else f"{self.CORTOS[c['nodo']]} espera" for c in cambios]
        self.cambiar_estado(
            f"Sale {a}: " + " · ".join(partes),
            COLOR_COLA if any(c["entra"] for c in cambios) else WHITE,
            espera=1.8,
            apoyo=f"Sale {a}: " + " · ".join(cortas),
        )
        for c in cambios:
            if c["entra"]:
                self.encolar(c["nodo"])
        self.play(*[f.animate.set_color(GRAY).set_opacity(0.25) for f in flechas], run_time=0.3)

    # ----- Final -----

    def final(self, traza):
        salieron = len(traza["orden"])
        if not traza["hay_ciclo"]:
            self.cambiar_estado(
                f"La cola quedó vacía y salieron los {self.n} cursos:\nel orden de abajo es un orden topológico",
                COLOR_LISTO,
                apoyo=f"{self.n} de {self.n} cursos: orden topológico ✓",
            )
            marco = SurroundingRectangle(VGroup(*self.orden), color=COLOR_LISTO, buff=0.12)
            self.play(Create(marco))
            self.marco = marco
            self.wait(1)
            return

        verbo = "salió" if salieron == 1 else "salieron"
        self.cambiar_estado(
            f"La cola quedó vacía, pero solo {verbo} {salieron} de {self.n} cursos",
            COLOR_CICLO,
            apoyo=f"Cola vacía: {salieron} de {self.n} cursos",
        )
        pendientes = [i for i in range(self.n) if i not in self.procesados]
        en_ciclo = sorted(nodos_en_ciclo(pendientes, self.aristas))
        bloqueados = [i for i in pendientes if i not in en_ciclo]

        if en_ciclo:
            nombres = [self.CORTOS[i] for i in en_ciclo]
            self.play(
                *[self.nodos[i][0].animate.set_stroke(COLOR_CICLO, width=6).set_fill(COLOR_CICLO, opacity=0.35) for i in en_ciclo],
                *[f.animate.set_color(COLOR_CICLO) for (u, v), f in self.flechas.items() if u in en_ciclo and v in en_ciclo],
            )
            self.cambiar_estado(
                f"{unir(nombres)} forman un ciclo: se esperan entre sí,\nasí que su grado nunca llega a 0",
                COLOR_CICLO,
                apoyo="Ciclo: " + " ⇄ ".join(nombres),
            )
        if bloqueados:
            nombres = [self.CORTOS[i] for i in bloqueados]
            self.play(*[self.nodos[i][0].animate.set_stroke(COLOR_BLOQUEADO, width=6).set_fill(COLOR_BLOQUEADO, opacity=0.3) for i in bloqueados])
            if len(bloqueados) == 1:
                texto = f"El curso {nombres[0]} no está en el ciclo, pero depende de él:\nqueda bloqueado"
            else:
                texto = f"Los cursos {unir(nombres)} no están en el ciclo, pero dependen de él:\nquedan bloqueados"
            self.cambiar_estado(texto, COLOR_BLOQUEADO, apoyo=f"{unir(nombres)}: bloqueado por el ciclo")
        self.cambiar_estado(
            "Si salen menos cursos que los que tiene el grafo, hay un ciclo:\nno existe un orden topológico completo",
            COLOR_CICLO,
            apoyo="procesados < V  →  hay ciclo",
        )
        self.wait(1)

    def volver_al_grafo(self):
        """Quita grados, cola y orden, y deja el grafo con su aspecto original."""
        extras = [*self.grados, self.paneles, *self.cola, *self.orden]
        if getattr(self, "marco", None) is not None:
            extras.append(self.marco)
            self.marco = None
        animaciones = [FadeOut(m) for m in extras]
        animaciones += [Transform(nodo, original.copy()) for nodo, original in zip(self.nodos, self.nodos_originales)]
        animaciones += [Transform(f, self.flechas_originales[k].copy()) for k, f in self.flechas.items()]
        if getattr(self, "estado", None) is not None:
            animaciones.append(FadeOut(self.estado))
            self.estado = None
        self.play(*animaciones, run_time=1)


class EscenaIdeaKahn(KahnBase):
    """La idea de Kahn, paso a paso, con 4 cursos de la malla (data/ejemplo.txt)."""

    ARCHIVO = "traza_ejemplo.json"
    NOMBRES = [NOMBRES_MALLA[i] for i in EJEMPLO_EN_MALLA]
    CORTOS = [CORTOS_MALLA[i] for i in EJEMPLO_EN_MALLA]
    POSICIONES = [POSICIONES_MALLA[i] for i in EJEMPLO_EN_MALLA]
    CONTINUA = True

    def construct(self):
        traza = self.preparar()
        self.add(self.construir_grafo())  # misma imagen con la que termina la escena anterior
        self.crear_grados(traza["grado_inicial"])

        self.cambiar_estado(
            "1. Contamos las flechas que llegan a cada curso: su grado de entrada.\nEs la cantidad de prerrequisitos que todavía le faltan",
            apoyo="Grado de entrada = prerrequisitos que faltan",
        )
        self.contar_grados()

        self.dibujar_paneles()
        self.cambiar_estado(
            "2. Un curso con grado 0 no espera a nadie: ya puede\nir en el orden. Entra a la cola de disponibles",
            COLOR_COLA,
            apoyo="Grado 0 → entra a la cola",
        )
        self.encolar_iniciales(traza)

        self.cambiar_estado(
            "3. Sacamos el primero de la cola y lo ponemos en el orden.\nSus flechas se cumplen: cada curso que lo necesitaba baja su grado en 1",
            apoyo="Sale de la cola → sus vecinos bajan su grado en 1",
        )
        self.ejecutar_pasos(traza)
        self.final(traza)
        self.otro_orden_valido()
        self.volver_al_grafo()

    def otro_orden_valido(self):
        """Si dos cursos estuvieron disponibles a la vez, intercambiarlos da otro orden válido."""
        if self.par_disponible is None:
            return
        x, y = self.par_disponible
        alternativo = list(self.ids_orden)
        i, j = alternativo.index(x), alternativo.index(y)
        alternativo[i], alternativo[j] = alternativo[j], alternativo[i]
        if violaciones(alternativo, self.aristas):  # solo se muestra si de verdad es válido
            return
        nombres = ", ".join(self.CORTOS[v] for v in alternativo)
        self.cambiar_estado(f"No es el único: {nombres}\ntambién respeta todas las flechas", COLOR_LISTO, apoyo=f"También válido: {nombres}")


class EscenaKahn(KahnBase):
    """Kahn sobre los 7 cursos de la malla. Empieza con los 4 cursos del ejemplo."""

    ARCHIVO = "traza_malla.json"
    NOMBRES = NOMBRES_MALLA
    CORTOS = CORTOS_MALLA
    POSICIONES = POSICIONES_MALLA
    DETALLADO = False

    def construct(self):
        traza = self.preparar()
        self.construir_grafo()

        # Imagen inicial: los 4 cursos del ejemplo; luego vuelven los demás
        ejemplo = set(EJEMPLO_EN_MALLA)
        aristas_ejemplo = [(u, v) for (u, v) in self.aristas if u in ejemplo and v in ejemplo]
        self.add(*[self.nodos[i] for i in EJEMPLO_EN_MALLA], *[self.flechas[k] for k in aristas_ejemplo])
        nuevos = [i for i in range(self.n) if i not in ejemplo]
        self.cambiar_estado(f"Ahora la malla completa: vuelven {unir([self.CORTOS[i] for i in nuevos])}")
        self.play(
            *[FadeIn(self.nodos[i], scale=0.8) for i in nuevos],
            *[GrowArrow(f) for k, f in self.flechas.items() if k not in aristas_ejemplo],
            run_time=1.2,
        )

        self.crear_grados(traza["grado_inicial"])
        self.cambiar_estado("Contamos otra vez los grados de entrada")
        self.play(LaggedStart(*[FadeIn(g, scale=1.6) for g in self.grados], lag_ratio=0.15))
        self.dibujar_paneles()
        iniciales = [self.CORTOS[v] for v in traza["cola_inicial"]]
        self.cambiar_estado(f"{unir(iniciales)} no tienen prerrequisitos: entran a la cola", COLOR_COLA, apoyo=f"{unir(iniciales)}: grado 0 → entran")
        self.encolar_iniciales(traza)
        self.ejecutar_pasos(traza)
        self.final(traza)


class EscenaCiclo(KahnBase):
    """Caso de borde: un ciclo inventado entre AED y ADA."""

    ARCHIVO = "traza_malla_ciclo.json"
    NOMBRES = [
        "Programación III",
        "Algoritmos y\nEstructuras de Datos",
        "Análisis y\nDiseño de Algoritmos",
        "Computación Paralela\ny Distribuida",
    ]
    CORTOS = ["Prog III", "AED", "ADA", "Comp. Paralela"]
    POSICIONES = [[-5.4, 0, 0], [-1.8, 0, 0], [1.8, 0, 0], [5.4, 0, 0]]
    DESPLAZAMIENTO = UP * 0.6

    def construct(self):
        traza = self.preparar()
        self.cambiar_estado(
            "¿Y si hubiera un ciclo? Supongamos (caso inventado)\nque AED también exigiera haber aprobado ADA",
            COLOR_CICLO,
            apoyo="Caso inventado: AED también exige ADA",
        )
        grafo = self.construir_grafo()
        self.crear_grados(traza["grado_inicial"])
        self.play(FadeIn(grafo), run_time=1)
        self.play(LaggedStart(*[FadeIn(g, scale=1.6) for g in self.grados], lag_ratio=0.2))
        self.dibujar_paneles()
        self.cambiar_estado("Aplicamos Kahn igual que antes", espera=0.8)
        self.encolar_iniciales(traza)
        self.ejecutar_pasos(traza)
        self.final(traza)
