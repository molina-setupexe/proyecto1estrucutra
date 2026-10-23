
catalogo = [
    ("Ella Baila Sola", "Eslabon Armado", "Regional"),
    ("La Bebe", "Yng Lvcas", "Reggaeton"),
    ("Blinding Lights", "The Weeknd", "Pop"),
    ("Numb", "Linkin Park", "Rock"),
    ("Titi Me Pregunto", "Bad Bunny", "Reggaeton"),
    ("Cruel Summer", "Taylor Swift", "Pop"),
    ("La Chona", "Los Tucanes de Tijuana", "Regional"),
    ("Smells Like Teen Spirit", "Nirvana", "Rock"),
    ("Despecha", "Rosalia", "Pop"),
    ("Pepas", "Farruko", "Urbano"),
    ("Danza Kuduro", "Don Omar", "Reggaeton"),
    ("Seven Nation Army", "The White Stripes", "Rock"),
    ("Ojitos Lindos", "Bad Bunny", "Reggaeton"),
    ("Viva la Vida", "Coldplay", "Rock"),
    ("Me Porto Bonito", "Bad Bunny", "Urbano"),
    ("Flowers", "Miley Cyrus", "Pop"),
    ("Ella Quiere Beber", "Anuel AA", "Urbano"),
    ("De Musica Ligera", "Soda Stereo", "Rock"),
    ("Mi Gente", "J Balvin", "Urbano"),
    ("As It Was", "Harry Styles", "Pop")
]

# Conjuntos de generos favoritos
amigo1 = {"Urbano", "Reggaeton", "Rock"}
amigo2 = {"Urbano", "Rock", "Pop"}

# Operaciones con conjuntos

# Union: elementos que estan en A o en B
union = amigo1 | amigo2

# Interseccion: elementos que estan en A y en B
interseccion = amigo1 & amigo2

# Diferencia: elementos de A que no estan en B
resta1 = amigo1 - amigo2

# Diferencia: elementos de B que no estan en A
resta2 = amigo2 - amigo1

# Diferencia simetrica: elementos que estan en uno u otro,
# pero no en ambos
diferencia_simetrica = amigo1 ^ amigo2


# Mostrar las operaciones
print("===== CONJUNTOS ORIGINALES =====")
print("Amigo 1:", amigo1)
print("Amigo 2:", amigo2)

print("\n===== UNION =====")
print("A union B:", union)

print("\n===== INTERSECCION =====")
print("A interseccion B:", interseccion)

print("\n===== DIFERENCIA =====")
print("A - B:", resta1)
print("B - A:", resta2)

print("\n===== DIFERENCIA SIMETRICA =====")
print("A diferencia simetrica B:", diferencia_simetrica)


# Funcion para mostrar las canciones de un conjunto
def mostrar_playlist(nombre, generos):
    print("\n" + nombre)
    print("-" * 40)

    canciones_encontradas = 0

    for titulo, artista, genero in catalogo:
        if genero in generos:
            print(titulo, "-", artista, "| Genero:", genero)
            canciones_encontradas += 1

    if canciones_encontradas == 0:
        print("No hay canciones para estos generos.")


# Mostrar las playlists de cada operacion
mostrar_playlist("PLAYLIST DE LA UNION", union)
mostrar_playlist("PLAYLIST DE LA INTERSECCION", interseccion)
mostrar_playlist("PLAYLIST A - B", resta1)
mostrar_playlist("PLAYLIST B - A", resta2)
mostrar_playlist("PLAYLIST DE LA DIFERENCIA SIMETRICA",
                 diferencia_simetrica)