#include <iostream>
#include <vector>
#include "Octree.h"

using namespace std ; 

// Pruebas por consola de la clase Octree.
// Cada prueba usa el Octree real y compara lo que devuelve contra lo que se espera.
// Al final se imprime el resumen y el programa sale con codigo 1 si algo fallo.

static int totales = 0 ; 
static int fallidas = 0 ; 

// compara lo obtenido con lo esperado y va llevando la cuenta
static void revisar(const string& nombre , bool obtenido , bool esperado){
    totales++ ; 
    if(obtenido==esperado){
        cout << "  [ok]    " << nombre << endl ; 
    }else{
        fallidas++ ; 
        cout << "  [FALLO] " << nombre
             << "  (esperaba " << (esperado ? "true" : "false")
             << " y devolvio " << (obtenido ? "true" : "false") << ")" << endl ; 
    }
}

// la misma idea pero con enteros , para contar nodos , puntos , etc
static void revisarInt(const string& nombre , int obtenido , int esperado){
    totales++ ; 
    if(obtenido==esperado){
        cout << "  [ok]    " << nombre << "  (" << obtenido << ")" << endl ; 
    }else{
        fallidas++ ; 
        cout << "  [FALLO] " << nombre
             << "  (esperaba " << esperado << " y devolvio " << obtenido << ")" << endl ; 
    }
}

// cuenta cuantos puntos hay guardados en todo el arbol
static int contarPuntos(const Octree& arbol){
    vector<Octree::InfoNodo> nodos ; 
    arbol.recorrerPostorder(nodos) ; 
    int total = 0 ; 
    for(int i = 0 ; i < (int)nodos.size() ; i++){
        total += (int)nodos[i].puntos.size() ; 
    }
    return total ; 
}

// cuantos nodos tiene el arbol en total
static int contarNodos(const Octree& arbol){
    vector<Octree::InfoNodo> nodos ; 
    arbol.recorrerPostorder(nodos) ; 
    return (int)nodos.size() ; 
}

// la profundidad mas grande que alcanzo el arbol
static int profundidadMaxima(const Octree& arbol){
    vector<Octree::InfoNodo> nodos ; 
    arbol.recorrerPostorder(nodos) ; 
    int prof = 0 ; 
    for(int i = 0 ; i < (int)nodos.size() ; i++){
        if(nodos[i].profundidad > prof){
            prof = nodos[i].profundidad ; 
        }
    }
    return prof ; 
}


// caso borde : un octree recien creado solo tiene la raiz y no encuentra nada
static void pruebaOctreeVacio(){
    cout << "1. caso borde : octree vacio" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 2) ; 

    revisarInt("el arbol arranca con un solo nodo (la raiz)" , contarNodos(arbol) , 1) ; 
    revisarInt("no hay ningun punto guardado" , contarPuntos(arbol) , 0) ; 
    revisar("buscar() en un arbol vacio devuelve false" , arbol.buscar(Point3D(1,1,1)) , false) ; 
    revisarInt("la profundidad es 0" , profundidadMaxima(arbol) , 0) ; 

    cout << endl ; 
}

// insercion normal : mientras no se pase la capacidad la hoja no se subdivide
static void pruebaInsercionSinSubdividir(){
    cout << "2. insercion sin subdivision (capacidad = 4)" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 4) ; 

    revisar("insertar(1,1,1)" , arbol.insertar(Point3D(1,1,1)) , true) ; 
    revisar("insertar(-2,3,0)" , arbol.insertar(Point3D(-2,3,0)) , true) ; 
    revisar("insertar(3,-3,2)" , arbol.insertar(Point3D(3,-3,2)) , true) ; 
    revisar("insertar(0,0,-1)" , arbol.insertar(Point3D(0,0,-1)) , true) ; 

    revisarInt("los 4 puntos quedaron guardados" , contarPuntos(arbol) , 4) ; 
    revisarInt("la raiz sigue siendo el unico nodo" , contarNodos(arbol) , 1) ; 
    revisarInt("la profundidad sigue en 0" , profundidadMaxima(arbol) , 0) ; 

    cout << endl ; 
}

// al pasarse de capacidad subdividir() tiene que crear los 8 hijos
static void pruebaSubdivision(){
    cout << "3. insercion con subdivision (capacidad = 1)" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 1) ; 

    arbol.insertar(Point3D(2,2,2)) ; 
    revisarInt("con 1 punto todavia no se subdivide" , contarNodos(arbol) , 1) ; 

    arbol.insertar(Point3D(-2,-2,-2)) ; 
    revisarInt("al meter el segundo punto aparecen los 8 hijos" , contarNodos(arbol) , 9) ; 
    revisarInt("la profundidad ahora es 1" , profundidadMaxima(arbol) , 1) ; 
    revisarInt("los 2 puntos siguen en el arbol" , contarPuntos(arbol) , 2) ; 

    revisar("el punto que estaba antes de subdividir sigue estando" , arbol.buscar(Point3D(2,2,2)) , true) ; 
    revisar("el punto que provoco la subdivision tambien esta" , arbol.buscar(Point3D(-2,-2,-2)) , true) ; 

    cout << endl ; 
}

