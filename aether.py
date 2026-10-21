import random
import json
from collections import deque
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

TAMANO = 10
CELDA = 62
MARGEN = 18
VIDA_MAXIMA = 100
ENERGIA_MAXIMA = 100

BIOMAS = {
    "bosque":   {"simbolo": "B", "color": "#347A45", "claro": "#5FAE69"},
    "desierto": {"simbolo": "D", "color": "#C99B55", "claro": "#E5C47C"},
    "nieve":    {"simbolo": "N", "color": "#B8D7E8", "claro": "#E6F5FC"},
    "pantano":  {"simbolo": "P", "color": "#526B45", "claro": "#839C65"},
    "montana":  {"simbolo": "M", "color": "#737987", "claro": "#A7ADB8"},
    "pradera":  {"simbolo": "R", "color": "#7CA64B", "claro": "#A9CE6B"},
}

NOMBRES_ENEMIGOS = {
    "bosque": "Lobo del bosque",
    "desierto": "Escorpion del desierto",
    "nieve": "Golem de hielo",
    "pantano": "Criatura del pantano",
    "montana": "Guardian de piedra",
    "pradera": "Bandido errante",
}

nombre_jugador = ""
mundo = []
visitados = []
jugador_fila = TAMANO // 2
jugador_columna = TAMANO // 2
vida = VIDA_MAXIMA
energia = ENERGIA_MAXIMA
nivel = 1
experiencia = 0.0
jefes = set()
jefes_derrotados = 0
salida_fila = 0
salida_columna = 0
salida_revelada = False
victoria = False
partida_terminada = False
eventos = deque(maxlen=80)
ventana_combate = None
juego_iniciado = False

# --------------------------- Interfaz ---------------------------

raiz = tk.Tk()
raiz.title("AETHER | Exploracion y supervivencia")
raiz.geometry("1450x900")
raiz.minsize(1120, 720)
raiz.configure(bg="#07111f")

FUENTE = ("Segoe UI", 10)
FUENTE_BOLD = ("Segoe UI", 10, "bold")
FONDO = "#07111f"
PANEL = "#0c1a2b"
PANEL2 = "#10243a"
BORDE = "#244564"
TEXTO = "#eaf3ff"
SUAVE = "#9eb5cf"
AZUL = "#1688f8"
VERDE = "#56d68b"
ROJO = "#ff5c68"
AMARILLO = "#f7c948"

# Layout principal
contenedor = tk.Frame(raiz, bg=FONDO)
contenedor.pack(fill="both", expand=True, padx=8, pady=8)

barra_superior = tk.Frame(contenedor, bg=PANEL, highlightbackground=BORDE, highlightthickness=1)
barra_superior.pack(fill="x", pady=(0, 8))

tk.Label(barra_superior, text="✥  AETHER", font=("Segoe UI", 18, "bold"),
         fg=TEXTO, bg=PANEL, padx=16, pady=10).pack(side="left")
titulo_mundo = tk.Label(barra_superior, text="El mundo te espera",
                        font=("Segoe UI", 12), fg=SUAVE, bg=PANEL)
titulo_mundo.pack(side="left", padx=20)
jugador_label = tk.Label(barra_superior, text="Jugador: —",
                         font=FUENTE_BOLD, fg=TEXTO, bg=PANEL, padx=16)
jugador_label.pack(side="right")

cuerpo = tk.Frame(contenedor, bg=FONDO)
cuerpo.pack(fill="both", expand=True)

# Menú lateral
lateral = tk.Frame(cuerpo, bg=PANEL, width=205, highlightbackground=BORDE, highlightthickness=1)
lateral.grid(row=0, column=0, sticky="ns", padx=(0, 8))
lateral.grid_propagate(False)

tk.Label(lateral, text="EXPLORACIÓN", font=("Segoe UI", 9, "bold"),
         fg=SUAVE, bg=PANEL, pady=14).pack(fill="x")

contenido = tk.Frame(cuerpo, bg=FONDO)
contenido.grid(row=0, column=1, sticky="nsew")

panel_derecho = tk.Frame(cuerpo, bg=PANEL, width=230, highlightbackground=BORDE, highlightthickness=1)
panel_derecho.grid(row=0, column=2, sticky="ns", padx=(8, 0))
panel_derecho.grid_propagate(False)
cuerpo.grid_rowconfigure(0, weight=1)
cuerpo.grid_columnconfigure(1, weight=1)

# Mapa central
marco_mapa = tk.Frame(contenido, bg=PANEL, highlightbackground=BORDE, highlightthickness=1)
marco_mapa.pack(fill="both", expand=True)

encabezado_mapa = tk.Frame(marco_mapa, bg=PANEL)
encabezado_mapa.pack(fill="x", padx=12, pady=(10, 4))
tk.Label(encabezado_mapa, text="MAPA DE AETHER", font=("Segoe UI", 13, "bold"),
         fg=TEXTO, bg=PANEL).pack(side="left")
