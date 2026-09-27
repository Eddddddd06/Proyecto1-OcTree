# Proyecto 1 — OcTree

**CS2023 — Algoritmos y Estructuras de Datos**

## Integrantes

- Osorio Panduro — Lógica e implementación C++
- Leonardo Sanchez — Animación en Manim (Python)

## Descripción

Implementación de un Octree en C++ con una animación en Manim para el video de sustentación. El Octree divide recursivamente el espacio 3D en 8 octantes, permitiendo inserciones y búsquedas en O(log N).

## Estructura

```
Proyecto1-OcTree/
├── Octree/
│   ├── include/
│   │   ├── Octree.h
│   │   └── Point3D.h
│   ├── src/
│   │   ├── Octree.cpp
│   │   └── main_test.cpp
│   └── CMakeLists.txt
├── Animacion/
│   └── octree_animacion.py
└── README.md
```

## Compilar (C++)

```bash
cd Octree
mkdir build && cd build
cmake ..
make
./main_test
```

## Renderizar animación

```bash
pip install manim
cd Animacion
python3 -m manim -pql octree_animacion.py OctreeAnimacion
```

Para calidad alta: `python3 -m manim -pqh octree_animacion.py OctreeAnimacion`

## Operaciones animadas

- Inserción con subdivisión automática
- Búsqueda exitosa y fallida
- Recorrido post-order (misma lógica que liberar)

## Complejidad

- Inserción: O(log N)
- Búsqueda: O(log N)
- Recorrido: O(N)
