#include <iostream>
#include "Octree.h"
using namespace std ; 


// definimos lo de los constrcutores 
Octree::Octree(float mX , float mY,float mZ , float maX , float maY , float maZ , int cap){
    root = new  OctreeNode(mX,mY,mZ,maX ,maY, maZ,cap )  ; 
}
Octree::~Octree(){
    liberar(root) ;  // usamos el liberar que era el extra de los extras xd
}

void Octree::liberar(OctreeNode* nodo ) {
    if(nodo==nullptr ){
        return; 
    }
    for(int i = 0; i <8 ;i++ ) {
        liberar(nodo->hijos[i]); 
    }
    delete nodo ; 
}

// definimos los aux 

// revisa si el punto esta dentro de el limite que se definio por cada cuadrante
bool Octree::contiene(const OctreeNode* nodo ,const  Point3D& p)const {
    if( p.x >= nodo->minX && p.x <=  nodo->maxX &&  p.y >= nodo->minY  &&  p.y<= nodo->maxY &&  p.z>=nodo->minZ  && p.z<= nodo->maxZ ){
        return true; 
    }else{
        return false ; 
    }

}

// obtiene en que cuadrante va el punto segun su posicion relativa al centro
int Octree::obtenerOctante(const  OctreeNode* nodo,const Point3D& p)const{
    float centroX  = (nodo->minX+nodo->maxX)/ 2.0f ; 
    float centroY = (nodo->minY+nodo->maxY)/2.0f; 
    float centroZ = (nodo->minZ +nodo->maxZ)/ 2.0f ; 
    int octante = 0 ; 

    if(p.x >=centroX ){
        octante += 1 ; 
    }
    if(p.y >= centroY ) {
        octante += 2 ; 
    }
    if(p.z >=centroZ ) {
        octante += 4 ; 
    }

    return octante; 


}

// funciones ya de el octree relaciondo a insercion depuntos y busqueda 
bool Octree::insertar(const Point3D& p ) {
    return insertar(root , p) ; 
}

bool Octree::buscar(const Point3D& p)  const{
    return buscar(root , p) ; 
}