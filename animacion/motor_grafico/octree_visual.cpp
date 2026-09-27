#include <cmath>
#include <cstdio>
#include <map>
#include <string>
#include <vector>
#include "raylib.h"
#include "Octree.h"

using namespace std ; 

// Mini app de visualizacion del Octree.
// Aca NO hay logica de octree , todo lo que se dibuja sale de la clase Octree real:
// insertar() , buscar() y recorrerPostorder() . raylib solo pinta lo que el arbol reporta.


// una escena es un caso que queremos mostrar con el octree real
struct Escena {
    string nombre ; 
    string detalle ; 
    float rango ; 
    int capacidad ; 
    vector<Point3D> puntos ; 
    Point3D buscaSi ;  // punto que si vamos a insertar
    Point3D buscaNo ;  // punto que nunca insertamos
};


// pasamos un Point3D a lo que entiende raylib
static Vector3 aVec(const Point3D& p){
    return Vector3{ p.x , p.y , p.z } ; 
}

// el centro de la caja del nodo , con sus limites reales
static Vector3 centroDe(const Octree::InfoNodo& n){
    return Vector3{ (n.minX+n.maxX)/2.0f , (n.minY+n.maxY)/2.0f , (n.minZ+n.maxZ)/2.0f } ; 
}

// el tamano de la caja del nodo
static Vector3 tamanoDe(const Octree::InfoNodo& n){
    return Vector3{ n.maxX-n.minX , n.maxY-n.minY , n.maxZ-n.minZ } ; 
}

// los limites identifican de forma unica a un nodo , nos sirve de llave
static string claveDe(const Octree::InfoNodo& n){
    char buf[160] ; 
    snprintf(buf , sizeof(buf) , "%.4f %.4f %.4f %.4f %.4f %.4f" ,
             n.minX , n.minY , n.minZ , n.maxX , n.maxY , n.maxZ ) ; 
    return string(buf) ; 
}


// armamos los casos , el 1 y el 3 son los casos borde
static vector<Escena> armarEscenas(){
    vector<Escena> escenas ; 

    Escena e1 ; 
    e1.nombre = "1. Caso borde: octree vacio y un solo punto" ; 
    e1.detalle = "arranca sin puntos , se inserta uno y el nodo raiz no llega a subdividirse" ; 
    e1.rango = 3.0f ; 
    e1.capacidad = 1 ; 
    e1.puntos.push_back(Point3D( 1.0f , 1.0f , 1.0f )) ; 
    e1.buscaSi = Point3D( 1.0f , 1.0f , 1.0f ) ; 
    e1.buscaNo = Point3D( -2.0f , 0.5f , -1.0f ) ; 
    escenas.push_back(e1) ; 

    Escena e2 ; 
    e2.nombre = "2. Insercion con subdivision (capacidad = 1)" ; 
    e2.detalle = "cada vez que una hoja se pasa de capacidad , subdividir() crea los 8 hijos" ; 
    e2.rango = 3.0f ; 
    e2.capacidad = 1 ; 
    e2.puntos.push_back(Point3D(  1.5f ,  1.5f ,  1.5f )) ; 
    e2.puntos.push_back(Point3D( -1.5f , -1.5f , -1.5f )) ; 
    e2.puntos.push_back(Point3D(  1.5f , -1.5f ,  1.5f )) ; 
    e2.puntos.push_back(Point3D( -1.0f ,  2.0f , -2.0f )) ; 
    e2.puntos.push_back(Point3D(  2.5f ,  0.5f , -1.0f )) ; 
    e2.puntos.push_back(Point3D(  0.5f ,  2.0f ,  2.0f )) ; 
    e2.puntos.push_back(Point3D(  8.0f ,  8.0f ,  8.0f )) ; // este queda fuera de la raiz a proposito
    e2.buscaSi = Point3D(  2.5f ,  0.5f , -1.0f ) ; 
    e2.buscaNo = Point3D(  0.0f ,  0.0f ,  0.0f ) ; 
    escenas.push_back(e2) ; 

    Escena e3 ; 
    e3.nombre = "3. Caso borde: puntos concentrados" ; 
    e3.detalle = "puntos muy pegados , una sola insercion provoca varias subdivisiones seguidas" ; 
    e3.rango = 3.0f ; 
    e3.capacidad = 1 ; 
    e3.puntos.push_back(Point3D( -2.0f , -2.0f , -2.0f )) ; 
    e3.puntos.push_back(Point3D( -2.5f , -2.5f , -2.5f )) ; 
    e3.puntos.push_back(Point3D( -2.8f , -2.8f , -2.8f )) ; 
    e3.puntos.push_back(Point3D( -2.9f , -2.9f , -2.9f )) ; 
    e3.buscaSi = Point3D( -2.8f , -2.8f , -2.8f ) ; 
    e3.buscaNo = Point3D( -2.7f , -2.7f , -2.7f ) ; 
    escenas.push_back(e3) ; 

    return escenas ; 
}


