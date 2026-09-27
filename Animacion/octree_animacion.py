"""
Animación de Octree — Proyecto CS2023
Autores: Leonardo, Edddd06
Renderizar con:  manim -pql octree_animacion.py OctreeAnimacion
"""

from manim import *
import numpy as np

# =============================================================================
# Simulación del Octree en Python
# (replica la lógica EXACTA de Octree.cpp / Octree.h / Point3D.h)
# =============================================================================

class OctreeNode:
    """Equivalente al struct OctreeNode del .h"""
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ, capacidad):
        self.minX = minX
        self.minY = minY
        self.minZ = minZ
        self.maxX = maxX
        self.maxY = maxY
        self.maxZ = maxZ
        self.capacidad = capacidad
        self.puntos = []           # vector<Point3D>
        self.hijos = [None] * 8    # OctreeNode* hijos[8]


class OctreeSim:
    """Equivalente a la clase Octree del .cpp"""

    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ, cap):
        self.root = OctreeNode(minX, minY, minZ, maxX, maxY, maxZ, cap)
        self.registro = []  # guarda (punto, subdivisiones_que_ocurrieron)

    # --- funciones auxiliares (misma lógica que Octree.cpp) ---

    def contiene(self, nodo, p):
        """Revisa si el punto esta dentro del cuadrante (linea 18‑25 del .cpp)"""
        return (p[0] >= nodo.minX and p[0] <= nodo.maxX and
                p[1] >= nodo.minY and p[1] <= nodo.maxY and
                p[2] >= nodo.minZ and p[2] <= nodo.maxZ)

    def obtenerOctante(self, nodo, p):
        """Calcula octante con la misma formula bit a bit del .cpp (linea 28‑48)"""
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
        """Divide en 8 hijos (linea 51‑73 del .cpp) — orden IDENTICO"""
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

        # redistribuimos puntos del padre a los hijos
        for pt in nodo.puntos:
            oct = self.obtenerOctante(nodo, pt)
            nodo.hijos[oct].puntos.append(pt)
        nodo.puntos.clear()

    def insertar(self, nodo, p, subdivisiones):
        """Inserción recursiva (linea 76‑96 del .cpp)"""
        if not self.contiene(nodo, p):
            return False

        if nodo.hijos[0] is None:
            if len(nodo.puntos) < nodo.capacidad:
                nodo.puntos.append(p)
                return True
            else:
                self.subdividir(nodo)
                subdivisiones.append(nodo)  # registramos que este nodo se dividió

        oct = self.obtenerOctante(nodo, p)
        return self.insertar(nodo.hijos[oct], p, subdivisiones)

    def insertar_punto(self, p):
        """Wrapper público — equivalente al insertar(const Point3D& p) del .cpp"""
        subdivisiones = []
        ok = self.insertar(self.root, p, subdivisiones)
        self.registro.append((p, subdivisiones))
        return ok


# =============================================================================
# Funciones de ayuda para Manim
# =============================================================================

def nodo_a_cubo(nodo, color=BLUE, opacidad=0.06):
    """Convierte un OctreeNode en un cubo 3D de Manim centrado correctamente."""
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
    """Convierte una tupla (x,y,z) en una esfera pequeña."""
    return Dot3D(point=np.array([p[0], p[1], p[2]]), color=color, radius=radio)


# =============================================================================
# Escena principal de Manim
# =============================================================================