estado_mapa = tk.Label(encabezado_mapa, text="Introduce tu nombre para comenzar",
                       font=FUENTE, fg=SUAVE, bg=PANEL)
estado_mapa.pack(side="right")

canvas = tk.Canvas(marco_mapa, bg="#081321", highlightthickness=0)
canvas.pack(fill="both", expand=True, padx=8, pady=8)

leyenda = tk.Frame(marco_mapa, bg=PANEL2)
leyenda.pack(fill="x", padx=8, pady=(0, 8))

# Panel derecho
def titulo_panel(parent, texto):
    tk.Label(parent, text=texto, font=("Segoe UI", 10, "bold"),
             fg=TEXTO, bg=PANEL, anchor="w", padx=12, pady=10).pack(fill="x")

titulo_panel(panel_derecho, "ESTADO DEL PERSONAJE")
estado_frame = tk.Frame(panel_derecho, bg=PANEL)
estado_frame.pack(fill="x", padx=12)

vida_texto = tk.Label(estado_frame, text="Vida  100 / 100", font=FUENTE_BOLD, fg=TEXTO, bg=PANEL, anchor="w")
vida_texto.pack(fill="x", pady=(2, 3))
vida_barra = tk.Canvas(estado_frame, height=12, bg="#243449", highlightthickness=0)
vida_barra.pack(fill="x", pady=(0, 10))

energia_texto = tk.Label(estado_frame, text="Energía  100 / 100", font=FUENTE_BOLD, fg=TEXTO, bg=PANEL, anchor="w")
energia_texto.pack(fill="x", pady=(2, 3))
energia_barra = tk.Canvas(estado_frame, height=12, bg="#243449", highlightthickness=0)
energia_barra.pack(fill="x", pady=(0, 10))

nivel_titulo = tk.Label(estado_frame, text="NIVEL 1 · 0%", font=FUENTE_BOLD, fg=AMARILLO, bg=PANEL, anchor="w")
nivel_titulo.pack(fill="x", pady=(4, 3))
xp_barra = tk.Canvas(estado_frame, height=12, bg="#243449", highlightthickness=0)
xp_barra.pack(fill="x", pady=(0, 8))

tk.Frame(panel_derecho, bg=BORDE, height=1).pack(fill="x", padx=10, pady=5)
titulo_panel(panel_derecho, "MÉTRICAS")
metricas_frame = tk.Frame(panel_derecho, bg=PANEL)
metricas_frame.pack(fill="x", padx=12)
metricas_label = tk.Label(metricas_frame, text="Zonas exploradas: 0\nJefes derrotados: 0 / 3\nMovimientos: 0",
                          font=FUENTE, fg=SUAVE, bg=PANEL, justify="left", anchor="w")
metricas_label.pack(fill="x")

tk.Frame(panel_derecho, bg=BORDE, height=1).pack(fill="x", padx=10, pady=5)
titulo_panel(panel_derecho, "REGISTRO")
registro = tk.Listbox(panel_derecho, height=11, bg="#091625", fg="#cfe2f8",
                      selectbackground=AZUL, relief="flat", borderwidth=0,
                      font=("Segoe UI", 9), activestyle="none")
registro.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# Barra inferior
barra_inferior = tk.Frame(contenedor, bg=PANEL, highlightbackground=BORDE, highlightthickness=1)
barra_inferior.pack(fill="x", pady=(8, 0))
mensaje = tk.Label(barra_inferior, text="Bienvenido a Aether.", font=FUENTE,
                   fg=TEXTO, bg=PANEL, anchor="w", padx=12, pady=10)
mensaje.pack(side="left", fill="x", expand=True)
atajos = tk.Label(barra_inferior, text="W A S D: mover   E: explorar   R: descansar   G/L: guardar/cargar   Q: salir",
                  font=("Segoe UI", 9), fg=SUAVE, bg=PANEL, padx=12)
atajos.pack(side="right")

movimientos = 0
turnos = 0
seccion_actual = "Mapa"

# --------------------------- Utilidades ---------------------------

def registrar(texto, color=None):
    if len(eventos) == eventos.maxlen:
        registro.delete(0)
    eventos.append(texto)
    registro.insert("end", "• " + texto)
    if color:
        registro.itemconfig("end", fg=color)
    registro.yview_moveto(1.0)
    mensaje.config(text=texto)

def posicion_libre(excluir):
    while True:
        f = random.randrange(TAMANO)
        c = random.randrange(TAMANO)
        if (f, c) not in excluir:
            return f, c