// un punto fuera de los limites de la raiz no se puede insertar
static void pruebaFueraDeLimites(){
    cout << "4. caso borde : punto fuera de los limites" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 2) ; 

    revisar("insertar(10,10,10) devuelve false" , arbol.insertar(Point3D(10,10,10)) , false) ; 
    revisar("insertar(-9,0,0) devuelve false" , arbol.insertar(Point3D(-9,0,0)) , false) ; 
    revisarInt("el arbol quedo vacio" , contarPuntos(arbol) , 0) ; 
    revisar("buscar() el punto de afuera devuelve false" , arbol.buscar(Point3D(10,10,10)) , false) ; 

    // los limites son inclusivos , asi que una esquina exacta si entra
    revisar("insertar en la esquina minima (-4,-4,-4)" , arbol.insertar(Point3D(-4,-4,-4)) , true) ; 
    revisar("insertar en la esquina maxima (4,4,4)" , arbol.insertar(Point3D(4,4,4)) , true) ; 
    revisar("buscar() la esquina minima" , arbol.buscar(Point3D(-4,-4,-4)) , true) ; 
    revisar("buscar() la esquina maxima" , arbol.buscar(Point3D(4,4,4)) , true) ; 

    cout << endl ; 
}

// busqueda de un punto que existe y de uno que no , con el camino recorrido
static void pruebaBusqueda(){
    cout << "5. busqueda exitosa y fallida" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 1) ; 
    arbol.insertar(Point3D(3,3,3)) ; 
    arbol.insertar(Point3D(-3,-3,-3)) ; 
    arbol.insertar(Point3D(3,-3,3)) ; 

    revisar("buscar() un punto insertado" , arbol.buscar(Point3D(-3,-3,-3)) , true) ; 
    revisar("buscar() un punto que nunca se inserto" , arbol.buscar(Point3D(0.5,0.5,0.5)) , false) ; 

    // la version con camino guarda los nodos por los que fue pasando
    vector<Octree::InfoNodo> camino ; 
    bool hallado = arbol.buscar(Point3D(3,3,3) , camino) ; 
    revisar("buscar() con camino encuentra el punto" , hallado , true) ; 
    revisar("el camino tiene al menos la raiz y una hoja" , camino.size() >= 2 , true) ; 
    revisarInt("el camino arranca en la raiz (profundidad 0)" , camino[0].profundidad , 0) ; 
    revisar("el camino termina en una hoja" , camino[camino.size()-1].esHoja , true) ; 

    // el camino tiene que ir bajando un nivel a la vez
    bool baja = true ; 
    for(int i = 1 ; i < (int)camino.size() ; i++){
        if(camino[i].profundidad != camino[i-1].profundidad + 1){
            baja = false ; 
        }
    }
    revisar("el camino baja de nivel en nivel" , baja , true) ; 

    // una busqueda fallida dentro de los limites igual recorre nodos
    vector<Octree::InfoNodo> caminoNo ; 
    revisar("buscar() con camino de un punto inexistente da false" , arbol.buscar(Point3D(0.5,0.5,0.5) , caminoNo) , false) ; 
    revisar("aun asi recorrio algunos nodos" , caminoNo.size() > 0 , true) ; 

    cout << endl ; 
}

// el postorder devuelve primero los hijos y al final el padre
static void pruebaPostorder(){
    cout << "6. recorrido postorder" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 1) ; 
    arbol.insertar(Point3D(2,2,2)) ; 
    arbol.insertar(Point3D(-2,-2,-2)) ; 

    vector<Octree::InfoNodo> orden ; 
    arbol.recorrerPostorder(orden) ; 

    revisarInt("devuelve los 9 nodos del arbol" , (int)orden.size() , 9) ; 
    revisarInt("la raiz queda de ultima" , orden[orden.size()-1].profundidad , 0) ; 
    revisar("el primero que sale es un hijo , no la raiz" , orden[0].profundidad > 0 , true) ; 

    // ningun padre puede salir antes que sus hijos , asi que la raiz es la unica de profundidad 0
    int raices = 0 ; 
    for(int i = 0 ; i < (int)orden.size() ; i++){
        if(orden[i].profundidad==0){
            raices++ ; 
        }
    }
    revisarInt("solo hay un nodo de profundidad 0" , raices , 1) ; 

    // en un arbol vacio el postorder devuelve nada mas la raiz
    Octree vacio(-1,-1,-1 , 1,1,1 , 2) ; 
    vector<Octree::InfoNodo> ordenVacio ; 
    vacio.recorrerPostorder(ordenVacio) ; 
    revisarInt("en un arbol vacio devuelve solo la raiz" , (int)ordenVacio.size() , 1) ; 

    cout << endl ; 
}

