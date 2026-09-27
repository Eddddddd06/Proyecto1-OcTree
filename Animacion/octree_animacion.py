"""
Animacion de Octree - CS2023
Leonardo Sanchez, Osorio Panduro
python3 -m manim -pql octree_animacion.py OctreeAnimacion
"""

from manim import *
import numpy as np


class OctreeNode:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ, capacidad):
        self.minX, self.minY, self.minZ = minX, minY, minZ
        self.maxX, self.maxY, self.maxZ = maxX, maxY, maxZ
        self.capacidad = capacidad
        self.puntos = []
        self.hijos = [None] * 8


class OctreeSim:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ, cap):
        self.root = OctreeNode(minX, minY, minZ, maxX, maxY, maxZ, cap)
        self.reg_ins = []
        self.reg_bus = []

    def contiene(self, nodo, p):
        return (p[0] >= nodo.minX and p[0] <= nodo.maxX and
                p[1] >= nodo.minY and p[1] <= nodo.maxY and
                p[2] >= nodo.minZ and p[2] <= nodo.maxZ)

    def obtenerOctante(self, nodo, p):
        cx = (nodo.minX + nodo.maxX) / 2.0
        cy = (nodo.minY + nodo.maxY) / 2.0
        cz = (nodo.minZ + nodo.maxZ) / 2.0
        octante = 0
        if p[0] >= cx:
            octante += 1
        if p[1] >= cy:
            octante += 2
        if p[2] >= cz:
            octante += 4
        return octante

    def subdividir(self, nodo):
        cx = (nodo.minX + nodo.maxX) / 2.0
        cy = (nodo.minY + nodo.maxY) / 2.0
        cz = (nodo.minZ + nodo.maxZ) / 2.0
        cap = nodo.capacidad
        nodo.hijos[0] = OctreeNode(nodo.minX, nodo.minY, nodo.minZ, cx, cy, cz, cap)
        nodo.hijos[1] = OctreeNode(cx, nodo.minY, nodo.minZ, nodo.maxX, cy, cz, cap)
        nodo.hijos[2] = OctreeNode(nodo.minX, cy, nodo.minZ, cx, nodo.maxY, cz, cap)
        nodo.hijos[3] = OctreeNode(cx, cy, nodo.minZ, nodo.maxX, nodo.maxY, cz, cap)
        nodo.hijos[4] = OctreeNode(nodo.minX, nodo.minY, cz, cx, cy, nodo.maxZ, cap)
        nodo.hijos[5] = OctreeNode(cx, nodo.minY, cz, nodo.maxX, cy, nodo.maxZ, cap)
        nodo.hijos[6] = OctreeNode(nodo.minX, cy, cz, cx, nodo.maxY, nodo.maxZ, cap)
        nodo.hijos[7] = OctreeNode(cx, cy, cz, nodo.maxX, nodo.maxY, nodo.maxZ, cap)
        for pt in nodo.puntos:
            oct = self.obtenerOctante(nodo, pt)
            nodo.hijos[oct].puntos.append(pt)
        nodo.puntos.clear()

    def insertar(self, nodo, p, subs):
        if not self.contiene(nodo, p):
            return False
        if nodo.hijos[0] is None:
            if len(nodo.puntos) < nodo.capacidad:
                nodo.puntos.append(p)
                return True
            else:
                self.subdividir(nodo)
                subs.append(nodo)
        oct = self.obtenerOctante(nodo, p)
        return self.insertar(nodo.hijos[oct], p, subs)

    def insertar_punto(self, p):
        subs = []
        ok = self.insertar(self.root, p, subs)
        self.reg_ins.append((p, subs))
        return ok

    def buscar(self, nodo, p, camino):
        if not self.contiene(nodo, p):
            return False
        camino.append(nodo)
        if nodo.hijos[0] is None:
            for pt in nodo.puntos:
                if pt[0] == p[0] and pt[1] == p[1] and pt[2] == p[2]:
                    return True
            return False
        oct = self.obtenerOctante(nodo, p)
        return self.buscar(nodo.hijos[oct], p, camino)

    def buscar_punto(self, p):
        camino = []
        found = self.buscar(self.root, p, camino)
        self.reg_bus.append((p, camino, found))
        return found

    def postorder(self, nodo, res):
        if nodo is None:
            return
        for i in range(8):
            self.postorder(nodo.hijos[i], res)
        res.append(nodo)


