<h1 align="center">Proyecto 1 — OcTree</h1>

<p align="center">
  <b>CS2023 — Algoritmos y Estructuras de Datos</b><br>
  Estructura de datos espacial en 3D implementada en C++ , con una app de visualización en raylib
</p>

---

## Integrantes

| Integrante | Responsabilidad |
|---|---|
| Osorio Panduro | Lógica e implementación del Octree en C++ |
| Leonardo Sanchez | Visualización 3D con raylib (C++) |
| Diego Antonio Rosario | Visualización 3D con raylib (C++) |

---

## Descripción

Un **Octree** divide recursivamente una región cúbica del espacio 3D en 8 octantes. Cuando una hoja se
pasa de su capacidad, se subdivide y reparte sus puntos entre los 8 hijos. Eso hace que insertar y
buscar cuesten **O(log N)** en lugar de recorrer todos los puntos.

El proyecto tiene dos partes:

- **La estructura** (`Octree/`) — la clase `Octree` y el struct `Point3D`, sin ninguna dependencia
  externa. Es la que se prueba por consola.
- **La visualización** (`animacion/motor_grafico/`) — una app en raylib que **no simula nada**: crea un
  objeto `Octree` real y dibuja exactamente lo que la clase reporta (los límites `minX..maxZ` de cada
  nodo, los puntos guardados, el camino que devuelve `buscar()` y el orden de `recorrerPostorder()`).
  raylib solo se encarga de la cámara 3D, las cajas, los puntos y los controles.

---

## Estructura del repositorio

```
Proyecto1-OcTree/
├── Octree/
│   ├── include/
│   │   ├── Point3D.h          punto 3D con operator== para comparar
│   │   └── Octree.h           clase Octree : nodo privado + InfoNodo de solo lectura
│   ├── src/
│   │   ├── Octree.cpp         toda la lógica : insertar , buscar , subdividir , postorder , liberar
│   │   └── main_test.cpp      55 pruebas por consola (9 casos , incluidos los borde)
│   └── CMakeLists.txt         compila los 2 ejecutables y baja raylib si hace falta
├── animacion/
│   └── motor_grafico/
│       └── octree_visual.cpp  app de visualización , usa el mismo Octree.cpp
└── README.md
```

> `Octree/build/` y `.vscode/` se generan localmente y están en `.gitignore`, no forman parte del repo.

---

## Requisitos

- Compilador con **C++17** (`g++` o `clang++`)
- **CMake 3.14** o superior
- Para la app de visualización, las librerías de desarrollo de OpenGL/X11 que pide raylib.
  En Arch: `sudo pacman -S base-devel cmake mesa libx11 libxrandr libxinerama libxcursor libxi`

No hay que instalar raylib a mano: si CMake no la encuentra en el sistema, la descarga y compila sola
dentro de `build/` (por eso la primera compilación tarda más).

---

## Compilar y ejecutar

```bash
cd Octree
cmake -S . -B build
cmake --build build -j8
```

Eso deja dos ejecutables en `Octree/build/`:

```bash
./build/main_test        # pruebas por consola de la clase Octree
./build/octree_visual    # app de visualización 3D
```

`main_test` sale con código `0` si todas las pruebas pasan y con `1` si alguna falla, así que sirve
para verificar rápido que la estructura sigue correcta después de cualquier cambio.

<details>
<summary><b>Desde VS Code</b></summary>

<br>

Con la carpeta `.vscode/` local:

- `Ctrl+Shift+B` corre la tarea **CMake: build** (compila los dos ejecutables).
- `F5` compila y lanza `octree_visual` con el depurador.
- También están las tareas **Ejecutar main_test** y **Ejecutar octree_visual**.

La primera compilación tiene que ser con CMake, porque es la que descarga raylib dentro de `build/`.
Después de eso el botón ▶ ("Run C/C++ File") también funciona: la tarea
`C/C++: g++ build active file` compila el archivo activo junto a `Octree.cpp` y enlaza raylib.

</details>

---

## La clase `Octree`

```cpp
Octree(float mX, float mY, float mZ, float maX, float maY, float maZ, int cap) ;
```

Crea el árbol con los límites de la raíz y la capacidad de puntos por nodo.

| Método | Devuelve | Qué hace |
|---|---|---|
| `insertar(p)` | `bool` | Inserta el punto. `false` si cae fuera de los límites de la raíz. |
| `buscar(p)` | `bool` | Busca el punto bajando solo por el octante que le toca. |
| `buscar(p, camino)` | `bool` | La misma búsqueda, pero además llena `camino` con los nodos recorridos. |
| `recorrerPostorder(salida)` | `void` | Llena `salida` con todos los nodos: primero los 8 hijos, al final el padre. |
| `~Octree()` | — | Libera toda la memoria con `liberar()`, en ese mismo orden post-order. |

`InfoNodo` es una copia de solo lectura de un nodo (`minX..maxZ`, `puntos`, `esHoja`, `profundidad`).
Existe para que la visualización pueda dibujar el árbol **sin tocar los nodos internos**, que siguen
siendo privados.

<details>
<summary><b>Ejemplo mínimo</b></summary>

<br>

```cpp
#include "Octree.h"

Octree arbol(-4,-4,-4 , 4,4,4 , 1) ;   // cubo de -4 a 4 , 1 punto por hoja

arbol.insertar(Point3D(2,2,2)) ;       // true , entra en la raíz
arbol.insertar(Point3D(-2,-2,-2)) ;    // true , la raíz se subdivide en 8
arbol.insertar(Point3D(10,10,10)) ;    // false , está fuera de los límites

arbol.buscar(Point3D(2,2,2)) ;         // true

vector<Octree::InfoNodo> camino ;
arbol.buscar(Point3D(2,2,2) , camino) ; // camino = raíz -> hijo -> hoja

vector<Octree::InfoNodo> orden ;
arbol.recorrerPostorder(orden) ;        // los 9 nodos , la raíz de última
```

