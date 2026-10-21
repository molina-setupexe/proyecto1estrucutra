import random

TAMANO = 10

biomas = {
    "bosque": {
        "simbolo": "B",
        "recursos": ["madera", "hierbas", "cristales"]
    },
    "desierto": {
        "simbolo": "D",
        "recursos": ["piedra", "cristales"]
    },
    "nieve": {
        "simbolo": "N",
        "recursos": ["piedra", "hierbas"]
    },
    "pantano": {
        "simbolo": "P",
        "recursos": ["hierbas", "cristales"]
    },
    "montana": {
        "simbolo": "M",
        "recursos": ["piedra", "cristales"]
    },
    "pradera": {
        "simbolo": "R",
        "recursos": ["hierbas", "madera"]
    }
}

# Crear el mundo con una matriz
mundo = []

for fila in range(TAMANO):
    fila_biomas = []

    for columna in range(TAMANO):
        bioma = random.choice(list(biomas.keys()))
        fila_biomas.append(bioma)

    mundo.append(fila_biomas)

# Matriz de zonas visitadas
visitados = []

for fila in range(TAMANO):
    visitados.append([False] * TAMANO)



# Posicion del jugador
jugador_fila = TAMANO // 2
jugador_columna = TAMANO // 2
mundo[jugador_fila][jugador_columna] = "bosque"

# Estado del jugador
vida = 100
energia = 100

inventario = {
    "madera": 0,
    "piedra": 0,
    "hierbas": 0,
    "cristales": 0
}


# Mostrar el mapa
def mostrar_mapa():
    print("\n MAPA ")

    for fila in range(TAMANO):
        for columna in range(TAMANO):

            if fila == jugador_fila and columna == jugador_columna:
                print("@", end=" ")

            elif visitados[fila][columna]:
                bioma = mundo[fila][columna]
                print(biomas[bioma]["simbolo"], end=" ")

            else:
                print("?", end=" ")

        print()

    print("\n@ Tu personaje | ? Zona desconocida")
    print("B Bosque | D Desierto | N Nieve")
    print("P Pantano | M Montana | R Pradera")


# Mostrar inventario
def mostrar_inventario():
    print("\nINVENTARIO ")

    for recurso, cantidad in inventario.items():
        print(recurso.capitalize() + ":", cantidad)


# Explorar la zona actual
def explorar():
    global vida, energia

    bioma = mundo[jugador_fila][jugador_columna]

    visitados[jugador_fila][jugador_columna] = True

    print("\nEstas explorando el bioma:", bioma.upper())

    # El bosque recupera energia
    if bioma == "bosque":
        energia = min(100, energia + 5)
        print("El bosque te ayuda a recuperar 5 de energia.")

    # Encontrar recursos
    if random.random() < 0.7:
        recurso = random.choice(biomas[bioma]["recursos"])
        cantidad = random.randint(1, 3)

        inventario[recurso] += cantidad

        print("Encontraste", cantidad, "de", recurso + "!")
    else:
        print("No encontraste recursos esta vez.")

    # Eventos aleatorios
    evento = random.randint(1, 10)

    if evento == 1:
        print("¡Encontraste ruinas antiguas!")
        inventario["cristales"] += 2

    elif evento == 2:
        print("¡Encontraste un cofre abandonado!")
        inventario["piedra"] += 3

    elif evento == 3:
        print("¡Una criatura salvaje te ataca!")
        vida -= 10
        print("Perdiste 10 puntos de vida.")

    else:
        print("No ocurrio nada extraordinario.")

    # Evitar que la vida sea negativa
    vida = max(0, vida)




# Mover al jugador
def mover(direccion):
    global jugador_fila, jugador_columna, energia

    nueva_fila = jugador_fila
    nueva_columna = jugador_columna

    if direccion == "w":
        nueva_fila -= 1
    elif direccion == "s":
        nueva_fila += 1
    elif direccion == "a":
        nueva_columna -= 1
    elif direccion == "d":
        nueva_columna += 1

    # Revisar los limites del mapa
    if (nueva_fila < 0 or nueva_fila >= TAMANO
            or nueva_columna < 0
            or nueva_columna >= TAMANO):
        print("No puedes salir de los limites del mundo.")
        return

    # Comprobar energia
    if energia < 10:
        print("No tienes energia suficiente para moverte.")
        print("Explora el bosque para recuperar un poco.")
        return

    # Realizar movimiento
    jugador_fila = nueva_fila
    jugador_columna = nueva_columna
    energia -= 10

    print("\nTe has movido a una nueva zona.")

    explorar()


# Inicio del juego

print("MAC")

print("Explora un mundo desconocido.")
print("Encuentra recursos y descubre ruinas.")
print("¡Sobrevive todo lo que puedas!")

visitados[jugador_fila][jugador_columna] = True
explorar()

# Bucle principal
while vida > 0:

    mostrar_mapa()

    print("\nPERSONAJE")
    print("Vida:", vida, "/ 100")
    print("Energia:", energia, "/ 100")

    print("\n¿Que quieres hacer?")
    print("W - Mover al norte")
    print("S - Mover al sur")
    print("A - Mover al oeste")
    print("D - Mover al este")
    print("I - Ver inventario")
    print("E - Explorar la zona actual")
    print("Q - Salir del juego")

    opcion = input("\nElige una accion: ").lower().strip()

    if opcion in ["w", "a", "s", "d"]:
        mover(opcion)

    elif opcion == "i":
        mostrar_inventario()

    elif opcion == "e":
        explorar()

    elif opcion == "q":
        print("\nAbandonaste el mundo de Aether.")
        break

    else:
        print("Opcion no valida. Intenta de nuevo.")

    # Recuperacion ligera de energia
    if opcion in ["w", "a", "s", "d"] and vida > 0:
        energia = min(100, energia)

    if vida <= 0:
        print("\nTu aventura ha terminado...")
        mostrar_inventario()

print("\nGracias por jugar MAC.")