def generar_mundo():
    global mundo, visitados, jugador_fila, jugador_columna
    global jefes, salida_fila, salida_columna
    global salida_revelada, jefes_derrotados, victoria
    global vida, energia, nivel, experiencia, movimientos, turnos
    global partida_terminada, eventos

    mundo = [
        [random.choice(list(BIOMAS.keys())) for _ in range(TAMANO)]
        for _ in range(TAMANO)
    ]
    jugador_fila = TAMANO // 2
    jugador_columna = TAMANO // 2
    mundo[jugador_fila][jugador_columna] = "bosque"

    visitados = [[False] * TAMANO for _ in range(TAMANO)]
    visitados[jugador_fila][jugador_columna] = True

    ocupadas = {(jugador_fila, jugador_columna)}
    jefes = set()
    for _ in range(3):
        p = posicion_libre(ocupadas)
        jefes.add(p)
        ocupadas.add(p)

    salida_fila, salida_columna = posicion_libre(ocupadas)
    salida_revelada = False
    jefes_derrotados = 0
    victoria = False
    partida_terminada = False
    vida = VIDA_MAXIMA
    energia = ENERGIA_MAXIMA
    nivel = 1
    experiencia = 0.0
    movimientos = 0
    turnos = 0
    eventos = deque(maxlen=80)
    registro.delete(0, "end")
    registrar("Has llegado al bosque inicial.", VERDE)
    actualizar_todo()

def explorar_manual():
    global turnos
    if not juego_iniciado or partida_terminada or victoria:
        return
    turnos += 1
    explorar()

def dibujar_barra(canvas_barra, valor, maximo, color):
    canvas_barra.delete("all")
    w = max(canvas_barra.winfo_width(), 120)
    canvas_barra.create_rectangle(0, 0, w, 12, fill="#243449", outline="")
    relleno = max(0, min(w, w * valor / maximo))
    canvas_barra.create_rectangle(0, 0, relleno, 12, fill=color, outline="")

def dibujar_mapa():
    canvas.delete("all")
    if len(mundo) != TAMANO or len(visitados) != TAMANO:
        return
    ancho = max(canvas.winfo_width(), 2 * MARGEN + TAMANO * 25)
    alto = max(canvas.winfo_height(), 2 * MARGEN + TAMANO * 25)
    celda = min((ancho - 2 * MARGEN) / TAMANO, (alto - 2 * MARGEN) / TAMANO)
    celda = max(25, celda)
    total = celda * TAMANO
    x0 = (ancho - total) / 2
    y0 = (alto - total) / 2

    # fondo decorativo
    canvas.create_rectangle(x0 - 5, y0 - 5, x0 + total + 5, y0 + total + 5,
                            fill="#0b1b2b", outline="#244564", width=2)

    for f in range(TAMANO):
        for c in range(TAMANO):
            x1 = x0 + c * celda
            y1 = y0 + f * celda
            x2 = x1 + celda
            y2 = y1 + celda
            pos = (f, c)

            if not visitados[f][c]:
                color = "#172638"
                simbolo = "?"
            else:
                bioma = mundo[f][c]
                color = BIOMAS[bioma]["color"]
                simbolo = BIOMAS[bioma]["simbolo"]

            # La salida solo aparece después del acertijo
            if salida_revelada and pos == (salida_fila, salida_columna):
                color = "#f7c948"
                simbolo = "S"

            if pos in jefes and visitados[f][c]:
                color = "#a72c3b"
                simbolo = "J"

            if pos == (jugador_fila, jugador_columna):
                color = "#1688f8"
                simbolo = "●"

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#0a1724", width=2)

            # Decoración sutil dentro de las zonas ya descubiertas
            if visitados[f][c] and simbolo not in ("●", "J", "S"):
                canvas.create_text(x1 + 7, y1 + 6, text=simbolo, anchor="nw",
                                   fill="#ffffff", font=("Segoe UI", max(7, int(celda * .15)), "bold"))

            color_texto = "#ffffff" if simbolo in ("?", "●", "J") else "#142235"
            if simbolo == "S":
                color_texto = "#142235"
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                               text=simbolo, fill=color_texto,
                               font=("Segoe UI", max(10, int(celda * .32)), "bold"))

    estado = "Salida revelada" if salida_revelada else "Explora y encuentra a los jefes"
    estado_mapa.config(text=f"{estado}  |  Jefes restantes: {len(jefes)}")

def actualizar_todo():
    if not raiz.winfo_exists():
        return
    jugador_label.config(text=f"Jugador: {nombre_jugador or '—'}   |   Nivel: {nivel}")
    vida_texto.config(text=f"♥  Vida  {vida} / {VIDA_MAXIMA}")
    energia_texto.config(text=f"⚡ Energía  {energia} / {ENERGIA_MAXIMA}")
    nivel_titulo.config(text=f"NIVEL {nivel}  ·  {experiencia:.1f}%")
    dibujar_barra(vida_barra, vida, VIDA_MAXIMA, ROJO)
    dibujar_barra(energia_barra, energia, ENERGIA_MAXIMA, AMARILLO)
    dibujar_barra(xp_barra, experiencia, 100, VERDE)
    exploradas = sum(sum(1 for v in fila if v) for fila in visitados)
    metricas_label.config(
        text=f"Zonas exploradas: {exploradas}\n"
             f"Jefes derrotados: {jefes_derrotados} / 3\n"
             f"Movimientos: {movimientos}\n"
             f"Turnos: {turnos}\n"
             f"Encuentro enemigo: {probabilidad_enemigo()}%\n"
             f"Caras del dado: {caras_dado()}"
    )
    dibujar_mapa()

