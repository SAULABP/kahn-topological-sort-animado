#include <iostream>
#include <vector>
using namespace std;

int main(){
    int n,m; // n es nodos, m aristas
    cin >> n >> m;

    vector<vector<int>> ady(n); //lista de adyacencia
    vector<int> grado(n, 0);  //grado de entrada de cada nodo

    // lee las aristas
    for(int i=0; i<m ; i++){
        int u,v;
        cin >> u >> v;
        ady[u].push_back(v);
        grado[v]++;
    }

    vector<int> cola;
    int frente = 0; //posicion del proximo nodo a salir, solo movemos frente hacia adelante

    //meter los nodos con grado 0
    for(int i= 0;  i< n; i++){
        if(grado[i] == 0){
            cola.push_back(i);
        }
    }

    //bucle principal
    while(frente < cola.size()){
        int actual = cola[frente];
        frente++;

            //restar los grados vecinos
            for(int vecino : ady[actual]){
                grado[vecino]--;
                if(grado[vecino] == 0){
                    cola.push_back(vecino);
                }
            }
    }

    //detectar ciclo e imprimir el orden
    if(cola.size()<n){
            cout<<"hay ciclo" <<endl;
    } else{
        for(int i = 0; i < n; i++){
            cout << cola[i] << " ";
        }
        cout << endl;
    }


    return 0;
}