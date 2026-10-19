#include <stdio.h>

#define N_CANCIONES 20
#define N_GENEROS   7


enum { CORRIDO, URBANO, REGGAETON, ROCK, METAL, SALSA, POP };
const char *NOMBRE_GENERO[N_GENEROS] =
    {"CORRIDO", "URBANO", "REGGAETON", "ROCK", "METAL", "SALSA", "POP"};

typedef int ConjuntoGeneros[N_GENEROS];


typedef struct {
    char titulo[60];
    char artista[60];
    int  genero;     
    int  duracion;   
    int  streams;    
} Cancion;


void interseccion(ConjuntoGeneros a, ConjuntoGeneros b, ConjuntoGeneros r) {
    for (int i = 0; i < N_GENEROS; i++)
        r[i] = (a[i] && b[i]) ? 1 : 0;
}

void imprimirConjunto(const char *nombre, ConjuntoGeneros c) {
    printf("%s = [", nombre);
    int primero = 1;
    for (int i = 0; i < N_GENEROS; i++) {
        if (c[i]) {
            printf("%s%s", primero ? "" : ", ", NOMBRE_GENERO[i]);
            primero = 0;
        }
    }
    printf("]\n");
}

int main(void) {
    Cancion catalogo[N_CANCIONES] = {
        {"PIENSALO",                    "Junior H",                          CORRIDO,   180,  300},
        {"Gil",                         "Milo J",                            URBANO,    195,  150},
        {"Nino",                        "Milo J",                            URBANO,    200,  140},
        {"Morocha",                     "Milo J",                            URBANO,    185,  120},
        {"Andromeda",                   "Wos",                               URBANO,    175,   60},
        {"Contando Ovejas",             "Wos",                               URBANO,    210,   50},
        {"TIERRA ZANTA",                "Trueno",                            URBANO,    215,   90},
        {"Mi vecinita",                 "Plan B",                            REGGAETON, 230,  100},
        {"Hasta Jesus tuvo un mal dia", "Ca7riel y Paco Amoroso",            ROCK,      240,   70},
        {"Bat Country",                 "Avenged Sevenfold",                 METAL,     313,  400},
        {"Oh, Que Sera?",               "Hector Lavoe",                      SALSA,     330,   80},
        {"Neon",                        "John Mayer",                        POP,       260,  350},
        {"Okupa",                       "Wos",                               URBANO,    190,   80},
        {"Bzrp Music Sessions Vol. 52", "Bizarrap y Quevedo",                URBANO,    198, 1500},
        {"Gasolina",                    "Daddy Yankee",                      REGGAETON, 192,  900},
        {"De musica ligera",            "Soda Stereo",                       ROCK,      212,  600},
        {"Enter Sandman",               "Metallica",                         METAL,     331, 2000},
        {"La vida es un carnaval",      "Celia Cruz",                        SALSA,     277,  700},
        {"Ella Baila Sola",             "Eslabon Armado y Peso Pluma",       CORRIDO,   164, 1800},
        {"Flowers",                     "Miley Cyrus",                       POP,       200, 2300}
    };

    /* Preferencias de los amigos */
    ConjuntoGeneros prefAmigo1 = {0, 1, 1, 1, 0, 0, 0};  /* URBANO, REGGAETON, ROCK */
    ConjuntoGeneros prefAmigo2 = {0, 1, 0, 1, 0, 0, 1};  /* URBANO, ROCK, POP */
    ConjuntoGeneros playlistComun;


    interseccion(prefAmigo1, prefAmigo2, playlistComun);

    imprimirConjunto("PREF_AMIGO1", prefAmigo1);
    imprimirConjunto("PREF_AMIGO2", prefAmigo2);
    imprimirConjunto("PLAYLIST_COMUN", playlistComun);

    /* Filtrar catalogo sin repetidos */
    int yaAgregadas[N_CANCIONES] = {0}; 
    int playlist[N_CANCIONES];            
    int total = 0, duracionTotal = 0;

    for (int i = 0; i < N_CANCIONES; i++) {
        if (playlistComun[catalogo[i].genero] && !yaAgregadas[i]) {
            playlist[total++] = i;
            yaAgregadas[i] = 1;           
            duracionTotal += catalogo[i].duracion;
        }
    }

    printf("\nPLAYLIST final  (%d canciones)\n", total);
    for (int k = 0; k < total; k++) {
        Cancion *c = &catalogo[playlist[k]];
        printf("%d. %s - %s [%s] (%d:%02d)\n", k + 1, c->titulo, c->artista,
               NOMBRE_GENERO[c->genero], c->duracion / 60, c->duracion % 60);
    }
    printf("Duracion total: %d:%02d\n", duracionTotal / 60, duracionTotal % 60);

    
    for (int i = 0; i < total - 1; i++) {
        for (int j = 0; j < total - 1 - i; j++) {
            if (catalogo[playlist[j]].streams < catalogo[playlist[j + 1]].streams) {
                int temp = playlist[j];
                playlist[j] = playlist[j + 1];
                playlist[j + 1] = temp;
            }
        }
    }

    printf("\nPLAYLIST ordenada por vistas");
    for (int k = 0; k < total; k++) {
        Cancion *c = &catalogo[playlist[k]];
        printf("%d. %s - %s (%d M)\n", k + 1, c->titulo, c->artista, c->streams);
    }

    return 0;
}