int main(){

    const int ANCHO = 1280 ; 
    const int ALTO = 720 ; 

    SetConfigFlags(FLAG_MSAA_4X_HINT | FLAG_WINDOW_RESIZABLE) ; 
    InitWindow(ANCHO , ALTO , "Octree - visualizacion con la clase real (C++ / raylib)") ; 
    SetTargetFPS(60) ; 

    vector<Escena> escenas = armarEscenas() ; 
    int escenaActual = 0 ; 

    // el arbol real , es el unico que guarda la estructura
    Octree* arbol = nullptr ; 

    vector<Octree::InfoNodo> nodos ;    
    map<string,float> aparicion ;       
    int paso = 0 ;                      
    string mensaje = "" ; 

    int modo = 0 ;                      
    vector<Octree::InfoNodo> camino ;   
    vector<Octree::InfoNodo> orden ;   
    map<string,int> posOrden ;         
    bool encontrado = false ; 
    Point3D objetivo ; 
    int visitados = 0 ; 
    float relojPaso = 0.0f ; 

    Point3D ultimoPunto ; 
    float tiempoUltimo = -10.0f ; 

    bool automatico = false ; 
    float relojAuto = 0.0f ; 

    // le volvemos a pedir al arbol real su estado completo
    auto refrescar = [&](){
        nodos.clear() ; 
        arbol->recorrerPostorder(nodos) ; 
        float ahora = (float)GetTime() ; 
        for(int i = 0 ; i < (int)nodos.size() ; i++){
            string k = claveDe(nodos[i]) ; 
            if(aparicion.find(k)==aparicion.end()){ // nodo nuevo , lo animamos al crecer
                aparicion[k] = ahora ; 
            }
        }
    } ; 

    // borramos el arbol y creamos uno nuevo con los limites de la escena
    auto reiniciar = [&](int idx){
        escenaActual = idx ; 
        float r = escenas[idx].rango ; 
        if(arbol!=nullptr){
            delete arbol ; 
        }
        arbol = new Octree(-r,-r,-r , r,r,r , escenas[idx].capacidad) ; 
        paso = 0 ; 
        modo = 0 ; 
        aparicion.clear() ; 
        camino.clear() ; 
        orden.clear() ; 
        posOrden.clear() ; 
        visitados = 0 ; 
        tiempoUltimo = -10.0f ; 
        automatico = false ; 
        mensaje = "octree vacio , solo existe el nodo raiz" ; 
        refrescar() ; 
    } ; 

    // le pedimos al octree real que inserte el siguiente punto de la escena
    auto insertarSiguiente = [&](){
        Escena& e = escenas[escenaActual] ; 
        if(paso >= (int)e.puntos.size()){
            mensaje = "ya no quedan puntos en esta escena , R para reiniciar" ; 
            automatico = false ; 
            return ; 
        }
        Point3D p = e.puntos[paso] ; 
        int antes = (int)nodos.size() ; 
        bool ok = arbol->insertar(p) ;   // <- la insercion real
        paso++ ; 
        refrescar() ; 
        int nuevos = (int)nodos.size() - antes ; 
        ultimoPunto = p ; 
        tiempoUltimo = (float)GetTime() ; 
        char buf[220] ; 
        if(!ok){
            snprintf(buf , sizeof(buf) , "insertar(%.1f, %.1f, %.1f) = false , el punto cae fuera de la raiz" , p.x,p.y,p.z) ; 
        }else if(nuevos > 0){
            snprintf(buf , sizeof(buf) , "insertar(%.1f, %.1f, %.1f) = true , se subdividio y aparecieron %d nodos" , p.x,p.y,p.z,nuevos) ; 
        }else{
            snprintf(buf , sizeof(buf) , "insertar(%.1f, %.1f, %.1f) = true , entro en una hoja sin subdividir" , p.x,p.y,p.z) ; 
        }
        mensaje = buf ; 
        modo = 0 ; 
    } ; 

    // busqueda usando el buscar() real que ademas nos devuelve el camino
    auto lanzarBusqueda = [&](const Point3D& p){
        camino.clear() ; 
        objetivo = p ; 
        encontrado = arbol->buscar(p , camino) ;   // <- la busqueda real
        modo = 1 ; 
        visitados = 0 ; 
        relojPaso = 0.0f ; 
        char buf[220] ; 
        snprintf(buf , sizeof(buf) , "buscar(%.1f, %.1f, %.1f) = %s , recorrio %d nodos" ,
                 p.x,p.y,p.z , encontrado ? "true" : "false" , (int)camino.size()) ; 
        mensaje = buf ; 
    } ; 

    // recorrido postorder real , el mismo orden en que liberar() borra los nodos
    auto lanzarPostorder = [&](){
        orden.clear() ; 
        posOrden.clear() ; 
        arbol->recorrerPostorder(orden) ;   // <- el recorrido real
        for(int i = 0 ; i < (int)orden.size() ; i++){
            posOrden[claveDe(orden[i])] = i ; 
        }
        modo = 2 ; 
        visitados = 0 ; 
        relojPaso = 0.0f ; 
        char buf[220] ; 
        snprintf(buf , sizeof(buf) , "recorrerPostorder() devolvio %d nodos , primero los hijos y al final la raiz" , (int)orden.size()) ; 
        mensaje = buf ; 
    } ; 

    reiniciar(0) ; 

    // camara en coordenadas esfericas , el mouse la mueve alrededor del origen
    float angH = 0.8f ; 
    float angV = 0.55f ; 
    float dist = 16.0f ; 

    Camera3D cam ; 
    cam.position = Vector3{ 0.0f , 0.0f , 1.0f } ; 
    cam.target = Vector3{ 0.0f , 0.0f , 0.0f } ; 
    cam.up = Vector3{ 0.0f , 1.0f , 0.0f } ; 
    cam.fovy = 45.0f ; 
    cam.projection = CAMERA_PERSPECTIVE ; 

    while(!WindowShouldClose()){

        float dt = GetFrameTime() ; 

        // controles de camara
        if(IsMouseButtonDown(MOUSE_BUTTON_LEFT)){
            Vector2 d = GetMouseDelta() ; 
            angH -= d.x * 0.005f ; 
            angV += d.y * 0.005f ; 
            if(angV > 1.5f){ angV = 1.5f ; }
            if(angV < -1.5f){ angV = -1.5f ; }
        }
        dist -= GetMouseWheelMove() * 1.2f ; 
        if(dist < 5.0f){ dist = 5.0f ; }
        if(dist > 45.0f){ dist = 45.0f ; }

        cam.position.x = dist * cosf(angV) * sinf(angH) ; 
        cam.position.y = dist * sinf(angV) ; 
        cam.position.z = dist * cosf(angV) * cosf(angH) ; 

        // controles de las operaciones
        if(IsKeyPressed(KEY_ONE)){ reiniciar(0) ; }
        if(IsKeyPressed(KEY_TWO)){ reiniciar(1) ; }
        if(IsKeyPressed(KEY_THREE)){ reiniciar(2) ; }
        if(IsKeyPressed(KEY_R)){ reiniciar(escenaActual) ; }
        if(IsKeyPressed(KEY_SPACE)){ insertarSiguiente() ; }
        if(IsKeyPressed(KEY_A)){ automatico = !automatico ; relojAuto = 0.0f ; }
        if(IsKeyPressed(KEY_B)){ lanzarBusqueda(escenas[escenaActual].buscaSi) ; }
        if(IsKeyPressed(KEY_N)){ lanzarBusqueda(escenas[escenaActual].buscaNo) ; }
        if(IsKeyPressed(KEY_T)){ lanzarPostorder() ; }

        if(automatico){
            relojAuto += dt ; 
            if(relojAuto > 0.8f){
                relojAuto = 0.0f ; 
                insertarSiguiente() ; 
            }
        }

        // avanzamos poco a poco el camino de busqueda o el postorder
        if(modo==1 && visitados < (int)camino.size()){
            relojPaso += dt ; 
            if(relojPaso > 0.45f){ relojPaso = 0.0f ; visitados++ ; }
        }
        if(modo==2 && visitados < (int)orden.size()){
            relojPaso += dt ; 
            if(relojPaso > 0.12f){ relojPaso = 0.0f ; visitados++ ; }
        }

        // datos que mostramos en pantalla , todos salen de la foto del arbol real
        int totalPuntos = 0 ; 
        int hojas = 0 ; 
        int profMax = 0 ; 
        for(int i = 0 ; i < (int)nodos.size() ; i++){
            totalPuntos += (int)nodos[i].puntos.size() ; 
            if(nodos[i].esHoja){ hojas++ ; }
            if(nodos[i].profundidad > profMax){ profMax = nodos[i].profundidad ; }
        }

        BeginDrawing() ; 
        ClearBackground(Color{ 16 , 17 , 23 , 255 }) ; 

        BeginMode3D(cam) ; 

        DrawGrid(20 , 1.0f) ; 

        // una caja por cada nodo real , con sus limites reales
        for(int i = 0 ; i < (int)nodos.size() ; i++){
            Octree::InfoNodo& n = nodos[i] ; 
            string k = claveDe(n) ; 

            // en el postorder los nodos ya visitados desaparecen , igual que en liberar
            if(modo==2){
                map<string,int>::iterator it = posOrden.find(k) ; 
                if(it!=posOrden.end() && it->second < visitados){
                    continue ; 
                }
            }

            // animacion de aparicion del nodo
            float f = ((float)GetTime() - aparicion[k]) / 0.35f ; 
            if(f > 1.0f){ f = 1.0f ; }
            if(f < 0.15f){ f = 0.15f ; }

            Color color ; 
            if(n.profundidad==0){
                color = Color{ 120 , 170 , 255 , 255 } ; 
            }else if(n.esHoja){
                color = Color{ 70 , 200 , 190 , 170 } ; 
            }else{
                color = Color{ 60 , 90 , 140 , 110 } ; 
            }

            // resaltamos el camino que devolvio buscar()
            if(modo==1){
                for(int j = 0 ; j < visitados && j < (int)camino.size() ; j++){
                    if(claveDe(camino[j])==k){
                        color = encontrado ? Color{ 255 , 170 , 40 , 255 } : Color{ 240 , 80 , 80 , 255 } ; 
                    }
                }
            }
            // y el nodo que toca en el postorder
            if(modo==2 && visitados < (int)orden.size() && claveDe(orden[visitados])==k){
                color = Color{ 200 , 120 , 255 , 255 } ; 
            }

            Vector3 t = tamanoDe(n) ; 
            t.x *= f ; t.y *= f ; t.z *= f ; 
            DrawCubeWiresV(centroDe(n) , t , color) ; 
        }

        // los puntos tambien salen de los nodos reales , no de una lista aparte
        for(int i = 0 ; i < (int)nodos.size() ; i++){
            if(modo==2){
                map<string,int>::iterator it = posOrden.find(claveDe(nodos[i])) ; 
                if(it!=posOrden.end() && it->second < visitados){
                    continue ; 
                }
            }
            for(int j = 0 ; j < (int)nodos[i].puntos.size() ; j++){
                Point3D p = nodos[i].puntos[j] ; 
                bool reciente = ((float)GetTime() - tiempoUltimo < 0.8f) && (p==ultimoPunto) ; 
                DrawSphere(aVec(p) , reciente ? 0.14f : 0.09f ,
                           reciente ? Color{ 255 , 230 , 90 , 255 } : Color{ 245 , 200 , 60 , 255 }) ; 
            }
        }

        // el punto que estamos buscando lo marcamos aparte
        if(modo==1){
            DrawSphereWires(aVec(objetivo) , 0.26f , 6 , 6 ,
                            encontrado ? Color{ 120 , 255 , 140 , 255 } : Color{ 255 , 90 , 90 , 255 }) ; 
        }

        EndMode3D() ; 

        // interfaz
        Escena& e = escenas[escenaActual] ; 

        DrawRectangle(0 , 0 , GetScreenWidth() , 92 , Color{ 10 , 11 , 16 , 220 }) ; 
        DrawText("OCTREE - todo lo dibujado sale de la clase Octree en C++" , 18 , 12 , 20 , Color{ 235 , 235 , 245 , 255 }) ; 
        DrawText(e.nombre.c_str() , 18 , 40 , 18 , Color{ 120 , 200 , 255 , 255 }) ; 
        DrawText(e.detalle.c_str() , 18 , 64 , 15 , Color{ 150 , 155 , 170 , 255 }) ; 

        int y = 106 ; 
        DrawText(TextFormat("capacidad por nodo: %d" , e.capacidad) , 18 , y , 16 , Color{ 200 , 205 , 215 , 255 }) ; y += 22 ; 
        DrawText(TextFormat("insertar() llamado: %d de %d" , paso , (int)e.puntos.size()) , 18 , y , 16 , Color{ 200 , 205 , 215 , 255 }) ; y += 22 ; 
        DrawText(TextFormat("nodos reales: %d   (hojas: %d)" , (int)nodos.size() , hojas) , 18 , y , 16 , Color{ 200 , 205 , 215 , 255 }) ; y += 22 ; 
        DrawText(TextFormat("puntos guardados: %d   profundidad: %d" , totalPuntos , profMax) , 18 , y , 16 , Color{ 200 , 205 , 215 , 255 }) ; y += 22 ; 

        if(nodos.size() > 0){
            Octree::InfoNodo& raiz = nodos[nodos.size()-1] ; // en postorder la raiz queda al final
            DrawText(TextFormat("raiz: min(%.2f, %.2f, %.2f)  max(%.2f, %.2f, %.2f)" ,
                                raiz.minX , raiz.minY , raiz.minZ , raiz.maxX , raiz.maxY , raiz.maxZ) ,
                     18 , y , 15 , Color{ 140 , 145 , 160 , 255 }) ; 
            y += 20 ; 
        }

        // mostramos los limites del nodo que se esta resaltando
        if(modo==1 && visitados > 0 && visitados <= (int)camino.size()){
            Octree::InfoNodo& n = camino[visitados-1] ; 
            DrawText(TextFormat("nodo del camino (prof %d): min(%.2f, %.2f, %.2f)  max(%.2f, %.2f, %.2f)" ,
                                n.profundidad , n.minX , n.minY , n.minZ , n.maxX , n.maxY , n.maxZ) ,
                     18 , y , 15 , Color{ 255 , 190 , 90 , 255 }) ; 
            y += 20 ; 
        }
        if(modo==2 && visitados < (int)orden.size()){
            Octree::InfoNodo& n = orden[visitados] ; 
            DrawText(TextFormat("postorder %d/%d (prof %d): min(%.2f, %.2f, %.2f)  max(%.2f, %.2f, %.2f)" ,
                                visitados+1 , (int)orden.size() , n.profundidad ,
                                n.minX , n.minY , n.minZ , n.maxX , n.maxY , n.maxZ) ,
                     18 , y , 15 , Color{ 210 , 150 , 255 , 255 }) ; 
            y += 20 ; 
        }

        if(totalPuntos==0 && paso==0){
            DrawText("estado: octree vacio" , 18 , y , 16 , Color{ 255 , 200 , 120 , 255 }) ; 
            y += 22 ; 
        }

        DrawText(mensaje.c_str() , 18 , GetScreenHeight()-58 , 17 , Color{ 235 , 235 , 245 , 255 }) ; 
        DrawText("[1|2|3] escena   [ESPACIO] insertar   [A] automatico   [B] buscar existente   [N] buscar inexistente   [T] postorder   [R] reiniciar   [mouse] girar/zoom" ,
                 18 , GetScreenHeight()-30 , 15 , Color{ 140 , 145 , 160 , 255 }) ; 

        DrawFPS(GetScreenWidth()-95 , 12) ; 

        EndDrawing() ; 
    }

    delete arbol ; 
    CloseWindow() ; 
    return 0 ; 
}