def probabilidad_enemigo():
    return max(10, 70 - 10 * (nivel - 1))

def caras_dado():
    return max(2, 7 - nivel)

# --------------------------- Juego ---------------------------

def explorar():
    global vida, energia
    if not juego_iniciado or partida_terminada or victoria:
        return
    visitados[jugador_fila][jugador_columna] = True
    bioma = mundo[jugador_fila][jugador_columna]
    registrar(f"Exploraste el bioma: {bioma}.", VERDE)

    if bioma == "bosque":
        anterior = energia
        energia = min(ENERGIA_MAXIMA, energia + 5)
        if energia > anterior:
            registrar("El bosque recuperó 5 puntos de energía.", VERDE)

    # Evento hostil ocasional durante la exploración
    if random.randint(1, 10) == 1:
        vida = max(0, vida - 5)
        registrar("Una criatura te sorprendió: perdiste 5 de vida.", ROJO)
        comprobar_muerte()
    actualizar_todo()

def combate_enemigo():
    global vida
    if partida_terminada:
        return
    bioma = mundo[jugador_fila][jugador_columna]
    enemigo = NOMBRES_ENEMIGOS[bioma]
    caras = caras_dado()
    respuesta = simpledialog.askinteger(
        "Encuentro: " + enemigo,
        f"¡Apareció un {enemigo}!\n\nAdivina el resultado del dado (1–{caras}).",
        minvalue=1, maxvalue=caras, parent=raiz
    )
    if respuesta is None:
        registrar("Evitaste responder, pero el enemigo atacó.", ROJO)
        dano = 10
    else:
        resultado = random.randint(1, caras)
        if respuesta == resultado:
            registrar(f"¡Acertaste! Derrotaste al {enemigo}.", VERDE)
            actualizar_todo()
            return
        registrar(f"Fallaste: salió {resultado}. Perdiste 10 de vida.", ROJO)
        dano = 10
    vida = max(0, vida - dano)
    comprobar_muerte()
    actualizar_todo()

def combate_jefe(posicion):
    global vida, jefes_derrotados
    resistencia = 2
    registrar("¡Un jefe bloquea tu camino!", ROJO)
    while resistencia > 0 and vida > 0:
        caras = caras_dado()
        respuesta = simpledialog.askinteger(
            "Combate contra jefe",
            f"Jefe: {resistencia} puntos de resistencia\n"
            f"Tu vida: {vida}\n\nAdivina el resultado del dado (1–{caras}).",
            minvalue=1, maxvalue=caras, parent=raiz
        )
        if respuesta is None:
            resultado = random.randint(1, caras)
            registrar(f"Cancelaste el intento. El jefe sacó {resultado}.", ROJO)
            vida = max(0, vida - 15)
        else:
            resultado = random.randint(1, caras)
            if respuesta == resultado:
                resistencia -= 1
                registrar(f"¡Golpe acertado! Resistencia del jefe: {resistencia}.", VERDE)
            else:
                vida = max(0, vida - 15)
                registrar(f"Fallaste: salió {resultado}. Perdiste 15 de vida.", ROJO)
        actualizar_todo()

    if vida <= 0:
        comprobar_muerte()
        return

    if posicion in jefes:
        jefes.remove(posicion)
        jefes_derrotados += 1
    registrar("¡Jefe derrotado! Ganaste experiencia.", VERDE)
    ganar_experiencia()
    if len(jefes) == 0:
        resolver_acertijo()
    actualizar_todo()

def ganar_experiencia():
    global nivel, experiencia
    ganancia = 50 / (2 ** (nivel - 1))
    experiencia += ganancia
    registrar(f"Ganaste {ganancia:g}% de experiencia.", AMARILLO)
    while experiencia >= 100:
        experiencia -= 100
        nivel += 1
        registrar(f"¡Subiste al nivel {nivel}!", VERDE)

