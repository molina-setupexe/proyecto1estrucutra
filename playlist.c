
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

/* Un conjunto se representa mediante un vector binario.
   1 = el genero pertenece al conjunto.
   0 = el genero no pertenece al conjunto. */
typedef struct {
    int pertenece[N_GENEROS];
} ConjuntoGeneros;

typedef struct {
    char titulo[60];
    char artista[60];
    int genero;
    int duracion;  /* Segundos */
    int streams;   /* Millones de reproducciones */
} Cancion;


/* ================= OPERACIONES ENTRE CONJUNTOS ================= */

/* Union: A U B */
ConjuntoGeneros unionConjuntos(
    ConjuntoGeneros a, ConjuntoGeneros b)
{
    ConjuntoGeneros r;

    for (int i = 0; i < N_GENEROS; i++)
        r.pertenece[i] =
            a.pertenece[i] || b.pertenece[i];

    return r;
}

/* Interseccion: A ∩ B */
ConjuntoGeneros interseccion(
    ConjuntoGeneros a, ConjuntoGeneros b)
{
    ConjuntoGeneros r;

    for (int i = 0; i < N_GENEROS; i++)
        r.pertenece[i] =
            a.pertenece[i] && b.pertenece[i];

    return r;
}

/* Diferencia: A - B */
ConjuntoGeneros diferencia(
    ConjuntoGeneros a, ConjuntoGeneros b)
{
    ConjuntoGeneros r;

    for (int i = 0; i < N_GENEROS; i++)
        r.pertenece[i] =
            a.pertenece[i] && !b.pertenece[i];

    return r;
}

/* Diferencia simetrica: A △ B
   Elementos que pertenecen a exactamente uno de los conjuntos. */
ConjuntoGeneros diferenciaSimetrica(
    ConjuntoGeneros a, ConjuntoGeneros b)
{
    ConjuntoGeneros r;

    for (int i = 0; i < N_GENEROS; i++)
        r.pertenece[i] =
            a.pertenece[i] != b.pertenece[i];

    return r;
}

/* Complemento relativo: U - A */
ConjuntoGeneros complemento(ConjuntoGeneros a)
{
    ConjuntoGeneros r;

    for (int i = 0; i < N_GENEROS; i++)
        r.pertenece[i] = !a.pertenece[i];

    return r;
}

/* Imprimir un conjunto */
void imprimirConjunto(
    const char *nombre, ConjuntoGeneros c)
{
    printf("%s = {", nombre);

    int primero = 1;

    for (int i = 0; i < N_GENEROS; i++) {
        if (c.pertenece[i]) {
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


/* ================= FUNCIONES DE PLAYLIST ================= */

int perteneceGenero(ConjuntoGeneros c, int genero)
{
    return c.pertenece[genero];
}

void ordenarPorStreams(
    int playlist[], int total, Cancion catalogo[])
{
    /* Ordenamiento burbuja descendente */
    for (int i = 0; i < total - 1; i++) {
        for (int j = 0; j < total - 1 - i; j++) {

            if (catalogo[playlist[j]].streams <
                catalogo[playlist[j + 1]].streams) {

                int temporal = playlist[j];
                playlist[j] = playlist[j + 1];
                playlist[j + 1] = temporal;
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
    printf("---------------------------------------------\n");

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


/* ================= PROGRAMA PRINCIPAL ================= */

int main(void)
{
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

    /* Preferencias de los amigos */
    ConjuntoGeneros amigo1 = {{
        0, 1, 1, 1, 0, 0, 0
    }}; /* URBANO, REGGAETON, ROCK */

    ConjuntoGeneros amigo2 = {{
        0, 1, 0, 1, 0, 0, 1
    }}; /* URBANO, ROCK, POP */


    /* 1. Operaciones de conjuntos */

    ConjuntoGeneros todos =
        unionConjuntos(amigo1, amigo2);

    ConjuntoGeneros comunes =
        interseccion(amigo1, amigo2);

    ConjuntoGeneros exclusivos1 =
        diferencia(amigo1, amigo2);

    ConjuntoGeneros exclusivos2 =
        diferencia(amigo2, amigo1);

    ConjuntoGeneros exclusivos =
        diferenciaSimetrica(amigo1, amigo2);

    ConjuntoGeneros ninguno =
        complemento(todos);


    printf("========= PREFERENCIAS MUSICALES =========\n");

    imprimirConjunto("AMIGO 1", amigo1);
    imprimirConjunto("AMIGO 2", amigo2);

    printf("\n========= OPERACIONES ENTRE CONJUNTOS =========\n");

    imprimirConjunto("UNION A U B", todos);
    imprimirConjunto("INTERSECCION A ^ B", comunes);
    imprimirConjunto("A - B", exclusivos1);
    imprimirConjunto("B - A", exclusivos2);
    imprimirConjunto("DIFERENCIA SIMETRICA", exclusivos);
    imprimirConjunto("GENEROS QUE NO GUSTAN A NINGUNO", ninguno);


   

    ConjuntoGeneros playlistGeneral =
        diferencia(todos, exclusivos);

    printf("\n========= PLAYLIST GENERAL =========\n");
    imprimirConjunto("GENEROS CONSERVADOS", playlistGeneral);


    

    int playlist[N_CANCIONES];
    int total = 0;

    for (int i = 0; i < N_CANCIONES; i++) {

        if (perteneceGenero(
                playlistGeneral, catalogo[i].genero)) {

            playlist[total] = i;
            total++;
        }
    }

    imprimirPlaylist(
        "PLAYLIST FINAL SIN GENEROS EXCLUSIVOS",
        playlist, total, catalogo);


    /* 4. Ordenar las canciones por reproducciones */

    ordenarPorStreams(playlist, total, catalogo);

    printf("\n========= PLAYLIST ORDENADA POR STREAMS =========\n");

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
