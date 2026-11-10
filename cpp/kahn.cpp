#include <iostream>
#include <fstream>
#include <vector>
using namespace std;

// Escribe un vector como lista JSON,  ejemplo [0, 1, 2]
void escribirLista(ofstream& archivo, vector<int>& lista, int desde){
    archivo << "[";
    for (int i = desde; i < lista.size(); i++) {
        archivo << lista[i];
        if (i + 1 < lista.size()) {
            archivo << ", ";
        }
    }
    archivo << "]";
}

int main(){
    int n,m; // n es nodos, m aristas
    cin >> n >> m;

    vector<vector<int>> ady(n); //lista de adyacencia
    vector<int> grado(n, 0);  //grado de entrada de cada nodo

    ofstream traza("data/traza.json");
    traza << "{\n";
    traza << "  \"n\": " << n << ",\n";
    traza << "  \"aristas\": [";

    // lee las aristas
    for(int i=0; i<m ; i++){
        int u,v;
        cin >> u >> v;
        ady[u].push_back(v);
        grado[v]++;

        traza << "[" << u << ", " << v << "]";
        if (i + 1 < m) {
            traza << ", ";
        }
    }

    traza << "],\n";

    traza << "  \"grado_inicial\": ";
    escribirLista(traza, grado, 0);
    traza << ",\n";

    vector<int> cola;
    int frente = 0; //posicion del proximo nodo a salir, solo movemos frente hacia adelante

    //meter los nodos con grado 0
    for(int i= 0;  i< n; i++){
        if(grado[i] == 0){
            cola.push_back(i);
        }
    }

    traza << "  \"cola_inicial\": ";
    escribirLista(traza, cola, 0);
    traza << ",\n";
    traza << "  \"pasos\": [\n";

    bool primerPaso = true;

    //bucle principal
    while(frente < cola.size()){
        int actual = cola[frente];
        frente++;

        if (!primerPaso) {
            traza << ",\n";
        }
        primerPaso = false;
        traza << "    {\"sale\": " << actual << ", \"cambios\": [";

        bool primerCambio = true;

        //restar los grados vecinos
        for(int vecino : ady[actual]){
            grado[vecino]--;
            if(grado[vecino] == 0){
                cola.push_back(vecino);
            }

            if (!primerCambio) {
                traza << ", ";
            }
            primerCambio = false;
            traza << "{\"nodo\": " << vecino
                  << ", \"grado\": " << grado[vecino]
                  << ", \"entra\": " << (grado[vecino] == 0 ? "true" : "false") << "}";
        }

        traza << "], \"cola\": ";
        escribirLista(traza, cola, frente);
        traza << "}";
    }

    traza << "\n  ],\n";

    //detectar ciclo e imprimir el orden
    if (cola.size() < n) {
        cout << "hay ciclo" << endl;
        traza << "  \"hay_ciclo\": true,\n";
    } else {
        for (int i = 0; i < n; i++) {
            cout << cola[i] << " ";
        }
        cout << endl;
        traza << "  \"hay_ciclo\": false,\n";
    }

    traza << "  \"orden\": ";
    escribirLista(traza, cola, 0);
    traza << "\n}\n";
    traza.close();

    return 0;
}
