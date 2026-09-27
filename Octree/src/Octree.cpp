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
    // calculamos los centors 
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

// divide todo el cuadrante en sus 8 parte o bueno el nodo en sus 8 hijos 
void Octree::subdividir( OctreeNode*  nodo){
    float centroX  = (nodo->minX+nodo->maxX)/ 2.0f ; 
    float centroY = (nodo->minY+nodo->maxY)/2.0f; 
    float centroZ = (nodo->minZ +nodo->maxZ)/ 2.0f ; 

    // creamos manualmente a los hijos

    nodo->hijos[0] = new OctreeNode(nodo->minX, nodo->minY , nodo->minZ,centroX ,centroY, centroZ, nodo->capacidad ) ;
    nodo->hijos[1] = new OctreeNode(centroX, nodo->minY, nodo->minZ , nodo->maxX,centroY, centroZ , nodo->capacidad );
    nodo->hijos[2] = new OctreeNode(nodo->minX ,centroY, nodo->minZ,centroX, nodo->maxY ,centroZ, nodo->capacidad) ;
    nodo->hijos[3] = new OctreeNode(centroX, centroY ,nodo->minZ,nodo->maxX,nodo->maxY, centroZ ,nodo->capacidad );
    nodo->hijos[4] = new OctreeNode(nodo->minX,nodo->minY,centroZ,centroX , centroY,nodo->maxZ,nodo->capacidad);
    nodo->hijos[5] = new OctreeNode(centroX , nodo->minY, centroZ, nodo->maxX,centroY ,nodo->maxZ, nodo->capacidad ) ;
    nodo->hijos[6] = new OctreeNode(nodo->minX, centroY,centroZ ,centroX, nodo->maxY,nodo->maxZ , nodo->capacidad ) ;
    nodo->hijos[7] = new OctreeNode(centroX,centroY,centroZ, nodo->maxX , nodo->maxY,nodo->maxZ, nodo->capacidad );

    // redistribuimos los puntos que ya tenia el nodo padre en los hijos
    for(int i = 0 ;i <(int)nodo->puntos.size() ;i++){ // casteamos el  nodo->puntos.size() para que nos de int  sin warnigs
        int oct=obtenerOctante(nodo, nodo->puntos[i] ); 
        nodo->hijos[oct]->puntos.push_back(nodo->puntos[i]); 
    }
    nodo->puntos.clear() ; // borrarmo el vectos para no  tener el punto tanto en el padre como en los hijos 
}

// insercion recursiva en el nodo cuadrante
bool Octree::insertar(OctreeNode*  nodo,const Point3D& p , int profundidad) {
    if(!contiene(nodo,p)) {  
        return false; 
    }

    if(nodo->hijos[0]==nullptr ){
        // si todavia cabe , o si ya llegamos al tope de subdivisiones , se guarda aca.
        // el tope importa porque puntos repetidos siempre caen en el mismo octante y
        // subdividir no los separaria nunca
        if( (int)nodo->puntos.size()< nodo->capacidad || profundidad >= PROFUNDIDAD_MAXIMA ){
            nodo->puntos.push_back(p); 
            return true;

        }else {
            subdividir(nodo) ; 

        }

    }

    int oct = obtenerOctante(nodo, p); 
    return insertar(nodo->hijos[oct],p,profundidad+1) ; 

}

// busqueda recursiva en el nodo cuadrante
bool Octree::buscar( const  OctreeNode* nodo,const Point3D& p , vector<InfoNodo>* camino , int profundidad ) const{
    if( !contiene(nodo,p) ){  // si nos da false es porque no debe estar en el cuadrante entonces salimos
        return false; 
    }

    if(camino!=nullptr){ // solo si nos pidieron el camino lo vamos guardando
        camino->push_back(infoDe(nodo,profundidad)); 
    }

    //si es hoja revisamos los puntos guardados
    if( nodo->hijos[0]==nullptr ){
        for(int i =0; i< (int)nodo->puntos.size(); i++) {
            if(nodo->puntos[i]==p){
                return true; 
            }

        }

        return false ; 

    }
    // y seguimos buscando al hijo que corresponde
    int oct = obtenerOctante(nodo,p); 
    return buscar( nodo->hijos[oct],p,camino,profundidad+1); 


}


// libera recursivamente toda la memoria de los nodos
void Octree::liberar(OctreeNode* nodo ) {
    if(nodo==nullptr ){
        return; 
    }
    for(int i = 0; i <8 ;i++ ) {
        liberar(nodo->hijos[i]); 
    }
    delete nodo ; 
}

// funciones ya de el octree relaciondo a insercion depuntos y busqueda 
bool Octree::insertar(const Point3D& p ) {
    return insertar(root , p , 0) ; 
}

bool Octree::buscar(const Point3D& p)  const{
    return buscar(root , p , nullptr , 0) ; 
}

// la misma busqueda pero devolviendo los nodos por los que paso
bool Octree::buscar(const Point3D& p , vector<InfoNodo>& camino)  const{
    return buscar(root , p , &camino , 0) ; 
}


// funciones de solo lectura para poder dibujar el arbol por fuera

// copia los limites y los puntos de un nodo a la struct de solo lectura
Octree::InfoNodo Octree::infoDe(const OctreeNode* nodo , int profundidad) const{
    InfoNodo info ; 
    info.minX = nodo->minX ; 
    info.minY = nodo->minY ; 
    info.minZ = nodo->minZ ; 
    info.maxX = nodo->maxX ; 
    info.maxY = nodo->maxY ; 
    info.maxZ = nodo->maxZ ; 
    info.puntos = nodo->puntos ; 
    info.esHoja = (nodo->hijos[0]==nullptr) ; // si no tiene hijos es hoja
    info.profundidad = profundidad ; 
    return info ; 
}

// recorrido postorder , primero los 8 hijos y al final el padre (igual que liberar)
void Octree::recorrerPostorder(const OctreeNode* nodo , int profundidad , vector<InfoNodo>& salida) const{
    if(nodo==nullptr ){
        return; 
    }
    for(int i = 0; i <8 ;i++ ) {
        recorrerPostorder(nodo->hijos[i] , profundidad+1 , salida); 
    }
    salida.push_back(infoDe(nodo,profundidad)); 
}

void Octree::recorrerPostorder(vector<InfoNodo>& salida) const{
    recorrerPostorder(root , 0 , salida) ; 
}