def nodo_a_cubo(nodo, color=BLUE, op=0.06):
    ancho = nodo.maxX - nodo.minX
    alto = nodo.maxY - nodo.minY
    prof = nodo.maxZ - nodo.minZ
    centro = np.array([
        (nodo.minX + nodo.maxX) / 2.0,
        (nodo.minY + nodo.maxY) / 2.0,
        (nodo.minZ + nodo.maxZ) / 2.0,
    ])
    cubo = Cube(side_length=1.0)
    cubo.stretch(ancho, 0)
    cubo.stretch(alto, 1)
    cubo.stretch(prof, 2)
    cubo.move_to(centro)
    cubo.set_stroke(color, width=1.5)
    cubo.set_fill(color, opacity=op)
    return cubo


def punto_a_dot(p, color=YELLOW, radio=0.06):
    return Dot3D(point=np.array([p[0], p[1], p[2]]), color=color, radius=radio)


nodo_mob = {}


class OctreeAnimacion(ThreeDScene):

    def construct(self):
        # portada
        titulo = Text("Animación de Octree", font_size=48, color=WHITE)
        nombres = Text("Leonardo Sanchez  &  Osorio Panduro", font_size=28, color=GRAY_B)
        curso = Text("CS2023 — Algoritmos y Estructuras de Datos", font_size=24, color=GRAY)
        grupo = VGroup(titulo, nombres, curso).arrange(DOWN, buff=0.4)
        self.play(FadeIn(grupo, shift=UP * 0.5), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(grupo), run_time=0.5)

        # intro
        intro1 = Text("¿Qué es un Octree?", font_size=40, color=BLUE_B)
        self.play(Write(intro1), run_time=0.7)
        self.wait(0.4)
        self.play(intro1.animate.to_edge(UP), run_time=0.4)

        explicacion = VGroup(
            Text("• Árbol de partición espacial en 3D.", font_size=24),
            Text("• Cada nodo representa un cubo (cuadrante).", font_size=24),
            Text("• Cuando un cubo supera su capacidad,", font_size=24),
            Text("  se subdivide en 8 hijos iguales.", font_size=24),
            Text("• Útil en motores gráficos, detección de", font_size=24),
            Text("  colisiones 3D y simulaciones de partículas.", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(intro1, DOWN, buff=0.4)

        for linea in explicacion:
            self.play(FadeIn(linea, shift=RIGHT * 0.3), run_time=0.3)
        self.wait(1.5)
        self.play(FadeOut(VGroup(intro1, explicacion)), run_time=0.5)

        # insercion
        texto_demo = Text("Operación: Inserción (capacidad = 1)", font_size=30, color=GREEN_B)
        self.play(Write(texto_demo), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(texto_demo), run_time=0.3)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        RANGO = 3.0
        arbol = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)

        cubo_raiz = nodo_a_cubo(arbol.root, color=BLUE, op=0.04)
        nodo_mob[id(arbol.root)] = cubo_raiz
        self.play(Create(cubo_raiz), run_time=0.6)
        self.wait(0.2)

        puntos_demo = [
            ( 1.5,  1.5,  1.5),
            (-1.5, -1.5, -1.5),
        ]

        cubos_vis = [cubo_raiz]
        dots_vis = []

        for p in puntos_demo:
            arbol.insertar_punto(p)
            _, subs = arbol.reg_ins[-1]

            dot = punto_a_dot(p)
            self.play(FadeIn(dot, scale=0.5), run_time=0.35)
            dots_vis.append(dot)

            for nodo_div in subs:
                nuevos = VGroup()
                for hijo in nodo_div.hijos:
                    c = nodo_a_cubo(hijo, color=TEAL, op=0.05)
                    nodo_mob[id(hijo)] = c
                    nuevos.add(c)
                    cubos_vis.append(c)
                self.play(LaggedStart(*[Create(c) for c in nuevos],
                                      lag_ratio=0.04), run_time=0.6)
            self.wait(0.2)

        self.wait(0.5)

        # busqueda
        texto_busq = Text("Operación: Búsqueda", font_size=30, color=ORANGE)
        self.add_fixed_in_frame_mobjects(texto_busq)
        texto_busq.to_edge(UP)
        self.play(Write(texto_busq), run_time=0.5)
        self.wait(0.3)

        punto_buscar = (1.5, 1.5, 1.5)
        arbol.buscar_punto(punto_buscar)
        _, camino, _ = arbol.reg_bus[-1]

        ilum = []
        for n in camino:
            mid = id(n)
            if mid in nodo_mob:
                cb = nodo_mob[mid]
                cb_copia = cb.copy()
                cb.set_stroke(ORANGE, width=2.5)
                cb.set_fill(ORANGE, opacity=0.12)
                ilum.append((cb, cb_copia))
                self.play(cb.animate.set_fill(ORANGE, opacity=0.12), run_time=0.25)

        res_si = Text("✓ Punto (1.5, 1.5, 1.5) encontrado", font_size=22, color=GREEN)
        self.add_fixed_in_frame_mobjects(res_si)
        res_si.next_to(texto_busq, DOWN, buff=0.25)
        self.play(FadeIn(res_si), run_time=0.4)
        self.wait(0.6)

        for cb, orig in ilum:
            cb.set_stroke(orig.get_stroke_color(), width=1.5)
            cb.set_fill(orig.get_fill_color(), opacity=orig.get_fill_opacity())
        self.play(FadeOut(res_si), run_time=0.3)

        punto_no = (0.0, 0.0, 0.0)
        arbol.buscar_punto(punto_no)
        _, camino2, _ = arbol.reg_bus[-1]

        ilum2 = []
        for n in camino2:
            mid = id(n)
            if mid in nodo_mob:
                cb = nodo_mob[mid]
                cb_copia = cb.copy()
                cb.set_stroke(RED, width=2.5)
                cb.set_fill(RED, opacity=0.10)
                ilum2.append((cb, cb_copia))
                self.play(cb.animate.set_fill(RED, opacity=0.10), run_time=0.25)

        res_no = Text("✗ Punto (0, 0, 0) no encontrado", font_size=22, color=RED)
        self.add_fixed_in_frame_mobjects(res_no)
        res_no.next_to(texto_busq, DOWN, buff=0.25)
        self.play(FadeIn(res_no), run_time=0.4)
        self.wait(0.6)

        for cb, orig in ilum2:
            cb.set_stroke(orig.get_stroke_color(), width=1.5)
            cb.set_fill(orig.get_fill_color(), opacity=orig.get_fill_opacity())

        self.play(FadeOut(res_no), FadeOut(texto_busq), run_time=0.3)
        self.play(*[FadeOut(m) for m in cubos_vis + dots_vis], run_time=0.5)
        nodo_mob.clear()

        # recorrido postorder (liberar)
        texto_rec = Text("Operación: Recorrido post-order (liberar)", font_size=30, color=PURPLE_B)
        self.add_fixed_in_frame_mobjects(texto_rec)
        texto_rec.to_edge(UP)
        self.play(Write(texto_rec), run_time=0.5)
        self.wait(0.3)

        arbol_rec = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)
        arbol_rec.insertar_punto((1.5, 1.5, 1.5))
        arbol_rec.insertar_punto((-1.5, -1.5, -1.5))

        cubos_rec = []

        def dibujar(nodo):
            if nodo is None:
                return
            c = nodo_a_cubo(nodo, color=BLUE_D, op=0.04)
            nodo_mob[id(nodo)] = c
            cubos_rec.append(c)
            self.add(c)
            for i in range(8):
                dibujar(nodo.hijos[i])

        dibujar(arbol_rec.root)
        self.wait(0.3)

        orden = []
        arbol_rec.postorder(arbol_rec.root, orden)

        for nodo_po in orden:
            mid = id(nodo_po)
            if mid in nodo_mob:
                cb = nodo_mob[mid]
                self.play(
                    cb.animate.set_stroke(PURPLE, width=2.5).set_fill(PURPLE, opacity=0.15),
                    run_time=0.08
                )
                self.play(FadeOut(cb, scale=0.7), run_time=0.08)

        self.play(FadeOut(texto_rec), run_time=0.3)
        nodo_mob.clear()

        # caso borde
        texto_borde = Text("Caso borde: puntos concentrados", font_size=30, color=RED_B)
        self.add_fixed_in_frame_mobjects(texto_borde)
        texto_borde.to_edge(UP)
        self.play(Write(texto_borde), run_time=0.5)
        self.wait(0.3)

        subtexto = Text(
            "Muchos puntos pegados → subdivisiones profundas en un solo lado",
            font_size=20, color=GRAY_B
        )
        self.add_fixed_in_frame_mobjects(subtexto)
        subtexto.next_to(texto_borde, DOWN, buff=0.15)
        self.play(FadeIn(subtexto), run_time=0.4)
        self.wait(0.3)

        arbol2 = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)
        cubo_raiz2 = nodo_a_cubo(arbol2.root, color=BLUE, op=0.04)
        self.play(Create(cubo_raiz2), run_time=0.5)

        puntos_esquina = [
            (-2.0, -2.0, -2.0),
            (-2.5, -2.5, -2.5),
            (-2.8, -2.8, -2.8),
            (-2.9, -2.9, -2.9),
        ]

        cubos_borde = [cubo_raiz2]
        dots_borde = []

        for p in puntos_esquina:
            arbol2.insertar_punto(p)
            _, subs = arbol2.reg_ins[-1]

            dot = punto_a_dot(p, color=RED_C, radio=0.05)
            self.play(FadeIn(dot, scale=0.5), run_time=0.25)
            dots_borde.append(dot)

            for nodo_div in subs:
                nuevos = VGroup()
                for hijo in nodo_div.hijos:
                    c = nodo_a_cubo(hijo, color=MAROON_B, op=0.04)
                    nuevos.add(c)
                    cubos_borde.append(c)
                self.play(LaggedStart(*[Create(c) for c in nuevos],
                                      lag_ratio=0.03), run_time=0.5)
            self.wait(0.1)

        self.wait(0.6)
        self.play(FadeOut(texto_borde), FadeOut(subtexto), run_time=0.3)
        self.play(*[FadeOut(m) for m in cubos_borde + dots_borde], run_time=0.5)

        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=0.4)

        # complejidad
        titulo_comp = Text("Complejidad del Octree", font_size=36, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(titulo_comp)
        titulo_comp.to_edge(UP)
        self.play(Write(titulo_comp), run_time=0.5)

        f_ins = MathTex(r"\text{Inserción: } O(\log N)", font_size=38, color=GREEN_B)
        f_bus = MathTex(r"\text{Búsqueda: } O(\log N)", font_size=38, color=GREEN_B)
        f_rec = MathTex(r"\text{Recorrido: } O(N)", font_size=38, color=GREEN_B)
        formulas = VGroup(f_ins, f_bus, f_rec).arrange(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(formulas)
        self.play(Write(f_ins), run_time=0.5)
        self.wait(0.2)
        self.play(Write(f_bus), run_time=0.5)
        self.wait(0.2)
        self.play(Write(f_rec), run_time=0.5)
        self.wait(0.3)

        razon = VGroup(
            Text("¿Por qué?", font_size=26, color=YELLOW),
            Text("En cada nivel bajamos a 1 de 8 hijos →", font_size=20),
            Text("profundidad máxima ≈ log₈(N) = O(log N).", font_size=20),
            Text("Recorrer todos los nodos es O(N).", font_size=20),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        razon.next_to(formulas, DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(razon)
        self.play(FadeIn(razon, shift=UP * 0.3), run_time=0.5)
        self.wait(2)

        self.play(FadeOut(titulo_comp), FadeOut(formulas), FadeOut(razon), run_time=0.5)

        # cierre
        cierre = VGroup(
            Text("Animación de Octree", font_size=40, color=WHITE),
            Text("Leonardo Sanchez  &  Osorio Panduro", font_size=26, color=GRAY_B),
            Text("CS2023 — Septiembre 2026", font_size=20, color=GRAY),
        ).arrange(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(cierre)
        self.play(FadeIn(cierre, shift=UP * 0.4), run_time=0.7)
        self.wait(1.2)
        self.play(FadeOut(cierre), run_time=0.5)
