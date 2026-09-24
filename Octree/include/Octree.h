#ifndef OCTREE_H
#define OCTREE_H
#include "Point3D.h"
#include <vector>
using namespace std ; 


class Octree{
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

    //  Funciones auxiliares

    // revisa si el punto esta dentro de un cuadrante  en especifico 
    bool contiene(const OctreeNode* nodo ,const  Point3D& p  )const;

    // obtiene  en que cuadrando se va a ir el punto 
    int obtenerOctante(const  OctreeNode* nodo,const Point3D& p)const;

    //divide en 8  el cuadrante
    void subdividir( OctreeNode*  nodo);

    // insercion rescursiva el nodo cuadrante
    bool insertar(OctreeNode*  nodo,const Point3D& p) ;

    // busqueda revursiva de el nodo cuadrante 
    bool buscar( const  OctreeNode* nodo,const Point3D& p ) const;

    // extr de los extras para liberar la memoria de los nodos cuadrantes
    void liberar(OctreeNode* nodo ) ;

public:

    Octree(float mX , float mY,float mZ , float maX , float maY , float maZ , int cap) ; 
    ~Octree();   

    // para insertar un punto 
    bool insertar(const Point3D& p ) ;
    //buscamos punto 
    bool buscar(const Point3D& p)  const;


};






#endif 
