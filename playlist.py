catalogo = [
    ("Ella Baila Sola", "Eslabon Armado", "Regional"),
    ("La Bebe", "Yng Lvcas", "Reggaeton"),
    ("Blinding Lights", "The Weeknd", "Pop"),
    ("Numb", "Linkin Park", "Rock"),
    ("Tití Me Preguntó", "Bad Bunny", "Reggaeton"),
    ("Cruel Summer", "Taylor Swift", "Pop"),
    ("La Chona", "Los Tucanes de Tijuana", "Regional"),
    ("Smells Like Teen Spirit", "Nirvana", "Rock"),
    ("Despechá", "Rosalía", "Pop"),
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

# Conjuntos de generos que le gustan a cada amigo
amigo1 = {"Urbano", "Reggaeton", "Rock"}
amigo2 = {"Urbano", "Rock", "Pop"}

# Operaciones con conjuntos
union = amigo1 | amigo2
interseccion = amigo1 & amigo2

# Mostrar los conjuntos
print("GENEROS DE CADA AMIGO")
print("Amigo 1:", amigo1)
print("Amigo 2:", amigo2)

print("\nUNION DE GENEROS")
print(union)

print("\nINTERSECCION DE GENEROS")
print(interseccion)


# Funcion para mostrar una playlist
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


# Mostrar las playlists
mostrar_playlist("PLAYLIST CON LA UNION", union)
mostrar_playlist("PLAYLIST CON LA INTERSECCION", interseccion)