def resolver_acertijo():
    global mundo, visitados, jugador_fila, jugador_columna
    global salida_fila, salida_columna, salida_revelada, jefes

    opcion = messagebox.askyesnocancel(
        "El mecanismo antiguo",
        "¡Derrotaste a los tres jefes!\n\n"
        "Elige la transformación del mapa:\n\n"
        "Sí = intercambiar dos renglones\n"
        "No = intercambiar dos columnas\n"
        "Cancelar = calcular la transpuesta",
        parent=raiz
    )

    if opcion is True:
        r1 = random.randrange(TAMANO)
        r2 = (r1 + random.randint(1, TAMANO - 1)) % TAMANO
        mundo[r1], mundo[r2] = mundo[r2], mundo[r1]
        visitados[r1], visitados[r2] = visitados[r2], visitados[r1]
        if jugador_fila == r1:
            jugador_fila = r2
        elif jugador_fila == r2:
            jugador_fila = r1
        if salida_fila == r1:
            salida_fila = r2
        elif salida_fila == r2:
            salida_fila = r1
        jefes = {(r2 if f == r1 else r1 if f == r2 else f, c) for f, c in jefes}
        registrar(f"Transformación aplicada: intercambio de renglones {r1 + 1} y {r2 + 1}.", VERDE)

    elif opcion is False:
        c1 = random.randrange(TAMANO)
        c2 = (c1 + random.randint(1, TAMANO - 1)) % TAMANO
        for f in range(TAMANO):
            mundo[f][c1], mundo[f][c2] = mundo[f][c2], mundo[f][c1]
            visitados[f][c1], visitados[f][c2] = visitados[f][c2], visitados[f][c1]
        if jugador_columna == c1:
            jugador_columna = c2
        elif jugador_columna == c2:
            jugador_columna = c1
        if salida_columna == c1:
            salida_columna = c2
        elif salida_columna == c2:
            salida_columna = c1
        jefes = {(f, c2 if c == c1 else c1 if c == c2 else c) for f, c in jefes}
        registrar(f"Transformación aplicada: intercambio de columnas {c1 + 1} y {c2 + 1}.", VERDE)

    else:
        mundo = [list(fila) for fila in zip(*mundo)]
        visitados = [list(fila) for fila in zip(*visitados)]
        jugador_fila, jugador_columna = jugador_columna, jugador_fila
        salida_fila, salida_columna = salida_columna, salida_fila
        jefes = {(c, f) for f, c in jefes}
        registrar("Transformación aplicada: transpuesta del mapa.", VERDE)

    salida_revelada = True
    for f in range(TAMANO):
        for c in range(TAMANO):
            visitados[f][c] = True
    registrar("¡Mapa revelado! Encuentra la salida amarilla S.", AMARILLO)
    actualizar_todo()

def mover(df, dc):
    global jugador_fila, jugador_columna, energia, movimientos, turnos
    if not juego_iniciado or partida_terminada or victoria:
        return
    nf = jugador_fila + df
    nc = jugador_columna + dc
    if not (0 <= nf < TAMANO and 0 <= nc < TAMANO):
        registrar("No puedes salir de los límites del mundo.", AMARILLO)
        return
    if energia < 10:
        registrar("No tienes energía suficiente. Descansa para recuperarla.", AMARILLO)
        return

    jugador_fila, jugador_columna = nf, nc
    energia -= 10
    movimientos += 1
    turnos += 1
    visitados[nf][nc] = True
    registrar("Te moviste a una nueva zona.")
    pos = (nf, nc)

    if pos in jefes:
        combate_jefe(pos)
    else:
        if random.randint(1, 100) <= probabilidad_enemigo():
            combate_enemigo()

    if vida > 0 and not partida_terminada:
        explorar()
        comprobar_victoria()
    actualizar_todo()

def descansar():
    global vida, energia, salida_fila, salida_columna, visitados, turnos
    if not juego_iniciado or partida_terminada or victoria:
        return
    turnos += 1
    anterior = vida
    vida = min(VIDA_MAXIMA, vida + 30)
    energia = ENERGIA_MAXIMA
    registrar(f"Descansaste: recuperaste {vida - anterior} de vida y toda la energía.", VERDE)

    # Ocultar la exploración anterior, pero conservar el mundo y los jefes vencidos.
    visitados = [[False] * TAMANO for _ in range(TAMANO)]
    visitados[jugador_fila][jugador_columna] = True

    if salida_revelada and random.random() < 0.20:
        anterior_salida = (salida_fila, salida_columna)
        salida_fila, salida_columna = posicion_libre({
            (jugador_fila, jugador_columna), anterior_salida
        })
        registrar("¡La salida cambió de posición! Tendrás que encontrarla de nuevo.", AMARILLO)
    elif salida_revelada:
        registrar("La salida no cambió de posición.")
    if random.randint(1, 100) <= probabilidad_enemigo():
        registrar("Un enemigo interrumpió tu descanso.", ROJO)
        combate_enemigo()
    actualizar_todo()

def comprobar_victoria():
    global victoria, partida_terminada
    if salida_revelada and (jugador_fila, jugador_columna) == (salida_fila, salida_columna):
        victoria = True
        partida_terminada = True
        registrar(f"¡Felicidades, {nombre_jugador}! Escapaste de Aether.", VERDE)
        messagebox.showinfo("Victoria", f"¡Lo lograste, {nombre_jugador}!\nEscapaste de Aether.", parent=raiz)
        actualizar_todo()

