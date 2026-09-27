#ifndef OCTREE_H
#define OCTREE_H
#include "Point3D.h"
#include <vector>
using namespace std ; 


class Octree{
public:
    // info de solo lectura de un nodo , es lo que usa la parte grafica para dibujar
    struct InfoNodo {
        float  minX,minY,minZ ;
        float  maxX,maxY,maxZ ;
        vector<Point3D> puntos ;
        bool esHoja ;
        int profundidad ;
    };

private:
    struct OctreeNode { //Osea es la representacion de la caja o cuadrante 
        //  estas cordenadas son basicamnte la corrdenada de los limites de el cuadrante
        float  minX,minY,minZ ;
        float  maxX,maxY,maxZ ;  
        // Definimos el vector de tipo Point3D para guardar los puntos en el cuadrante 
        vector<Point3D> puntos ;
        // Esta variable define la capacidad para poder dividirse en 8 
        int capacidad ; 
        // Este arreglo contiene los 8 hijos de el cuadrante padre 
        OctreeNode* hijos[8] ; 


        OctreeNode(float mX , float mY,float mZ , float maX , float maY , float maZ , int cap ){ // constructor 
            minX = mX;
            minY = mY ; 
            minZ = mZ ; 
            maxX = maX  ; 
            maxY = maY ; 
            maxZ = maZ ; 
            capacidad = cap ; 

            for (int i = 0 ;  i< 8 ; i++){
                hijos[i]  = nullptr ; 
            }
        }
    };

    OctreeNode* root ;  

    // tope de subdivisiones . sin esto , dos puntos identicos (o casi) con capacidad
    // llena harian que insertar() se subdividiera para siempre y reventara la pila
    static const int PROFUNDIDAD_MAXIMA = 12 ;

    //  Funciones auxiliares

    // revisa si el punto esta dentro de un cuadrante  en especifico 
    bool contiene(const OctreeNode* nodo ,const  Point3D& p  )const;

    // obtiene  en que cuadrando se va a ir el punto 
    int obtenerOctante(const  OctreeNode* nodo,const Point3D& p)const;

    //divide en 8  el cuadrante
    void subdividir( OctreeNode*  nodo);

    // insercion rescursiva el nodo cuadrante
    bool insertar(OctreeNode*  nodo,const Point3D& p , int profundidad) ;

    // busqueda revursiva de el nodo cuadrante , el camino es opcional
    bool buscar( const  OctreeNode* nodo,const Point3D& p , vector<InfoNodo>* camino , int profundidad ) const;

    // copia los limites y los puntos de un nodo a la struct de solo lectura
    InfoNodo infoDe(const OctreeNode* nodo , int profundidad) const;

    // recorrido postorder recursivo que va llenando la salida
    void recorrerPostorder(const OctreeNode* nodo , int profundidad , vector<InfoNodo>& salida) const;

    // extr de los extras para liberar la memoria de los nodos cuadrantes
    void liberar(OctreeNode* nodo ) ;

public:

    Octree(float mX , float mY,float mZ , float maX , float maY , float maZ , int cap) ; 
    ~Octree();   

    // para insertar un punto 
    bool insertar(const Point3D& p ) ;
    //buscamos punto 
    bool buscar(const Point3D& p)  const;

    // la misma busqueda pero guardando los nodos por los que va pasando
    bool buscar(const Point3D& p , vector<InfoNodo>& camino)  const;

    // recorrido postorder de solo lectura , el mismo orden que usa liberar
    void recorrerPostorder(vector<InfoNodo>& salida) const;


};






#endif 
