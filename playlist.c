
#include <stdio.h>
#define N_CANCIONES 20
#define N_GENEROS 7

enum {
    CORRIDO, URBANO, REGGAETON, ROCK,
    METAL, SALSA, POP
};

const char *NOMBRE_GENERO[N_GENEROS] = {
    "CORRIDO", "URBANO", "REGGAETON", "ROCK",
    "METAL", "SALSA", "POP"
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

//Union
Conjunto unionConjuntos(Conjunto a, Conjunto b) {
    return a | b;
}

//interseccion
Conjunto interseccion(Conjunto a, Conjunto b) {
    return a & b;
}

//diferencia
Conjunto diferencia(Conjunto a, Conjunto b) {
    return a & ~b;
}


void imprimirConjunto(const char *nombre, Conjunto c) {
    printf("%s = {", nombre);

    int primero = 1;

    for (int i = 0; i < N_GENEROS; i++) {
        if (c & GENERO(i)) {
            printf("%s%s",
                   primero ? "" : ", ",
                   NOMBRE_GENERO[i]);
            primero = 0;
        }
    }

    if (primero)
        printf("vacio");

    printf("}\n");
}


void ordenarPorStreams(
    int playlist[], int total, Cancion catalogo[])
{
    for (int i = 0; i < total - 1; i++) {
        for (int j = 0; j < total - 1 - i; j++) {

            if (catalogo[playlist[j]].streams <
                catalogo[playlist[j + 1]].streams) {

                int temp = playlist[j];
                playlist[j] = playlist[j + 1];
                playlist[j + 1] = temp;
            }
        }
    }
}

void imprimirPlaylist(
    const char *titulo,
    int playlist[],
    int total,
    Cancion catalogo[])
{
    int duracionTotal = 0;

    printf("\n%s (%d canciones)\n", titulo, total);
    printf("-----------------------------------------------\n");

    for (int i = 0; i < total; i++) {
        Cancion *c = &catalogo[playlist[i]];

        printf("%d. %s - %s [%s] (%d:%02d)\n",
               i + 1,
               c->titulo,
               c->artista,
               NOMBRE_GENERO[c->genero],
               c->duracion / 60,
               c->duracion % 60);

        duracionTotal += c->duracion;
    }

    printf("Duracion total: %d:%02d\n",
           duracionTotal / 60,
           duracionTotal % 60);
}


int main(void) {

    Cancion catalogo[N_CANCIONES] = {
        {"PIENSALO", "Junior H", CORRIDO, 180, 300},
        {"Gil", "Milo J", URBANO, 195, 150},
        {"Nino", "Milo J", URBANO, 200, 140},
        {"Morocha", "Milo J", URBANO, 185, 120},
        {"Andromeda", "Wos", URBANO, 175, 60},
        {"Contando Ovejas", "Wos", URBANO, 210, 50},
        {"TIERRA ZANTA", "Trueno", URBANO, 215, 90},
        {"Mi vecinita", "Plan B", REGGAETON, 230, 100},
        {"Hasta Jesus tuvo un mal dia",
         "Ca7riel y Paco Amoroso", ROCK, 240, 70},
        {"Bat Country", "Avenged Sevenfold", METAL, 313, 400},
        {"Oh, Que Sera?", "Hector Lavoe", SALSA, 330, 80},
        {"Neon", "John Mayer", POP, 260, 350},
        {"Okupa", "Wos", URBANO, 190, 80},
        {"Bzrp Music Sessions Vol. 52",
         "Bizarrap y Quevedo", URBANO, 198, 1500},
        {"Gasolina", "Daddy Yankee", REGGAETON, 192, 900},
        {"De musica ligera", "Soda Stereo", ROCK, 212, 600},
        {"Enter Sandman", "Metallica", METAL, 331, 2000},
        {"La vida es un carnaval", "Celia Cruz", SALSA, 277, 700},
        {"Ella Baila Sola", "Eslabon Armado y Peso Pluma",
         CORRIDO, 164, 1800},
        {"Flowers", "Miley Cyrus", POP, 200, 2300}
    };


    Conjunto amigo1 =
        GENERO(URBANO) | GENERO(REGGAETON) | GENERO(ROCK);

    Conjunto amigo2 =
        GENERO(URBANO) |
        GENERO(ROCK) |
        GENERO(POP);


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



    Conjunto playlistGeneral = interseccion(amigo1, amigo2);

    printf("\n========== PLAYLIST GENERAL ==========\n");

    imprimirConjunto("GENEROS CONSERVADOS", playlistGeneral);
    int playlist[N_CANCIONES];
    int total = 0;

    for (int i = 0; i < N_CANCIONES; i++) {

        if (playlistGeneral & GENERO(catalogo[i].genero)) {
            playlist[total++] = i;
        }
    }
    imprimirPlaylist(
        "PLAYLIST FINAL",
        playlist, total, catalogo);


    ordenarPorStreams(playlist, total, catalogo);
	printf("\n========== PLAYLIST ORDENADA POR STREAMS ==========\n");

    for (int i = 0; i < total; i++) {
        Cancion *c = &catalogo[playlist[i]];

        printf("%d. %s - %s (%d M)\n",
               i + 1,
               c->titulo,
               c->artista,
               c->streams);
    }

    return 0;
}