def comprobar_muerte():
    global vida, partida_terminada
    if vida <= 0:
        vida = 0
        partida_terminada = True
        registrar("Tu vida llegó a cero. La aventura terminó.", ROJO)
        actualizar_todo()
        if messagebox.askyesno("Fin de la aventura", "Has perdido toda la vida.\n¿Quieres generar un mundo nuevo?", parent=raiz):
            generar_mundo()
        else:
            registrar("Puedes elegir Guardar o Salir desde el menú.", SUAVE)

# --------------------------- Menú y paneles ---------------------------

def seleccionar_seccion(nombre):
    global seccion_actual
    seccion_actual = nombre
    for boton, texto in botones_menu:
        boton.configure(bg=AZUL if texto == nombre else PANEL2)
    if nombre == "Mapa":
        registrar("Mapa principal: ● eres tú, J son jefes y S es la salida.", SUAVE)
    elif nombre == "Movimiento":
        messagebox.showinfo("Movimiento", "Usa W/A/S/D o las flechas del teclado.\nCada movimiento consume 10 de energía.", parent=raiz)
    elif nombre == "Métricas":
        mostrar_metricas()
    elif nombre == "Descansar":
        descansar()
    elif nombre == "Guardar":
        guardar_partida()
    elif nombre == "Cargar":
        cargar_partida()
    elif nombre == "Opciones":
        mostrar_opciones()
    elif nombre == "Salir":
        salir_juego()

def mostrar_metricas():
    exploradas = sum(sum(1 for v in fila if v) for fila in visitados)
    messagebox.showinfo(
        "Métricas de la aventura",
        f"Jugador: {nombre_jugador}\nNivel: {nivel}\nExperiencia: {experiencia:.2f}%\n"
        f"Vida: {vida}/{VIDA_MAXIMA}\nEnergía: {energia}/{ENERGIA_MAXIMA}\n"
        f"Zonas exploradas: {exploradas}/{TAMANO*TAMANO}\n"
        f"Movimientos: {movimientos}\nTurnos: {turnos}\nJefes derrotados: {jefes_derrotados}/3\n"
        f"Probabilidad de enemigo: {probabilidad_enemigo()}%\nCaras del dado: {caras_dado()}",
        parent=raiz
    )

def mostrar_opciones():
    messagebox.showinfo(
        "Opciones",
        "Controles:\nW/A/S/D o flechas: mover\nE: explorar\nR: descansar\nM: métricas\nI: mostrar ayuda\nG: guardar\nL: cargar\nQ: salir\n\n"
        "La aventura usa un mapa de 10 × 10. La salida se revela al derrotar a los tres jefes.",
        parent=raiz
    )

def guardar_partida():
    archivo = filedialog.asksaveasfilename(
        parent=raiz, title="Guardar partida", defaultextension=".json",
        filetypes=[("Partida de Aether", "*.json")]
    )
    if not archivo:
        return
    datos = {
        "nombre": nombre_jugador, "mundo": mundo, "visitados": visitados,
        "jugador_fila": jugador_fila, "jugador_columna": jugador_columna,
        "vida": vida, "energia": energia, "nivel": nivel, "experiencia": experiencia,
        "jefes": [list(pos) for pos in sorted(jefes)], "jefes_derrotados": jefes_derrotados,
        "salida_fila": salida_fila, "salida_columna": salida_columna,
        "salida_revelada": salida_revelada, "movimientos": movimientos, "turnos": turnos,
        "victoria": victoria, "partida_terminada": partida_terminada,
        "version": 1
    }
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        registrar("Partida guardada correctamente.", VERDE)
    except OSError as error:
        messagebox.showerror("Error al guardar", str(error), parent=raiz)