class OctreeAnimacion(ThreeDScene):

    def construct(self):
        # ------------------------------------------------------------------
        # 0 · PORTADA — nombres y título
        # ------------------------------------------------------------------
        titulo = Text("Animación de Octree", font_size=48, color=WHITE)
        nombres = Text("Leonardo  &  Edddd06", font_size=30, color=GRAY_B)
        curso = Text("CS2023 — Algoritmos y Estructuras de Datos", font_size=24, color=GRAY)
        grupo = VGroup(titulo, nombres, curso).arrange(DOWN, buff=0.4)

        self.play(FadeIn(grupo, shift=UP * 0.5), run_time=1.2)
        self.wait(1.5)
        self.play(FadeOut(grupo), run_time=0.6)

        # ------------------------------------------------------------------
        # 1 · INTRO CONCEPTUAL — qué es un Octree
        # ------------------------------------------------------------------
        intro1 = Text("¿Qué es un Octree?", font_size=40, color=BLUE_B)
        self.play(Write(intro1), run_time=0.8)
        self.wait(0.6)
        self.play(intro1.animate.to_edge(UP), run_time=0.5)

        explicacion = VGroup(
            Text("• Es un árbol de partición espacial en 3D.", font_size=24),
            Text("• Cada nodo representa un cubo (cuadrante).", font_size=24),
            Text("• Cuando un cubo supera su capacidad,", font_size=24),
            Text("  se subdivide en 8 hijos iguales.", font_size=24),
            Text("• Se usa en motores gráficos, detección de", font_size=24),
            Text("  colisiones 3D y simulaciones de partículas.", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(intro1, DOWN, buff=0.5)

        for linea in explicacion:
            self.play(FadeIn(linea, shift=RIGHT * 0.3), run_time=0.4)
        self.wait(2)
        self.play(FadeOut(VGroup(intro1, explicacion)), run_time=0.6)

        # ------------------------------------------------------------------
        # 2 · ANIMACIÓN PRINCIPAL — inserción y subdivisión con cap = 1
        # ------------------------------------------------------------------
        texto_demo = Text("Demo: Inserción con capacidad = 1", font_size=32, color=GREEN_B)
        self.play(Write(texto_demo), run_time=0.7)
        self.wait(0.6)
        self.play(FadeOut(texto_demo), run_time=0.4)

        # Configuramos la cámara 3D
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # Creamos el Octree con el mismo rango que sería razonable para la anim
        RANGO = 3.0
        arbol = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)

        # Cubo raíz visual
        cubo_raiz = nodo_a_cubo(arbol.root, color=BLUE, opacidad=0.04)
        self.play(Create(cubo_raiz), run_time=0.8)
        self.wait(0.3)

        # Puntos escogidos para la demo (bien separados para que sea claro)
        puntos_demo = [
            ( 1.5,  1.5,  1.5),   # octante 7  (x+, y+, z+)
            (-1.5, -1.5, -1.5),   # octante 0  (x-, y-, z-)
        ]

        cubos_visibles = [cubo_raiz]  # para poder borrarlos después
        dots_visibles  = []

        for p in puntos_demo:
            arbol.insertar_punto(p)
            punto_actual, subs = arbol.registro[-1]

            # Mostrar el punto
            dot = punto_a_dot(punto_actual)
            self.play(FadeIn(dot, scale=0.5), run_time=0.4)
            dots_visibles.append(dot)

            # Si hubo subdivisiones, dibujar los 8 hijos de cada nodo dividido
            for nodo_div in subs:
                nuevos_cubos = VGroup()
                for hijo in nodo_div.hijos:
                    c = nodo_a_cubo(hijo, color=TEAL, opacidad=0.05)
                    nuevos_cubos.add(c)
                    cubos_visibles.append(c)
                self.play(LaggedStart(*[Create(c) for c in nuevos_cubos],
                                      lag_ratio=0.05), run_time=0.8)

            self.wait(0.3)

        # Breve pausa para que se vea el resultado
        self.wait(0.8)

        # Limpiamos escena para el caso borde
        self.play(*[FadeOut(m) for m in cubos_visibles + dots_visibles], run_time=0.6)

        # ------------------------------------------------------------------
        # 3 · CASO BORDE — puntos muy pegados en una esquina
        # ------------------------------------------------------------------
        texto_borde = Text("Caso borde: puntos concentrados", font_size=32, color=RED_B)
        self.add_fixed_in_frame_mobjects(texto_borde)
        texto_borde.to_edge(UP)
        self.play(Write(texto_borde), run_time=0.7)
        self.wait(0.5)

        subtexto = Text(
            "Muchos puntos pegados → subdivisiones profundas en un solo lado",
            font_size=22, color=GRAY_B
        )
        self.add_fixed_in_frame_mobjects(subtexto)
        subtexto.next_to(texto_borde, DOWN, buff=0.2)
        self.play(FadeIn(subtexto), run_time=0.5)
        self.wait(0.5)

        # Nuevo octree para este caso
        arbol2 = OctreeSim(-RANGO, -RANGO, -RANGO, RANGO, RANGO, RANGO, cap=1)
        cubo_raiz2 = nodo_a_cubo(arbol2.root, color=BLUE, opacidad=0.04)
        self.play(Create(cubo_raiz2), run_time=0.6)

        # Puntos concentrados en la esquina negativa (octante 0 siempre)
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
            punto_actual, subs = arbol2.registro[-1]

            dot = punto_a_dot(punto_actual, color=RED_C, radio=0.05)
            self.play(FadeIn(dot, scale=0.5), run_time=0.3)
            dots_borde.append(dot)

            for nodo_div in subs:
                nuevos = VGroup()
                for hijo in nodo_div.hijos:
                    c = nodo_a_cubo(hijo, color=MAROON_B, opacidad=0.04)
                    nuevos.add(c)
                    cubos_borde.append(c)
                self.play(LaggedStart(*[Create(c) for c in nuevos],
                                      lag_ratio=0.04), run_time=0.6)

            self.wait(0.15)

        self.wait(1)
        self.play(FadeOut(texto_borde), FadeOut(subtexto), run_time=0.4)
        self.play(*[FadeOut(m) for m in cubos_borde + dots_borde], run_time=0.6)

        # Volvemos a 2D para las mates
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=0.5)

        # ------------------------------------------------------------------
        # 4 · COMPLEJIDAD — O(log N)
        # ------------------------------------------------------------------
        titulo_comp = Text("Complejidad del Octree", font_size=38, color=BLUE_B)
        self.add_fixed_in_frame_mobjects(titulo_comp)
        titulo_comp.to_edge(UP)
        self.play(Write(titulo_comp), run_time=0.7)

        formula_busq = MathTex(
            r"\text{Búsqueda: } O(\log N)", font_size=40, color=GREEN_B
        )
        formula_ins = MathTex(
            r"\text{Inserción: } O(\log N)", font_size=40, color=GREEN_B
        )
        formulas = VGroup(formula_busq, formula_ins).arrange(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(formulas)
        self.play(Write(formula_busq), run_time=0.6)
        self.wait(0.3)
        self.play(Write(formula_ins), run_time=0.6)
        self.wait(0.5)

        razon = VGroup(
            Text("¿Por qué?", font_size=28, color=YELLOW),
            Text("En cada nivel del árbol, solo bajamos a 1 de los", font_size=22),
            Text("8 hijos → la profundidad máxima es proporcional", font_size=22),
            Text("a log₈(N), que es O(log N).", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        razon.next_to(formulas, DOWN, buff=0.6)
        self.add_fixed_in_frame_mobjects(razon)
        self.play(FadeIn(razon, shift=UP * 0.3), run_time=0.7)
        self.wait(2.5)

        self.play(FadeOut(titulo_comp), FadeOut(formulas), FadeOut(razon), run_time=0.6)

        # ------------------------------------------------------------------
        # 5 · CIERRE
        # ------------------------------------------------------------------
        cierre = VGroup(
            Text("Animación de Octree", font_size=40, color=WHITE),
            Text("Leonardo  &  Edddd06", font_size=28, color=GRAY_B),
            Text("CS2023 — Septiembre 2026", font_size=22, color=GRAY),
        ).arrange(DOWN, buff=0.35)
        self.add_fixed_in_frame_mobjects(cierre)
        self.play(FadeIn(cierre, shift=UP * 0.4), run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(cierre), run_time=0.6)
