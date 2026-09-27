"""
Animacion de Octree — Proyecto CS2023
Autores: Leonardo Sanchez, Osorio Panduro
Renderizar:  python3 -m manim -pql octree_animacion.py OctreeAnimacion
"""

from manim import *
import numpy as np

# ---- Simulacion del Octree en Python (misma logica que el .cpp) ----

class OctreeNode:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ, capacidad):
        self.minX = minX
        self.minY = minY
        self.minZ = minZ
        self.maxX = maxX
        self.maxY = maxY
        self.maxZ = maxZ
        self.capacidad = capacidad
        self.puntos = []
        self.hijos = [None] * 8


class OctreeSim:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ, cap):
        self.root = OctreeNode(minX, minY, minZ, maxX, maxY, maxZ, cap)
        self.registro_insercion = []
        self.registro_busqueda = []

    def contiene(self, nodo, p):
        # checa si el punto cae dentro de los limites del nodo
        return (p[0] >= nodo.minX and p[0] <= nodo.maxX and
                p[1] >= nodo.minY and p[1] <= nodo.maxY and
                p[2] >= nodo.minZ and p[2] <= nodo.maxZ)

    def obtenerOctante(self, nodo, p):
        # sacamos el centro y vemos a cual de los 8 octantes va
        centroX = (nodo.minX + nodo.maxX) / 2.0
        centroY = (nodo.minY + nodo.maxY) / 2.0
        centroZ = (nodo.minZ + nodo.maxZ) / 2.0
        octante = 0
        if p[0] >= centroX:
            octante += 1
        if p[1] >= centroY:
            octante += 2
        if p[2] >= centroZ:
            octante += 4
        return octante

    def subdividir(self, nodo):
        # parte el nodo en 8 hijos (mismo orden que el cpp)
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

        # pasamos los puntos del padre a donde les toque
        for pt in nodo.puntos:
            oct = self.obtenerOctante(nodo, pt)
            nodo.hijos[oct].puntos.append(pt)
        nodo.puntos.clear()

    def insertar(self, nodo, p, subdivisiones):
        if not self.contiene(nodo, p):
            return False

        if nodo.hijos[0] is None:
            if len(nodo.puntos) < nodo.capacidad:
                nodo.puntos.append(p)
                return True
            else:
                self.subdividir(nodo)
                subdivisiones.append(nodo)

        oct = self.obtenerOctante(nodo, p)
        return self.insertar(nodo.hijos[oct], p, subdivisiones)

    def insertar_punto(self, p):
        subdivisiones = []
        ok = self.insertar(self.root, p, subdivisiones)
        self.registro_insercion.append((p, subdivisiones))
        return ok

    def buscar(self, nodo, p, camino):
        if not self.contiene(nodo, p):
            return False

        camino.append(nodo)

        # si es hoja buscamos en sus puntos
        if nodo.hijos[0] is None:
            for pt in nodo.puntos:
                if pt[0] == p[0] and pt[1] == p[1] and pt[2] == p[2]:
                    return True
            return False

        # si no bajamos al hijo que le toca
        oct = self.obtenerOctante(nodo, p)
        return self.buscar(nodo.hijos[oct], p, camino)

    def buscar_punto(self, p):
        camino = []
        encontrado = self.buscar(self.root, p, camino)
        self.registro_busqueda.append((p, camino, encontrado))
        return encontrado

    def recorrido_postorder(self, nodo, resultado):
        # mismo orden que liberar() del cpp: primero hijos, luego el nodo
        if nodo is None:
            return
        for i in range(8):
            self.recorrido_postorder(nodo.hijos[i], resultado)
        resultado.append(nodo)


# ---- Helpers para dibujar en Manim ----

def nodo_a_cubo(nodo, color=BLUE, opacidad=0.06):
    ancho  = nodo.maxX - nodo.minX
    alto   = nodo.maxY - nodo.minY
    prof   = nodo.maxZ - nodo.minZ
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
    cubo.set_fill(color, opacity=opacidad)
    return cubo


def punto_a_dot(p, color=YELLOW, radio=0.06):
    return Dot3D(point=np.array([p[0], p[1], p[2]]), color=color, radius=radio)


# para trackear que cubo de manim le corresponde a cada nodo
nodo_a_mob = {}


# ---- Escena principal ----