def cargar_partida():
    global nombre_jugador, mundo, visitados, jugador_fila, jugador_columna
    global vida, energia, nivel, experiencia, jefes, jefes_derrotados
    global salida_fila, salida_columna, salida_revelada, movimientos, turnos
    global victoria, partida_terminada, juego_iniciado, eventos

    archivo = filedialog.askopenfilename(
        parent=raiz, title="Cargar partida",
        filetypes=[("Partida de Aether", "*.json"), ("Todos los archivos", "*.*")]
    )
    if not archivo:
        return

    try:
        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, dict):
            raise ValueError("El archivo no es una partida compatible de Aether.")
        es_partida_anterior = "version" not in datos
        if es_partida_anterior:
            datos = dict(datos)
            datos["turnos"] = datos.get("movimientos")
            datos["version"] = 1
        elif type(datos["version"]) is not int or datos["version"] != 1:
            raise ValueError("El archivo no es una partida compatible de Aether.")

        nombre = datos["nombre"]
        nuevo_mundo = datos["mundo"]
        nuevas_visitas = datos["visitados"]
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre) > 24:
            raise ValueError("El nombre del jugador no es válido.")
        if (not isinstance(nuevo_mundo, list) or len(nuevo_mundo) != TAMANO
                or any(not isinstance(fila, list) or len(fila) != TAMANO
                       or any(bioma not in BIOMAS for bioma in fila)
                       for fila in nuevo_mundo)):
            raise ValueError("El mapa guardado no tiene un formato válido.")
        if (not isinstance(nuevas_visitas, list) or len(nuevas_visitas) != TAMANO
                or any(not isinstance(fila, list) or len(fila) != TAMANO
                       or any(type(valor) is not bool for valor in fila)
                       for fila in nuevas_visitas)):
            raise ValueError("El registro de zonas visitadas no es válido.")

        def entero_en_rango(clave, minimo, maximo):
            valor = datos[clave]
            if type(valor) is not int or not minimo <= valor <= maximo:
                raise ValueError(f"El valor '{clave}' no es válido.")
            return valor

        fila_jugador = entero_en_rango("jugador_fila", 0, TAMANO - 1)
        columna_jugador = entero_en_rango("jugador_columna", 0, TAMANO - 1)
        fila_salida = entero_en_rango("salida_fila", 0, TAMANO - 1)
        columna_salida = entero_en_rango("salida_columna", 0, TAMANO - 1)
        nueva_vida = entero_en_rango("vida", 0, VIDA_MAXIMA)
        nueva_energia = entero_en_rango("energia", 0, ENERGIA_MAXIMA)
        nuevo_nivel = entero_en_rango("nivel", 1, 1000000)
        nuevos_movimientos = entero_en_rango("movimientos", 0, 1000000000)
        nuevos_turnos = entero_en_rango("turnos", nuevos_movimientos, 2000000000)
        jefes_derrotados_guardados = entero_en_rango("jefes_derrotados", 0, 3)
        nueva_experiencia = datos["experiencia"]
        if (type(nueva_experiencia) not in (int, float)
                or not 0 <= nueva_experiencia < 100):
            raise ValueError("La experiencia guardada no es válida.")

        posiciones_jefes = datos["jefes"]
        if not isinstance(posiciones_jefes, list) or len(posiciones_jefes) > 3:
            raise ValueError("La lista de jefes no es válida.")
        nuevos_jefes = set()
        for posicion in posiciones_jefes:
            if (not isinstance(posicion, list) or len(posicion) != 2
                    or any(type(coordenada) is not int
                           or not 0 <= coordenada < TAMANO for coordenada in posicion)):
                raise ValueError("Una posición de jefe no es válida.")
            nuevos_jefes.add(tuple(posicion))
        if (len(nuevos_jefes) != len(posiciones_jefes)
                or (fila_jugador, columna_jugador) in nuevos_jefes
                or (fila_salida, columna_salida) in nuevos_jefes
                or jefes_derrotados_guardados != 3 - len(nuevos_jefes)):
            raise ValueError("Las posiciones o el conteo de jefes son inconsistentes.")

        nueva_salida_revelada = datos["salida_revelada"]
        nueva_victoria = datos.get(
            "victoria",
            es_partida_anterior and nueva_salida_revelada
            and (fila_jugador, columna_jugador) == (fila_salida, columna_salida)
            and nueva_vida > 0
        )
        nueva_partida_terminada = datos.get(
            "partida_terminada", nueva_victoria or nueva_vida == 0
        )
        if (type(nueva_salida_revelada) is not bool
                or type(nueva_victoria) is not bool
                or type(nueva_partida_terminada) is not bool):
            raise ValueError("El estado de finalización no es válido.")
        if (nueva_salida_revelada != (len(nuevos_jefes) == 0)
                or (nueva_victoria and (
                    not nueva_partida_terminada or not nueva_salida_revelada
                    or (fila_jugador, columna_jugador) != (fila_salida, columna_salida)))
                or (nueva_partida_terminada and not nueva_victoria and nueva_vida != 0)
                or (not nueva_partida_terminada and nueva_vida == 0)):
            raise ValueError("El estado guardado de la aventura es inconsistente.")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        messagebox.showerror("No se pudo cargar la partida", str(error), parent=raiz)
        return

    nombre_jugador = nombre.strip()
    mundo = nuevo_mundo
    visitados = nuevas_visitas
    jugador_fila, jugador_columna = fila_jugador, columna_jugador
    vida, energia = nueva_vida, nueva_energia
    nivel, experiencia = nuevo_nivel, nueva_experiencia
    jefes, jefes_derrotados = nuevos_jefes, jefes_derrotados_guardados
    salida_fila, salida_columna = fila_salida, columna_salida
    salida_revelada = nueva_salida_revelada
    movimientos = nuevos_movimientos
    turnos = nuevos_turnos
    victoria, partida_terminada = nueva_victoria, nueva_partida_terminada
    juego_iniciado = True
    eventos = deque(maxlen=80)
    registro.delete(0, "end")
    titulo_mundo.config(text=f"El mundo te espera, {nombre_jugador}")
    registrar("Partida cargada correctamente.", VERDE)
    actualizar_todo()
    canvas.focus_set()

