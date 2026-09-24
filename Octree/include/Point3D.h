#ifndef POINT3D_H
#define POINT3D_H
struct Point3D{
    float x ; 
    float y ; 
    float z ; 

    Point3D (){ // constructor por defecto
        x = 0.0 ; 
        y = 0.0 ; 
        z = 0.0 ; 
    }

    Point3D( float equis , float ye , float zeta){ // constructor con atributos
        x = equis ; 
        y = ye ; 
        z = zeta ;
    }

    bool operator==(const Point3D& otro) const{  // sobrecargamos esto para poder hacer comparaciones mas adelante
        
        if(x == otro.x && y == otro.y &&  z == otro.z){ // si el actual con el de la izq es igual a el otro entonces true
            return true ; 
        }else{
            return false ;
        }

    }
};



#endif 