class OctreeAnimacion(ThreeDScene):

    def construct(self):

        # --- Portada ---
        titulo = Text("Animación de Octree", font_size=48, color=WHITE)
        nombres = Text("Leonardo Sanchez  &  Osorio Panduro", font_size=28, color=GRAY_B)
        curso = Text("CS2023 — Algoritmos y Estructuras de Datos", font_size=24, color=GRAY)
        grupo = VGroup(titulo, nombres, curso).arrange(DOWN, buff=0.4)

        self.play(FadeIn(grupo, shift=UP * 0.5), run_time=1.0)
        self.wait(1.2)
        self.play(FadeOut(grupo), run_time=0.5)

        # --- Intro: que es un Octree ---
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

        # --- Demo insercion (cap = 1) ---
        texto_demo = Text("Operación: Inserción (capacidad = 1)", font_size=30, color=GREEN_B)
        self.play(Write(texto_demo), run_time=0.6)
        self.wait(0.4)
        self.play(FadeOut(texto_demo), run_time=0.3)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        RANGO = 3.0
        arbol = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)

        cubo_raiz = nodo_a_cubo(arbol.root, color=BLUE, opacidad=0.04)
        nodo_a_mob[id(arbol.root)] = cubo_raiz
        self.play(Create(cubo_raiz), run_time=0.6)
        self.wait(0.2)

        puntos_demo = [
            ( 1.5,  1.5,  1.5),
            (-1.5, -1.5, -1.5),
        ]

        cubos_visibles = [cubo_raiz]
        dots_visibles  = []

        for p in puntos_demo:
            arbol.insertar_punto(p)
            punto_actual, subs = arbol.registro_insercion[-1]

            dot = punto_a_dot(punto_actual)
            self.play(FadeIn(dot, scale=0.5), run_time=0.35)
            dots_visibles.append(dot)

            for nodo_div in subs:
                nuevos_cubos = VGroup()
                for hijo in nodo_div.hijos:
                    c = nodo_a_cubo(hijo, color=TEAL, opacidad=0.05)
                    nodo_a_mob[id(hijo)] = c
                    nuevos_cubos.add(c)
                    cubos_visibles.append(c)
                self.play(LaggedStart(*[Create(c) for c in nuevos_cubos],
                                      lag_ratio=0.04), run_time=0.6)

            self.wait(0.2)

        self.wait(0.5)

        # --- Demo busqueda ---
        texto_busq = Text("Operación: Búsqueda", font_size=30, color=ORANGE)
        self.add_fixed_in_frame_mobjects(texto_busq)
        texto_busq.to_edge(UP)
        self.play(Write(texto_busq), run_time=0.5)
        self.wait(0.3)

        # buscar uno que si existe
        punto_buscar = (1.5, 1.5, 1.5)
        arbol.buscar_punto(punto_buscar)
        _, camino, _ = arbol.registro_busqueda[-1]

        cubos_iluminados = []
        for nodo_cam in camino:
            mob_id = id(nodo_cam)
            if mob_id in nodo_a_mob:
                cubo_cam = nodo_a_mob[mob_id]
                cubo_cam_copia = cubo_cam.copy()
                cubo_cam.set_stroke(ORANGE, width=2.5)
                cubo_cam.set_fill(ORANGE, opacity=0.12)
                cubos_iluminados.append((cubo_cam, cubo_cam_copia))
                self.play(cubo_cam.animate.set_fill(ORANGE, opacity=0.12), run_time=0.25)

        resultado_si = Text("✓ Punto (1.5, 1.5, 1.5) encontrado", font_size=22, color=GREEN)
        self.add_fixed_in_frame_mobjects(resultado_si)
        resultado_si.next_to(texto_busq, DOWN, buff=0.25)
        self.play(FadeIn(resultado_si), run_time=0.4)
        self.wait(0.6)

        # restauramos los colores
        for cubo_cam, cubo_orig in cubos_iluminados:
            cubo_cam.set_stroke(cubo_orig.get_stroke_color(), width=1.5)
            cubo_cam.set_fill(cubo_orig.get_fill_color(), opacity=cubo_orig.get_fill_opacity())

        self.play(FadeOut(resultado_si), run_time=0.3)

        # buscar uno que NO existe
        punto_no = (0.0, 0.0, 0.0)
        arbol.buscar_punto(punto_no)
        _, camino2, _ = arbol.registro_busqueda[-1]

        cubos_iluminados2 = []
        for nodo_cam in camino2:
            mob_id = id(nodo_cam)
            if mob_id in nodo_a_mob:
                cubo_cam = nodo_a_mob[mob_id]
                cubo_cam_copia = cubo_cam.copy()
                cubo_cam.set_stroke(RED, width=2.5)
                cubo_cam.set_fill(RED, opacity=0.10)
                cubos_iluminados2.append((cubo_cam, cubo_cam_copia))
                self.play(cubo_cam.animate.set_fill(RED, opacity=0.10), run_time=0.25)

        resultado_no = Text("✗ Punto (0, 0, 0) no encontrado", font_size=22, color=RED)
        self.add_fixed_in_frame_mobjects(resultado_no)
        resultado_no.next_to(texto_busq, DOWN, buff=0.25)
        self.play(FadeIn(resultado_no), run_time=0.4)
        self.wait(0.6)

        for cubo_cam, cubo_orig in cubos_iluminados2:
            cubo_cam.set_stroke(cubo_orig.get_stroke_color(), width=1.5)
            cubo_cam.set_fill(cubo_orig.get_fill_color(), opacity=cubo_orig.get_fill_opacity())

        self.play(FadeOut(resultado_no), FadeOut(texto_busq), run_time=0.3)
        self.play(*[FadeOut(m) for m in cubos_visibles + dots_visibles], run_time=0.5)
        nodo_a_mob.clear()

        # --- Demo recorrido postorder (como liberar) ---
        texto_rec = Text("Operación: Recorrido post-order (liberar)", font_size=30, color=PURPLE_B)
        self.add_fixed_in_frame_mobjects(texto_rec)
        texto_rec.to_edge(UP)
        self.play(Write(texto_rec), run_time=0.5)
        self.wait(0.3)

        # armamos otro octree chico para esta parte
        arbol_rec = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)
        arbol_rec.insertar_punto((1.5, 1.5, 1.5))
        arbol_rec.insertar_punto((-1.5, -1.5, -1.5))

        cubos_rec = []

        def dibujar_nodos(nodo):
            if nodo is None:
                return
            c = nodo_a_cubo(nodo, color=BLUE_D, opacidad=0.04)
            nodo_a_mob[id(nodo)] = c
            cubos_rec.append(c)
            self.add(c)
            for i in range(8):
                dibujar_nodos(nodo.hijos[i])

        dibujar_nodos(arbol_rec.root)
        self.wait(0.3)

        # sacamos el orden postorder y animamos cada nodo desapareciendo
        orden_post = []
        arbol_rec.recorrido_postorder(arbol_rec.root, orden_post)

        for nodo_po in orden_post:
            mob_id = id(nodo_po)
            if mob_id in nodo_a_mob:
                cubo_po = nodo_a_mob[mob_id]
                self.play(
                    cubo_po.animate.set_stroke(PURPLE, width=2.5).set_fill(PURPLE, opacity=0.15),
                    run_time=0.08
                )
                self.play(FadeOut(cubo_po, scale=0.7), run_time=0.08)

        self.play(FadeOut(texto_rec), run_time=0.3)
        nodo_a_mob.clear()

        # --- Caso borde: puntos pegados en una esquina ---
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
        cubo_raiz2 = nodo_a_cubo(arbol2.root, color=BLUE, opacidad=0.04)
        self.play(Create(cubo_raiz2), run_time=0.5)

        puntos_esquina = [
            (-2.0, -2.0, -2.0),
            (-2.5, -2.5, -2.5),
            (-2.8, -2.8, -2.8),
            (-2.9, -2.9, -2.9),
        ]

        cubos_borde = [cubo_raiz2]
        dots_borde  = []

        for p in puntos_esquina:
            arbol2.insertar_punto(p)
            punto_actual, subs = arbol2.registro_insercion[-1]

            dot = punto_a_dot(punto_actual, color=RED_C, radio=0.05)
            self.play(FadeIn(dot, scale=0.5), run_time=0.25)
            dots_borde.append(dot)

            for nodo_div in subs:
                nuevos = VGroup()
                for hijo in nodo_div.hijos:
                    c = nodo_a_cubo(hijo, color=MAROON_B, opacidad=0.04)
                    nuevos.add(c)
                    cubos_borde.append(c)
                self.play(LaggedStart(*[Create(c) for c in nuevos],
                                      lag_ratio=0.03), run_time=0.5)

            self.wait(0.1)

        self.wait(0.6)
        self.play(FadeOut(texto_borde), FadeOut(subtexto), run_time=0.3)
        self.play(*[FadeOut(m) for m in cubos_borde + dots_borde], run_time=0.5)

        # volvemos a 2d para las mates
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=0.4)

        # --- Complejidad ---
        titulo_comp = Text("Complejidad del Octree", font_size=36, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(titulo_comp)
        titulo_comp.to_edge(UP)
        self.play(Write(titulo_comp), run_time=0.5)

        formula_ins = MathTex(
            r"\text{Inserción: } O(\log N)", font_size=38, color=GREEN_B
        )
        formula_busq = MathTex(
            r"\text{Búsqueda: } O(\log N)", font_size=38, color=GREEN_B
        )
        formula_rec = MathTex(
            r"\text{Recorrido: } O(N)", font_size=38, color=GREEN_B
        )
        formulas = VGroup(formula_ins, formula_busq, formula_rec).arrange(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(formulas)
        self.play(Write(formula_ins), run_time=0.5)
        self.wait(0.2)
        self.play(Write(formula_busq), run_time=0.5)
        self.wait(0.2)
        self.play(Write(formula_rec), run_time=0.5)
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

        # --- Cierre ---
        cierre = VGroup(
            Text("Animación de Octree", font_size=40, color=WHITE),
            Text("Leonardo Sanchez  &  Osorio Panduro", font_size=26, color=GRAY_B),
            Text("CS2023 — Septiembre 2026", font_size=20, color=GRAY),
        ).arrange(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(cierre)
        self.play(FadeIn(cierre, shift=UP * 0.4), run_time=0.7)
        self.wait(1.2)
        self.play(FadeOut(cierre), run_time=0.5)