def salir_juego():
    if messagebox.askyesno("Salir de Aether", "¿Seguro que quieres salir?", parent=raiz):
        raiz.destroy()

botones_menu = []
opciones_menu = [
    ("▦", "Mapa"),
    ("✥", "Movimiento"),
    ("▥", "Métricas"),
    ("☾", "Descansar"),
    ("▣", "Guardar"),
    ("▤", "Cargar"),
    ("⚙", "Opciones"),
    ("⇥", "Salir"),
]

for icono, texto in opciones_menu:
    b = tk.Button(
        lateral, text=f"  {icono}   {texto}", anchor="w",
        font=FUENTE_BOLD, fg=TEXTO, bg=AZUL if texto == "Mapa" else PANEL2,
        activebackground=AZUL, activeforeground="white", relief="flat",
        padx=10, pady=10, cursor="hand2",
        command=lambda t=texto: seleccionar_seccion(t)
    )
    b.pack(fill="x", padx=9, pady=3)
    botones_menu.append((b, texto))

tk.Frame(lateral, bg=BORDE, height=1).pack(fill="x", padx=10, pady=12)
tk.Label(lateral, text="LEYENDA", font=("Segoe UI", 9, "bold"),
         fg=SUAVE, bg=PANEL).pack(anchor="w", padx=14, pady=(0, 8))

for simbolo, texto, color in [
    ("●", "Jugador", "#1688f8"),
    ("J", "Jefe", "#a72c3b"),
    ("S", "Salida", "#f7c948"),
    ("B", "Bosque", BIOMAS["bosque"]["color"]),
    ("D", "Desierto", BIOMAS["desierto"]["color"]),
    ("N", "Nieve", BIOMAS["nieve"]["color"]),
    ("P", "Pantano", BIOMAS["pantano"]["color"]),
    ("M", "Montaña", BIOMAS["montana"]["color"]),
    ("R", "Pradera", BIOMAS["pradera"]["color"]),
]:
    fila_leyenda = tk.Frame(lateral, bg=PANEL)
    fila_leyenda.pack(fill="x", padx=14, pady=2)
    tk.Label(fila_leyenda, text=simbolo, width=3, fg="white", bg=color,
             font=FUENTE_BOLD).pack(side="left")
    tk.Label(fila_leyenda, text=texto, fg=SUAVE, bg=PANEL, font=FUENTE).pack(side="left", padx=8)

def actualizar_leyenda_inferior():
    for hijo in leyenda.winfo_children():
        hijo.destroy()
    tk.Label(leyenda, text="● Tú", fg="#7fc4ff", bg=PANEL2, font=FUENTE_BOLD, padx=8, pady=7).pack(side="left")
    tk.Label(leyenda, text="J Jefe", fg="#ff929a", bg=PANEL2, font=FUENTE_BOLD, padx=8, pady=7).pack(side="left")
    tk.Label(leyenda, text="S Salida", fg=AMARILLO, bg=PANEL2, font=FUENTE_BOLD, padx=8, pady=7).pack(side="left")
    tk.Label(leyenda, text="Las zonas oscuras aún no se han descubierto", fg=SUAVE, bg=PANEL2, font=FUENTE, padx=8, pady=7).pack(side="right")



def manejar_tecla(evento):
    tecla = evento.keysym.lower()
    if tecla in ("w", "up"):
        mover(-1, 0)
    elif tecla in ("s", "down"):
        mover(1, 0)
    elif tecla in ("a", "left"):
        mover(0, -1)
    elif tecla in ("d", "right"):
        mover(0, 1)
    elif tecla == "e":
        explorar_manual()
    elif tecla == "r":
        descansar()
    elif tecla == "m":
        mostrar_metricas()
    elif tecla == "i":
        mostrar_opciones()
    elif tecla == "g":
        guardar_partida()
    elif tecla == "l":
        cargar_partida()
    elif tecla == "q":
        salir_juego()

raiz.bind("<KeyPress>", manejar_tecla)
canvas.bind("<Configure>", lambda e: dibujar_mapa())

def comenzar():
    global nombre_jugador, juego_iniciado
    nombre = simpledialog.askstring("Bienvenido a Aether", "¿Cómo te llamas, explorador?", parent=raiz)
    if nombre is None or not nombre.strip():
        nombre = "Explorador"
    nombre_jugador = nombre.strip()[:24]
    juego_iniciado = True
    titulo_mundo.config(text=f"El mundo te espera, {nombre_jugador}")
    registrar(f"¡Bienvenido, {nombre_jugador}! Explora, sobrevive y encuentra la salida.", VERDE)
    generar_mundo()
    actualizar_leyenda_inferior()
    canvas.focus_set()

if __name__ == "__main__":
    actualizar_leyenda_inferior()
    raiz.after(250, comenzar)
    raiz.mainloop()