// caso borde : puntos muy pegados obligan a subdividir varias veces seguidas
static void pruebaPuntosConcentrados(){
    cout << "7. caso borde : puntos concentrados en una esquina" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 1) ; 

    arbol.insertar(Point3D(-3.90f,-3.90f,-3.90f)) ; 
    int nodosAntes = contarNodos(arbol) ; 
    arbol.insertar(Point3D(-3.95f,-3.95f,-3.95f)) ; 
    int nodosDespues = contarNodos(arbol) ; 

    revisar("una sola insercion encadeno varias subdivisiones" , nodosDespues > nodosAntes + 8 , true) ; 
    revisar("la profundidad paso de 1" , profundidadMaxima(arbol) > 1 , true) ; 
    revisarInt("los 2 puntos siguen guardados" , contarPuntos(arbol) , 2) ; 
    revisar("se encuentra el primer punto" , arbol.buscar(Point3D(-3.90f,-3.90f,-3.90f)) , true) ; 
    revisar("se encuentra el segundo punto" , arbol.buscar(Point3D(-3.95f,-3.95f,-3.95f)) , true) ; 

    cout << endl ; 
}

// caso borde : el mismo punto insertado dos veces
static void pruebaPuntoRepetido(){
    cout << "8. caso borde : punto repetido" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 4) ; 

    revisar("primera insercion de (1,1,1)" , arbol.insertar(Point3D(1,1,1)) , true) ; 
    revisar("segunda insercion del mismo punto" , arbol.insertar(Point3D(1,1,1)) , true) ; 
    revisarInt("quedan las dos copias guardadas" , contarPuntos(arbol) , 2) ; 
    revisar("buscar() lo encuentra igual" , arbol.buscar(Point3D(1,1,1)) , true) ; 

    cout << endl ; 
}

// caso borde : puntos repetidos con la capacidad llena.
// subdividir() nunca los separa porque caen siempre en el mismo octante , asi que
// sin el tope de profundidad esto se iria en recursion infinita
static void pruebaRepetidosCapacidadLlena(){
    cout << "9. caso borde : repetidos con capacidad 1 (tope de profundidad)" << endl ; 

    Octree arbol(-4,-4,-4 , 4,4,4 , 1) ; 

    revisar("insertar(1,1,1) la primera vez" , arbol.insertar(Point3D(1,1,1)) , true) ; 
    revisar("insertar(1,1,1) otra vez , sin desbordar la pila" , arbol.insertar(Point3D(1,1,1)) , true) ; 
    revisar("insertar(1,1,1) una tercera vez" , arbol.insertar(Point3D(1,1,1)) , true) ; 

    revisarInt("los 3 puntos quedaron guardados" , contarPuntos(arbol) , 3) ; 
    revisar("el arbol dejo de subdividirse en el tope" , profundidadMaxima(arbol) <= 12 , true) ; 
    revisar("buscar() sigue encontrando el punto" , arbol.buscar(Point3D(1,1,1)) , true) ; 
    revisar("y sigue sin encontrar uno que no esta" , arbol.buscar(Point3D(-1,-1,-1)) , false) ; 

    cout << endl ; 
}


int main(){

    cout << endl ; 
    cout << "==============================================" << endl ; 
    cout << " Pruebas de la clase Octree" << endl ; 
    cout << "==============================================" << endl << endl ; 

    pruebaOctreeVacio() ; 
    pruebaInsercionSinSubdividir() ; 
    pruebaSubdivision() ; 
    pruebaFueraDeLimites() ; 
    pruebaBusqueda() ; 
    pruebaPostorder() ; 
    pruebaPuntosConcentrados() ; 
    pruebaPuntoRepetido() ; 
    pruebaRepetidosCapacidadLlena() ; 

    cout << "==============================================" << endl ; 
    if(fallidas==0){
        cout << " Todo bien : " << totales << " pruebas pasaron" << endl ; 
    }else{
        cout << " " << fallidas << " de " << totales << " pruebas fallaron" << endl ; 
    }
    cout << "==============================================" << endl << endl ; 

    if(fallidas > 0){
        return 1 ; 
    }
    return 0 ; 
}
