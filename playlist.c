
#include <stdio.h>
#include <stdlib.h>

#define N_CANCIONES 20
#define N_GENEROS 7

enum { CORRIDO, URBANO, REGGAETON, ROCK, METAL, SALSA, POP };
const char *NOMBRE_GENERO[N_GENEROS] = {
    "CORRIDO", "URBANO", "REGGAETON", "ROCK", "METAL", "SALSA", "POP"
};

typedef unsigned int Conjunto;
#define GENERO(g) (1u << (g))

typedef struct {
    char titulo[60];
    char artista[60];
    int genero;
    int duracion;
    int streams;
} Cancion;

typedef struct Nodo {
    Cancion cancion;
    struct Nodo *anterior;
    struct Nodo *siguiente;
} Nodo;

typedef struct {
    Nodo *primero;
    Nodo *ultimo;
    Nodo *actual;
    int cantidad;
} Playlist;

Cancion catalogo[N_CANCIONES] = {
    {"PIENSALO", "Junior H", CORRIDO, 180, 300},
    {"Gil", "Milo J", URBANO, 195, 150},
    {"Nino", "Milo J", URBANO, 200, 140},
    {"Morocha", "Milo J", URBANO, 185, 120},
    {"Andromeda", "Wos", URBANO, 175, 60},
    {"Contando Ovejas", "Wos", URBANO, 210, 50},
    {"TIERRA ZANTA", "Trueno", URBANO, 215, 90},
    {"Mi vecinita", "Plan B", REGGAETON, 230, 100},
    {"Hasta Jesus tuvo un mal dia", "Ca7riel y Paco Amoroso", ROCK, 240, 70},
    {"Bat Country", "Avenged Sevenfold", METAL, 313, 400},
    {"Oh, Que Sera?", "Hector Lavoe", SALSA, 330, 80},
    {"Neon", "John Mayer", POP, 260, 350},
    {"Okupa", "Wos", URBANO, 190, 80},
    {"Bzrp Music Sessions Vol. 52", "Bizarrap y Quevedo", URBANO, 198, 1500},
    {"Gasolina", "Daddy Yankee", REGGAETON, 192, 900},
    {"De musica ligera", "Soda Stereo", ROCK, 212, 600},
    {"Enter Sandman", "Metallica", METAL, 331, 2000},
    {"La vida es un carnaval", "Celia Cruz", SALSA, 277, 700},
    {"Ella Baila Sola", "Eslabon Armado y Peso Pluma", CORRIDO, 164, 1800},
    {"Flowers", "Miley Cyrus", POP, 200, 2300}
};

Conjunto unionConjuntos(Conjunto a, Conjunto b) { return a | b; }
Conjunto interseccion(Conjunto a, Conjunto b) { return a & b; }
Conjunto diferencia(Conjunto a, Conjunto b) { return a & ~b; }

void imprimirConjunto(const char *nombre, Conjunto conjunto)
{
    int i, primero = 1;
    printf("%s = {", nombre);
    for (i = 0; i < N_GENEROS; i++) {
        if (conjunto & GENERO(i)) {
            printf("%s%s", primero ? "" : ", ", NOMBRE_GENERO[i]);
            primero = 0;
        }
    }
    if (primero) printf("vacio");
    printf("}\n");
}

void inicializarPlaylist(Playlist *p)
{
    p->primero = p->ultimo = p->actual = NULL;
    p->cantidad = 0;
}

Nodo *crearNodo(Cancion cancion)
{
    Nodo *nuevo = malloc(sizeof(Nodo));
    if (nuevo == NULL) {
        fprintf(stderr, "No hay memoria suficiente.\n");
        exit(EXIT_FAILURE);
    }
    nuevo->cancion = cancion;
    nuevo->anterior = NULL;
    nuevo->siguiente = NULL;
    return nuevo;
}

/* Agrega al final en tiempo constante O(1). */
void agregarFinal(Playlist *p, Cancion cancion)
{
    Nodo *nuevo = crearNodo(cancion);
    if (p->primero == NULL) {
        p->primero = p->ultimo = p->actual = nuevo;
    } else {
        nuevo->anterior = p->ultimo;
        p->ultimo->siguiente = nuevo;
        p->ultimo = nuevo;
    }
    p->cantidad++;
}

void liberarPlaylist(Playlist *p)
{
    Nodo *aux = p->primero;
    while (aux != NULL) {
        Nodo *siguiente = aux->siguiente;
        free(aux);
        aux = siguiente;
    }
    inicializarPlaylist(p);
}

/* Ordena de mayor a menor streams intercambiando canciones, no nodos. */
void ordenarPorStreams(Playlist *p)
{
    Nodo *i, *j;
    for (i = p->primero; i != NULL; i = i->siguiente) {
        for (j = i->siguiente; j != NULL; j = j->siguiente) {
            if (i->cancion.streams < j->cancion.streams) {
                Cancion temporal = i->cancion;
                i->cancion = j->cancion;
                j->cancion = temporal;
            }
        }
    }
}

