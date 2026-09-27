# Proyecto 1 — OcTree

**CS2023 — Algoritmos y Estructuras de Datos**

## Integrantes

| Nombre   | GitHub   | Rol                         |
|----------|----------|-----------------------------|
| Edddd06  | Edddd06  | Lógica e implementación C++ |
| Leonardo | Leonardo | Animación en Manim (Python) |

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
manim -pql octree_animacion.py OctreeAnimacion
```

- `-pql` = preview + quality low (rápido para probar).
- Para calidad alta: `manim -pqh octree_animacion.py OctreeAnimacion`

## Complejidad

| Operación  | Complejidad promedio | Razón                                                        |
|------------|----------------------|--------------------------------------------------------------|
| Inserción  | O(log N)             | En cada nivel se baja a 1 de 8 hijos → profundidad ~log₈(N) |
| Búsqueda   | O(log N)             | Misma razón: recorrido de raíz a hoja                        |

## Historial de commits

### Commits on Sep 26, 2026

- **Render final del caso borde y limpieza de escena** — Leonardo committed today
- **Agregando textos de complejidad O(log N) y cierre** — Leonardo committed today
- **Ajustando tiempos de animación para no pasar de 2 min** — Leonardo committed today

### Commits on Sep 25, 2026

- **Configurando la escena 3D y portada en Manim** — Leonardo committed 1 day ago
- **Dibujando el primer cubo partiendo en 8 subcubos** — Leonardo committed 1 day ago

### Commits on Sep 23, 2026

- **Agregando las ultimas funciones** — Edddd06 committed 3 days ago
- **Primeras funciones añadidas al Octree.cpp** — Edddd06 committed 3 days ago