</details>

---

## Cómo funciona por dentro

**En qué octante cae un punto.** Se compara contra el centro del nodo y se arma un índice con bits:

| Bit | Condición | Suma |
|---|---|---|
| X | `p.x >= centroX` | `+1` |
| Y | `p.y >= centroY` | `+2` |
| Z | `p.z >= centroZ` | `+4` |

Así los 8 octantes quedan numerados del `0` al `7` sin usar `if` anidados, y `subdividir()` crea los
hijos en ese mismo orden.

**Subdivisión.** `insertar()` solo subdivide cuando una hoja ya está llena. Al subdividir, los puntos
que tenía el padre se reparten entre los hijos y el vector del padre se limpia, para que un punto no
quede duplicado en dos niveles.

**Límites inclusivos.** `contiene()` usa `>=` y `<=`, así que un punto que cae justo en una esquina o
en una cara del cubo sí entra.

**Tope de subdivisiones.** Hay un límite de **12 niveles** (`PROFUNDIDAD_MAXIMA`). Dos puntos idénticos
caen siempre en el mismo octante, así que subdividir no los separaría nunca: sin el tope, `insertar()`
se subdividiría para siempre y desbordaría la pila. Al llegar al tope, la hoja simplemente guarda los
puntos aunque se pase de su capacidad.

---

## Pruebas por consola

`./build/main_test` corre 9 casos (55 comprobaciones), varios de ellos casos borde:

| # | Caso | Qué verifica |
|---|---|---|
| 1 | Octree vacío | Solo existe la raíz, `buscar()` da `false`, profundidad 0 |
| 2 | Inserción sin subdivisión | Con capacidad 4 y 4 puntos, la raíz no se subdivide |
| 3 | Inserción con subdivisión | Al pasarse de capacidad aparecen los 8 hijos y los puntos no se pierden |
| 4 | Fuera de límites | `insertar()` da `false` afuera, y `true` justo en las esquinas |
| 5 | Búsqueda | Éxito y fallo, y que el camino baje un nivel a la vez hasta una hoja |
| 6 | Post-order | Devuelve los 9 nodos con la raíz de última, y solo la raíz en un árbol vacío |
| 7 | Puntos concentrados | Una sola inserción encadena varias subdivisiones seguidas |
| 8 | Punto repetido | Con capacidad libre, las dos copias se guardan |
| 9 | Repetidos con capacidad llena | El tope de profundidad evita la recursión infinita |

---

## App de visualización

```bash
./build/octree_visual
```

Todo lo que se ve en pantalla sale de la clase real. Los contadores de arriba a la izquierda (nodos,
hojas, puntos guardados, profundidad, límites de la raíz) se recalculan pidiéndole al árbol su
`recorrerPostorder()` después de cada operación.

### Controles

| Tecla | Acción |
|---|---|
| `1` `2` `3` | cambiar de escena |
| `ESPACIO` | insertar el siguiente punto con `Octree::insertar()` |
| `A` | inserción automática (un punto cada 0.8 s) |
| `B` | `Octree::buscar()` de un punto que **sí** existe |
| `N` | `Octree::buscar()` de un punto que **no** existe |
| `T` | `Octree::recorrerPostorder()` (mismo orden que `liberar()`) |
| `R` | reiniciar la escena (octree vacío) |
| mouse | arrastrar para girar, rueda para zoom |

### Qué significa cada color

| Color | Qué es |
|---|---|
| 🔵 azul | nodo raíz |
| 🩵 turquesa | hoja |
| 🔷 azul oscuro | nodo interno (ya subdividido) |
| 🟡 amarillo | puntos guardados (el último insertado se ve más grande) |
| 🟠 naranja | camino de una búsqueda **exitosa** |
| 🔴 rojo | camino de una búsqueda **fallida** |
| 🟣 morado | nodo que toca en el recorrido post-order |

En el post-order los nodos ya visitados **desaparecen**, para que se vea que es el mismo orden en que
`liberar()` borra la memoria: primero los hijos, al final la raíz.

### Escenas

1. **Caso borde — octree vacío y un solo punto.** Arranca sin puntos, se inserta uno y la raíz no
   llega a subdividirse.
2. **Inserción con subdivisión.** Con capacidad 1, cada vez que una hoja se pasa aparecen sus 8 hijos
   reales. Incluye a propósito un punto fuera de los límites donde `insertar()` devuelve `false`.
3. **Caso borde — puntos concentrados.** Puntos muy pegados en una esquina: una sola inserción
   provoca varias subdivisiones seguidas.

---

## Operaciones y complejidad

| Operación | Complejidad | Nota |
|---|---|---|
| Inserción (`insertar`) | O(log N) | Baja por un solo octante; subdivide si la hoja está llena |
| Búsqueda (`buscar`) | O(log N) | Descarta 7 de 8 octantes en cada nivel |
| Recorrido (`recorrerPostorder`) | O(N) | Visita todos los nodos |
| Liberación (`liberar`) | O(N) | Mismo orden post-order, lo llama el destructor |

Las cotas O(log N) valen cuando los puntos están razonablemente repartidos. Si se concentran mucho en
una misma zona (escena 3), el árbol se vuelve profundo en ese rincón y la búsqueda se acerca al peor
caso, hasta el tope de 12 niveles.