void generarPlaylist(Playlist *p, Conjunto generos)
{
    int i;
    for (i = 0; i < N_CANCIONES; i++) {
        if (generos & GENERO(catalogo[i].genero))
            agregarFinal(p, catalogo[i]);
    }
    ordenarPorStreams(p);
}

void imprimirCancion(const Cancion *c, int posicion)
{
    printf("%2d. %s - %s\n", posicion, c->titulo, c->artista);
    printf("    Genero: %s | Duracion: %d:%02d | Streams: %d M\n",
           NOMBRE_GENERO[c->genero], c->duracion / 60,
           c->duracion % 60, c->streams);
}

int posicionActual(const Playlist *p)
{
    Nodo *aux = p->primero;
    int posicion = 1;
    while (aux != NULL && aux != p->actual) {
        aux = aux->siguiente;
        posicion++;
    }
    return aux == NULL ? 0 : posicion;
}

void mostrarCancionActual(const Playlist *p)
{
    if (p->actual == NULL) {
        printf("\nNo hay canciones en la playlist.\n");
        return;
    }
    printf("\n========== CANCION ACTUAL =========="
           "\n");
    imprimirCancion(&p->actual->cancion, posicionActual(p));
    printf("Cancion %d de %d\n", posicionActual(p), p->cantidad);
}

void siguienteCancion(Playlist *p)
{
    if (p->actual == NULL) {
        printf("\nLa playlist esta vacia.\n");
    } else if (p->actual->siguiente == NULL) {
        printf("\nYa estas en la ultima cancion.\n");
        mostrarCancionActual(p);
    } else {
        p->actual = p->actual->siguiente;
        mostrarCancionActual(p);
    }
}

void cancionAnterior(Playlist *p)
{
    if (p->actual == NULL) {
        printf("\nLa playlist esta vacia.\n");
    } else if (p->actual->anterior == NULL) {
        printf("\nYa estas en la primera cancion.\n");
        mostrarCancionActual(p);
    } else {
        p->actual = p->actual->anterior;
        mostrarCancionActual(p);
    }
}

void mostrarPlaylist(const Playlist *p)
{
    Nodo *aux = p->primero;
    int posicion = 1;
    if (aux == NULL) {
        printf("\nLa playlist esta vacia.\n");
        return;
    }
    printf("\n========== PLAYLIST (%d canciones) ==========\n", p->cantidad);
    while (aux != NULL) {
        printf(aux == p->actual ? " >> " : "    ");
        imprimirCancion(&aux->cancion, posicion++);
        aux = aux->siguiente;
    }
}

int main(void)
{
    Playlist playlist;
    int opcion;
    Conjunto amigo1 = GENERO(URBANO) | GENERO(REGGAETON) | GENERO(ROCK);
    Conjunto amigo2 = GENERO(URBANO) | GENERO(ROCK) | GENERO(POP);
    Conjunto todos = unionConjuntos(amigo1, amigo2);
    Conjunto comunes = interseccion(amigo1, amigo2);
    Conjunto exclusivos1 = diferencia(amigo1, amigo2);
    Conjunto exclusivos2 = diferencia(amigo2, amigo1);

    printf("========== PREFERENCIAS MUSICALES ==========\n");
    imprimirConjunto("Lucia", amigo1);
    imprimirConjunto("Isaac", amigo2);
    printf("\n========== OPERACIONES ENTRE CONJUNTOS ==========\n");
    imprimirConjunto("Mezcla de ambos", todos);
    imprimirConjunto("Gustos en comun", comunes);
    imprimirConjunto("Exclusivos de Lucia", exclusivos1);
    imprimirConjunto("Exclusivos de Isaac", exclusivos2);

    inicializarPlaylist(&playlist);
    generarPlaylist(&playlist, comunes);

    printf("\n========== PLAYLIST GENERAL ==========\n");
    imprimirConjunto("GENEROS CONSERVADOS", comunes);
    mostrarPlaylist(&playlist);
    mostrarCancionActual(&playlist);

    do {
        printf("\n========== MENU DE REPRODUCCION ==========\n");
        printf("1. Siguiente cancion\n");
        printf("2. Cancion anterior\n");
        printf("3. Mostrar playlist\n");
        printf("0. Salir\n");
        printf("Opcion: ");

        if (scanf("%d", &opcion) != 1) {
            int c;
            while ((c = getchar()) != '\n' && c != EOF) { }
            opcion = -1;
            printf("Entrada invalida. Escribe un numero.\n");
            continue;
        }

        switch (opcion) {
            case 1: siguienteCancion(&playlist); break;
            case 2: cancionAnterior(&playlist); break;
            case 3: mostrarPlaylist(&playlist); break;
            case 0: printf("Cerrando playlist. Hasta luego.\n"); break;
            default: printf("Opcion no valida.\n");
        }
    } while (opcion != 0);

    liberarPlaylist(&playlist);
    return 0;
}
