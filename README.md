# Proyecto 1 — OcTree

**CS2023 — Algoritmos y Estructuras de Datos**

## Integrantes

| Nombre           | GitHub         | Rol                         |
|------------------|----------------|-----------------------------|
| Osorio Panduro   | Edddd06        | Lógica e implementación C++ |
| Leonardo Sanchez | Leonardo       | Animación en Manim (Python) |

## Descripción

Implementación de un **Octree** (árbol de partición espacial 3D) en C++ junto con una animación explicativa hecha en **Manim** (estilo 3Blue1Brown) para el video de sustentación.

Un Octree divide recursivamente el espacio 3D en 8 octantes. Cuando un nodo supera su capacidad de puntos, se subdivide en 8 hijos iguales y redistribuye los puntos existentes. Esto permite búsquedas e inserciones en **O(log N)**.

## Estructura del proyecto

```
Proyecto1-OcTree/
├── Octree/
│   ├── include/
│   │   ├── Octree.h        # Clase Octree y struct OctreeNode
│   │   └── Point3D.h       # Struct Point3D
│   ├── src/
│   │   ├── Octree.cpp      # Implementación de la lógica del Octree
│   │   └── main_test.cpp   # Tests de inserción y búsqueda
│   └── CMakeLists.txt       # Build del proyecto C++
├── Animacion/
│   └── octree_animacion.py  # Script de Manim para el video
└── README.md
```

## Compilar el Octree (C++)

```bash
cd Octree
mkdir build && cd build
cmake ..
make
./main_test
```

## Renderizar la animación (Python / Manim)

Requisitos: Python 3.8+ y Manim Community Edition.

```bash
pip install manim
cd Animacion
python3 -m manim -pql octree_animacion.py OctreeAnimacion
```

- `-pql` = preview + quality low (rápido para probar).
- Para calidad alta: `python3 -m manim -pqh octree_animacion.py OctreeAnimacion`

## Operaciones animadas

La animación muestra las tres operaciones principales del Octree, todas impulsadas por una simulación en Python que replica exactamente la lógica del C++:

| Operación   | Descripción en la animación                                     |
|-------------|----------------------------------------------------------------|
| Inserción   | Se insertan puntos y se muestra la subdivisión automática en 8 |
| Búsqueda    | Se busca un punto existente (✓) y uno inexistente (✗)          |
| Recorrido   | Recorrido post-order (misma lógica que `liberar()`)            |

## Complejidad

| Operación  | Complejidad promedio | Razón                                                        |
|------------|----------------------|--------------------------------------------------------------|
| Inserción  | O(log N)             | En cada nivel se baja a 1 de 8 hijos → profundidad ~log₈(N) |
| Búsqueda   | O(log N)             | Misma razón: recorrido de raíz a hoja                        |
| Recorrido  | O(N)                 | Se visita cada nodo una sola vez                             |
