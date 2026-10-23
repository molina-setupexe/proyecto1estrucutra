import ctypes
import random
import json
import sys
import warnings
from collections import deque
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

def configurar_dpi_windows():
    if sys.platform != "win32":
        return

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    establecer_contexto = getattr(user32, "SetProcessDpiAwarenessContext", None)
    if establecer_contexto is not None:
        establecer_contexto.argtypes = [ctypes.c_void_p]
        establecer_contexto.restype = ctypes.c_bool
        if establecer_contexto(ctypes.c_void_p(-4)):
            return

    try:
        shcore = ctypes.WinDLL("shcore", use_last_error=True)
        establecer_conciencia = shcore.SetProcessDpiAwareness
        establecer_conciencia.argtypes = [ctypes.c_int]
        establecer_conciencia.restype = ctypes.c_long
        if establecer_conciencia(2) == 0:
            return
    except OSError:
        pass

    establecer_sistema = user32.SetProcessDPIAware
    establecer_sistema.argtypes = []
    establecer_sistema.restype = ctypes.c_bool
    if not establecer_sistema():
        warnings.warn(
            "No se pudo habilitar la conciencia de DPI en Windows; "
            "el sistema podría escalar la ventana.",
            RuntimeWarning,
            stacklevel=2,
        )


configurar_dpi_windows()

TAMANO = 10
RADIO_JEFES_SALIDA = 3
CARAS_DADO_ZONA_FACIL = 4
ZONA_FACIL = frozenset(
    (fila, columna)
    for fila in range(TAMANO // 2 - 3, TAMANO // 2)
    for columna in range(TAMANO // 2 - 2, TAMANO // 2 + 2)
)
MINIJEFES_CERCA = 4
MINIJEFES_LEJANOS = 2
EXPERIENCIA_MINIJEFE = 30
CELDA = 62
MARGEN = 18
VIDA_MAXIMA = 100
ENERGIA_MAXIMA = 100

BIOMAS = {
    "bosque":   {"simbolo": "B", "color": "#E0EBDD", "claro": "#C7D9C4", "acento": "#527A5D"},
    "desierto": {"simbolo": "D", "color": "#F3E8D6", "claro": "#E9D6B8", "acento": "#AA7B42"},
    "nieve":    {"simbolo": "N", "color": "#E2EDF0", "claro": "#CCDFE5", "acento": "#648A9A"},
    "pantano":  {"simbolo": "P", "color": "#E5EBDD", "claro": "#D3DEC5", "acento": "#718456"},
    "montana":  {"simbolo": "M", "color": "#E5E7EB", "claro": "#D1D5DC", "acento": "#707887"},
    "pradera":  {"simbolo": "R", "color": "#E9EEDC", "claro": "#D9E4C3", "acento": "#77934E"},
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
minijefes = set()
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
raiz.configure(bg="#F3F5F1")

FUENTE = ("Segoe UI", 10)
FUENTE_BOLD = ("Segoe UI", 10, "bold")
FONDO = "#F3F5F1"
PANEL = "#FFFFFF"
PANEL2 = "#F7F8F5"
BORDE = "#E5E9E2"
TEXTO = "#26352D"
SUAVE = "#78857C"
AZUL = "#527A64"
VERDE = "#568264"
ROJO = "#C66C62"
AMARILLO = "#C7963C"

# Layout principal
contenedor = tk.Frame(raiz, bg=FONDO)
contenedor.pack(fill="both", expand=True, padx=18, pady=16)

barra_superior = tk.Frame(contenedor, bg=FONDO)
barra_superior.pack(fill="x", pady=(0, 16))

marca = tk.Frame(barra_superior, bg=FONDO)
marca.pack(side="left")
tk.Label(marca, text="✳", font=("Segoe UI Symbol", 20),
         fg=AZUL, bg=FONDO).pack(side="left", padx=(2, 9))
tk.Label(marca, text="AETHER", font=("Segoe UI", 19, "bold"),
         fg=TEXTO, bg=FONDO).pack(side="left")
titulo_mundo = tk.Label(barra_superior, text="El mundo te espera",
                        font=("Segoe UI", 11), fg=SUAVE, bg=FONDO)
titulo_mundo.pack(side="left", padx=20)
jugador_label = tk.Label(barra_superior, text="Jugador: —",
                         font=FUENTE_BOLD, fg=TEXTO, bg=FONDO, padx=8)
jugador_label.pack(side="right")

cuerpo = tk.Frame(contenedor, bg=FONDO)
cuerpo.pack(fill="both", expand=True)

# Menú lateral
lateral = tk.Frame(cuerpo, bg=PANEL, width=205)
lateral.grid(row=0, column=0, sticky="ns", padx=(0, 8))
lateral.grid_propagate(False)

tk.Label(lateral, text="EXPLORACIÓN", font=("Segoe UI", 9, "bold"),
         fg=SUAVE, bg=PANEL, pady=17).pack(fill="x")

contenido = tk.Frame(cuerpo, bg=FONDO)
contenido.grid(row=0, column=1, sticky="nsew")

panel_derecho = tk.Frame(cuerpo, bg=PANEL, width=230)
panel_derecho.grid(row=0, column=2, sticky="ns", padx=(8, 0))
panel_derecho.grid_propagate(False)
cuerpo.grid_rowconfigure(0, weight=1)
cuerpo.grid_columnconfigure(1, weight=1)

# Mapa central
marco_mapa = tk.Frame(contenido, bg=PANEL)
marco_mapa.pack(fill="both", expand=True)

encabezado_mapa = tk.Frame(marco_mapa, bg=PANEL)
encabezado_mapa.pack(fill="x", padx=22, pady=(18, 8))
tk.Label(encabezado_mapa, text="Mapa de Aether", font=("Segoe UI", 15, "bold"),
         fg=TEXTO, bg=PANEL).pack(side="left")
estado_mapa = tk.Label(encabezado_mapa, text="Introduce tu nombre para comenzar",
                       font=FUENTE, fg=SUAVE, bg=PANEL)
estado_mapa.pack(side="right")

canvas = tk.Canvas(marco_mapa, bg="#FBFCFA", highlightthickness=0)
canvas.pack(fill="both", expand=True, padx=14, pady=8)

leyenda = tk.Frame(marco_mapa, bg=PANEL)
leyenda.pack(fill="x", padx=18, pady=(4, 12))

# Panel derecho
def titulo_panel(parent, texto):
    tk.Label(parent, text=texto, font=("Segoe UI", 9, "bold"),
             fg=SUAVE, bg=PANEL, anchor="w", padx=16, pady=14).pack(fill="x")

titulo_panel(panel_derecho, "ESTADO DEL PERSONAJE")
estado_frame = tk.Frame(panel_derecho, bg=PANEL)
estado_frame.pack(fill="x", padx=16)

vida_texto = tk.Label(estado_frame, text="Vida  100 / 100", font=FUENTE_BOLD, fg=TEXTO, bg=PANEL, anchor="w")
vida_texto.pack(fill="x", pady=(2, 3))
vida_barra = tk.Canvas(estado_frame, height=8, bg="#EDF0EB", highlightthickness=0)
vida_barra.pack(fill="x", pady=(0, 12))

energia_texto = tk.Label(estado_frame, text="Energía  100 / 100", font=FUENTE_BOLD, fg=TEXTO, bg=PANEL, anchor="w")
energia_texto.pack(fill="x", pady=(2, 3))
energia_barra = tk.Canvas(estado_frame, height=8, bg="#EDF0EB", highlightthickness=0)
energia_barra.pack(fill="x", pady=(0, 12))

nivel_titulo = tk.Label(estado_frame, text="NIVEL 1 · 0%", font=FUENTE_BOLD, fg=AMARILLO, bg=PANEL, anchor="w")
nivel_titulo.pack(fill="x", pady=(4, 3))
xp_barra = tk.Canvas(estado_frame, height=8, bg="#EDF0EB", highlightthickness=0)
xp_barra.pack(fill="x", pady=(0, 8))

tk.Frame(panel_derecho, bg=BORDE, height=1).pack(fill="x", padx=16, pady=8)
titulo_panel(panel_derecho, "MÉTRICAS")
metricas_frame = tk.Frame(panel_derecho, bg=PANEL)
metricas_frame.pack(fill="x", padx=16)
metricas_label = tk.Label(metricas_frame, text="Zonas exploradas: 0\nJefes derrotados: 0 / 3\nMovimientos: 0",
                          font=FUENTE, fg=SUAVE, bg=PANEL, justify="left", anchor="w")
metricas_label.pack(fill="x")

tk.Frame(panel_derecho, bg=BORDE, height=1).pack(fill="x", padx=16, pady=8)
titulo_panel(panel_derecho, "REGISTRO")
registro = tk.Listbox(panel_derecho, height=11, bg="#FFFFFF", fg=TEXTO,
                      selectbackground="#E4EEE7", selectforeground=TEXTO, relief="flat", borderwidth=0,
                      font=("Segoe UI", 9), activestyle="none")
registro.pack(fill="both", expand=True, padx=16, pady=(0, 16))

# Barra inferior
barra_inferior = tk.Frame(contenedor, bg=FONDO)
barra_inferior.pack(fill="x", pady=(12, 0))
mensaje = tk.Label(barra_inferior, text="Bienvenido a Aether.", font=FUENTE,
                   fg=TEXTO, bg=FONDO, anchor="w", padx=2, pady=6)
mensaje.pack(side="left", fill="x", expand=True)
atajos = tk.Label(barra_inferior, text="W A S D mover   ·   E explorar   ·   R descansar   ·   G/L guardar/cargar   ·   Q salir",
                  font=("Segoe UI", 9), fg=SUAVE, bg=FONDO, padx=2)
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

def es_esquina(fila, columna):
    return fila in (0, TAMANO - 1) and columna in (0, TAMANO - 1)

def posiciones_jefes_cerca_salida(fila_salida, columna_salida, excluir, cantidad):
    candidatas = [
        (f, c)
        for f in range(TAMANO)
        for c in range(TAMANO)
        if 0 < abs(f - fila_salida) + abs(c - columna_salida) <= RADIO_JEFES_SALIDA
        and (f, c) not in excluir
    ]
    if len(candidatas) < cantidad:
        raise RuntimeError("No hay suficientes posiciones para colocar a los jefes.")
    return set(random.sample(candidatas, cantidad))

def generar_posiciones_jefes(fila_salida, columna_salida, excluir, cantidad):
    if cantidad == 0:
        return set()
    posiciones_faciles = list(ZONA_FACIL - excluir)
    if not posiciones_faciles:
        raise RuntimeError("No hay posiciones libres en la zona fácil para un jefe.")
    jefe_facil = random.choice(posiciones_faciles)
    restantes = posiciones_jefes_cerca_salida(
        fila_salida, columna_salida, excluir | {jefe_facil}, cantidad - 1
    )
    return restantes | {jefe_facil}

def posiciones_submatriz_salida(fila_salida, columna_salida):
    direccion_fila = 1 if fila_salida == 0 else -1
    direccion_columna = 1 if columna_salida == 0 else -1
    return {
        (fila_salida + direccion_fila * desplazamiento_fila,
         columna_salida + direccion_columna * desplazamiento_columna)
        for desplazamiento_fila in range(3)
        for desplazamiento_columna in range(4)
    }

def generar_minijefes(fila_salida, columna_salida, excluir):
    submatriz = posiciones_submatriz_salida(fila_salida, columna_salida)
    cercanos = [
        posicion for posicion in submatriz
        if posicion not in excluir and posicion != (fila_salida, columna_salida)
    ]
    lejanos = [
        (f, c)
        for f in range(TAMANO)
        for c in range(TAMANO)
        if abs(f - fila_salida) + abs(c - columna_salida) >= 5
        and (f, c) not in excluir
        and (f, c) not in submatriz
    ]
    if len(cercanos) < MINIJEFES_CERCA or len(lejanos) < MINIJEFES_LEJANOS:
        raise RuntimeError("No hay suficientes posiciones para colocar a los minijefes.")
    return (
        set(random.sample(cercanos, MINIJEFES_CERCA))
        | set(random.sample(lejanos, MINIJEFES_LEJANOS))
    )

def generar_mundo():
    global mundo, visitados, jugador_fila, jugador_columna
    global jefes, minijefes, salida_fila, salida_columna
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

    salida_fila, salida_columna = random.choice((
        (0, 0), (0, TAMANO - 1),
        (TAMANO - 1, 0), (TAMANO - 1, TAMANO - 1)
    ))
    jefes = generar_posiciones_jefes(
        salida_fila, salida_columna, {(jugador_fila, jugador_columna)}, 3
    )
    minijefes = generar_minijefes(
        salida_fila, salida_columna,
        jefes | {(jugador_fila, jugador_columna)}
    )
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
    h = max(canvas_barra.winfo_height(), 8)
    canvas_barra.create_rectangle(0, 0, w, h, fill="#EDF0EB", outline="")
    relleno = max(0, min(w, w * valor / maximo))
    if relleno:
        canvas_barra.create_rectangle(0, 0, relleno, h, fill=color, outline="")

def dibujar_icono_bioma(superficie, bioma, centro_x, centro_y, tamano):
    acento = BIOMAS[bioma]["acento"]
    claro = BIOMAS[bioma]["claro"]
    s = max(12, tamano)
    x, y = centro_x, centro_y

    if bioma == "bosque":
        superficie.create_rectangle(x - s * .055, y + s * .05, x + s * .055,
                                    y + s * .43, fill="#8C6749", outline="")
        superficie.create_polygon(
            x, y - s * .48, x - s * .34, y + s * .12, x + s * .34, y + s * .12,
            fill=acento, outline=""
        )
        superficie.create_polygon(
            x, y - s * .12, x - s * .40, y + s * .36, x + s * .40, y + s * .36,
            fill=claro, outline=""
        )
    elif bioma == "desierto":
        superficie.create_oval(x + s * .18, y - s * .42, x + s * .38,
                               y - s * .22, fill="#D7A94E", outline="")
        superficie.create_polygon(
            x - s * .44, y + s * .34, x - s * .05, y - s * .04,
            x + s * .43, y + s * .34, fill=claro, outline=""
        )
        superficie.create_line(x, y + s * .12, x, y - s * .18,
                               fill=acento, width=max(2, int(s * .09)))
        superficie.create_line(x - s * .15, y + s * .03, x - s * .15,
                               y - s * .09, fill=acento, width=max(2, int(s * .07)))
        superficie.create_line(x + s * .15, y + s * .08, x + s * .15,
                               y - s * .08, fill=acento, width=max(2, int(s * .07)))
    elif bioma == "nieve":
        superficie.create_polygon(
            x - s * .46, y + s * .36, x - s * .10, y - s * .36,
            x + s * .12, y + s * .36, fill=acento, outline=""
        )
        superficie.create_polygon(
            x - s * .12, y + s * .36, x + s * .22, y - s * .46,
            x + s * .48, y + s * .36, fill=claro, outline=""
        )
        superficie.create_polygon(
            x - s * .20, y - s * .16, x - s * .10, y - s * .36,
            x + s * .01, y - s * .15, x - s * .10, y - s * .20,
            fill="#FFFFFF", outline=""
        )
        superficie.create_polygon(
            x + s * .08, y - s * .20, x + s * .22, y - s * .46,
            x + s * .36, y - s * .19, x + s * .22, y - s * .25,
            fill="#FFFFFF", outline=""
        )
    elif bioma == "pantano":
        superficie.create_line(x - s * .43, y + s * .28, x + s * .43, y + s * .28,
                               fill=claro, width=max(2, int(s * .08)))
        superficie.create_line(x - s * .36, y + s * .40, x + s * .35, y + s * .40,
                               fill=acento, width=max(1, int(s * .04)))
        for desplazamiento, alto in ((-.24, .28), (.02, .43), (.25, .34)):
            superficie.create_line(x + s * desplazamiento, y + s * .19,
                                   x + s * desplazamiento, y - s * alto,
                                   fill=acento, width=max(2, int(s * .06)))
            superficie.create_oval(
                x + s * (desplazamiento - .09), y - s * (alto + .06),
                x + s * (desplazamiento + .09), y - s * (alto - .04),
                fill=claro, outline=""
            )
    elif bioma == "montana":
        superficie.create_polygon(
            x - s * .48, y + s * .38, x - s * .12, y - s * .32,
            x + s * .16, y + s * .38, fill=acento, outline=""
        )
        superficie.create_polygon(
            x - s * .10, y + s * .38, x + s * .22, y - s * .46,
            x + s * .49, y + s * .38, fill=claro, outline=""
        )
        superficie.create_polygon(
            x + s * .07, y - s * .05, x + s * .22, y - s * .46,
            x + s * .36, y - s * .02, x + s * .22, y - s * .12,
            fill="#FFFFFF", outline=""
        )
    else:
        for desplazamiento, alto in ((-.28, .33), (-.08, .45), (.14, .36), (.32, .27)):
            superficie.create_line(
                x + s * desplazamiento, y + s * .38,
                x + s * (desplazamiento - .08), y - s * alto,
                fill=acento, width=max(2, int(s * .055))
            )
            superficie.create_oval(
                x + s * (desplazamiento - .19), y - s * (alto - .04),
                x + s * (desplazamiento - .04), y - s * (alto - .14),
                fill=claro, outline=""
            )

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

    separacion = max(3, celda * .055)
    for f in range(TAMANO):
        for c in range(TAMANO):
            x1 = x0 + c * celda
            y1 = y0 + f * celda
            x2 = x1 + celda
            y2 = y1 + celda
            pos = (f, c)

            if not visitados[f][c]:
                color = "#F0F2EF"
                simbolo = ""
            else:
                bioma = mundo[f][c]
                color = BIOMAS[bioma]["color"]
                simbolo = bioma

            if pos == (salida_fila, salida_columna):
                color = "#F4E8C9"
                simbolo = "salida"

            if pos in jefes:
                color = "#F4DFDC"
                simbolo = "jefe"

            if pos in minijefes:
                color = "#EAE1F2"
                simbolo = "minijefe"

            if pos == (jugador_fila, jugador_columna):
                color = "#DFECE4"
                simbolo = "jugador"

            canvas.create_rectangle(
                x1 + separacion, y1 + separacion, x2 - separacion, y2 - separacion,
                fill=color, outline=""
            )
            centro_x, centro_y = (x1 + x2) / 2, (y1 + y2) / 2
            if simbolo in BIOMAS:
                dibujar_icono_bioma(canvas, simbolo, centro_x, centro_y, celda * .54)
            elif simbolo == "jefe":
                radio = celda * .22
                canvas.create_oval(centro_x - radio, centro_y - radio,
                                   centro_x + radio, centro_y + radio,
                                   fill="#B75F57", outline="")
                canvas.create_text(centro_x, centro_y, text="J", fill="#FFFFFF",
                                   font=("Segoe UI", max(9, int(celda * .22)), "bold"))
            elif simbolo == "minijefe":
                radio = celda * .20
                canvas.create_oval(centro_x - radio, centro_y - radio,
                                   centro_x + radio, centro_y + radio,
                                   fill="#8663A8", outline="")
                canvas.create_text(centro_x, centro_y, text="m", fill="#FFFFFF",
                                   font=("Segoe UI", max(9, int(celda * .2)), "bold"))
            elif simbolo == "salida":
                radio = celda * .24
                canvas.create_oval(centro_x - radio, centro_y - radio,
                                   centro_x + radio, centro_y + radio,
                                   fill="#D5A948", outline="")
                canvas.create_text(centro_x, centro_y, text="S", fill="#FFFFFF",
                                   font=("Segoe UI", max(9, int(celda * .2)), "bold"))
            elif simbolo == "jugador":
                radio = celda * .22
                canvas.create_oval(centro_x - radio, centro_y - radio,
                                   centro_x + radio, centro_y + radio,
                                   fill=AZUL, outline="#FFFFFF", width=2)
                canvas.create_oval(centro_x - radio * .26, centro_y - radio * .26,
                                   centro_x + radio * .26, centro_y + radio * .26,
                                   fill="#FFFFFF", outline="")
            else:
                radio = max(1.5, celda * .025)
                for desplazamiento in (-1, 0, 1):
                    cx = centro_x + desplazamiento * radio * 3
                    canvas.create_oval(cx - radio, centro_y - radio,
                                       cx + radio, centro_y + radio,
                                       fill="#D8DDD7", outline="")

    fila_min = min(fila for fila, _ in ZONA_FACIL)
    fila_max = max(fila for fila, _ in ZONA_FACIL) + 1
    columna_min = min(columna for _, columna in ZONA_FACIL)
    columna_max = max(columna for _, columna in ZONA_FACIL) + 1
    canvas.create_rectangle(
        x0 + columna_min * celda + separacion / 2,
        y0 + fila_min * celda + separacion / 2,
        x0 + columna_max * celda - separacion / 2,
        y0 + fila_max * celda - separacion / 2,
        outline="#568264", width=3, dash=(7, 3)
    )
    zona_jefe = (
        "Jefe en zona fácil: dado 1–4"
        if (jugador_fila, jugador_columna) in ZONA_FACIL
        else "Zona fácil superior marcada: jefes usan dado 1–4"
    )
    estado = "Salida abierta" if salida_revelada else "Salida visible · derrota a los jefes para abrirla"
    estado_mapa.config(
        text=f"{estado}  |  {zona_jefe}  |  Jefes: {len(jefes)}"
             f"  ·  Minijefes: {len(minijefes)}"
    )

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
             f"Minijefes restantes: {len(minijefes)}\n"
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

def caras_dado_jefe(posicion):
    if posicion in ZONA_FACIL:
        return CARAS_DADO_ZONA_FACIL
    return caras_dado()

def probabilidad_minijefe(fila, columna):
    if (fila, columna) in posiciones_submatriz_salida(salida_fila, salida_columna):
        return 30
    return 5

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
    resistencia = 3
    en_zona_facil = posicion in ZONA_FACIL
    if en_zona_facil:
        registrar("¡Jefe en la zona fácil! El dado va del 1 al 4.", VERDE)
    else:
        registrar("¡Un jefe bloquea tu camino!", ROJO)
    while resistencia > 0 and vida > 0:
        caras = caras_dado_jefe(posicion)
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
    resolver_acertijo()
    actualizar_todo()

def combate_minijefe(posicion):
    global vida
    resistencia = 2
    registrar("¡Apareció un minijefe! Vencerlo te dará experiencia para subir de nivel.", "#8663A8")
    while resistencia > 0 and vida > 0:
        caras = caras_dado()
        respuesta = simpledialog.askinteger(
            "Combate contra minijefe",
            f"Minijefe: {resistencia} puntos de resistencia\n"
            f"Tu vida: {vida}\n\nAdivina el resultado del dado (1–{caras}).",
            minvalue=1, maxvalue=caras, parent=raiz
        )
        resultado = random.randint(1, caras)
        if respuesta == resultado:
            resistencia -= 1
            registrar(f"¡Golpe acertado! Resistencia del minijefe: {resistencia}.", VERDE)
        else:
            vida = max(0, vida - 10)
            registrar(f"Fallaste: salió {resultado}. Perdiste 10 de vida.", ROJO)
        actualizar_todo()

    if vida <= 0:
        comprobar_muerte()
        return

    minijefes.discard(posicion)
    registrar(
        f"¡Minijefe derrotado! Ganaste {EXPERIENCIA_MINIJEFE}% de experiencia.",
        "#8663A8"
    )
    ganar_experiencia(EXPERIENCIA_MINIJEFE)
    actualizar_todo()

def ganar_experiencia(ganancia=75):
    global nivel, experiencia
    experiencia += ganancia
    registrar(f"Ganaste {ganancia:g}% de experiencia.", AMARILLO)
    while experiencia >= 100:
        experiencia -= 100
        nivel += 1
        registrar(f"¡Subiste al nivel {nivel}!", VERDE)

def solicitar_operacion_matriz():
    dialogo = tk.Toplevel(raiz)
    dialogo.title("Transformar matriz del mapa")
    dialogo.transient(raiz)
    dialogo.resizable(False, False)
    dialogo.configure(bg=PANEL)
    operacion = {"valor": None}

    tk.Label(
        dialogo,
        text="El jefe cayó. Elige una operación para reorganizar los biomas:",
        font=FUENTE_BOLD, fg=TEXTO, bg=PANEL, wraplength=460,
        justify="left", padx=20, pady=18
    ).pack(fill="x")

    opciones = tk.Frame(dialogo, bg=PANEL)
    opciones.pack(fill="x", padx=14, pady=(0, 14))

    def elegir(valor):
        operacion["valor"] = valor
        dialogo.destroy()

    for texto, valor in (
        ("Cambiar dos filas", "filas"),
        ("Cambiar dos columnas", "columnas"),
        ("Reorganizar mapa\n(transpuesta)", "transpuesta"),
    ):
        tk.Button(
            opciones, text=texto, font=FUENTE_BOLD, fg=TEXTO, bg="#E8F0EA",
            activebackground="#DCE8DF", relief="flat", padx=10, pady=10,
            cursor="hand2", command=lambda v=valor: elegir(v)
        ).pack(side="left", expand=True, fill="x", padx=4)

    dialogo.protocol("WM_DELETE_WINDOW", lambda: None)
    dialogo.bind("1", lambda _evento: elegir("filas"))
    dialogo.bind("2", lambda _evento: elegir("columnas"))
    dialogo.bind("3", lambda _evento: elegir("transpuesta"))
    dialogo.update_idletasks()
    x = raiz.winfo_rootx() + (raiz.winfo_width() - dialogo.winfo_width()) // 2
    y = raiz.winfo_rooty() + (raiz.winfo_height() - dialogo.winfo_height()) // 2
    dialogo.geometry(f"+{max(0, x)}+{max(0, y)}")
    dialogo.grab_set()
    dialogo.focus_set()
    raiz.wait_window(dialogo)
    return operacion["valor"]

def resolver_acertijo():
    global mundo, visitados, jugador_fila, jugador_columna
    global salida_fila, salida_columna, salida_revelada, jefes, minijefes

    opcion = solicitar_operacion_matriz()

    if opcion == "filas":
        filas_disponibles = [f for f in range(TAMANO) if f != salida_fila]
        r1, r2 = random.sample(filas_disponibles, 2)
        mundo[r1], mundo[r2] = mundo[r2], mundo[r1]
        visitados[r1], visitados[r2] = visitados[r2], visitados[r1]
        if jugador_fila == r1:
            jugador_fila = r2
        elif jugador_fila == r2:
            jugador_fila = r1
        jefes = {
            (r2 if f == r1 else r1 if f == r2 else f, c)
            for f, c in jefes
        }
        minijefes = {
            (r2 if f == r1 else r1 if f == r2 else f, c)
            for f, c in minijefes
        }
        registrar(f"Transformación aplicada: intercambio de renglones {r1 + 1} y {r2 + 1}.", VERDE)

    elif opcion == "columnas":
        columnas_disponibles = [c for c in range(TAMANO) if c != salida_columna]
        c1, c2 = random.sample(columnas_disponibles, 2)
        for f in range(TAMANO):
            mundo[f][c1], mundo[f][c2] = mundo[f][c2], mundo[f][c1]
            visitados[f][c1], visitados[f][c2] = visitados[f][c2], visitados[f][c1]
        if jugador_columna == c1:
            jugador_columna = c2
        elif jugador_columna == c2:
            jugador_columna = c1
        jefes = {
            (f, c2 if c == c1 else c1 if c == c2 else c)
            for f, c in jefes
        }
        minijefes = {
            (f, c2 if c == c1 else c1 if c == c2 else c)
            for f, c in minijefes
        }
        registrar(f"Transformación aplicada: intercambio de columnas {c1 + 1} y {c2 + 1}.", VERDE)

    elif opcion == "transpuesta":
        mundo = [list(fila) for fila in zip(*mundo)]
        visitados = [list(fila) for fila in zip(*visitados)]
        jugador_fila, jugador_columna = jugador_columna, jugador_fila
        salida_fila, salida_columna = salida_columna, salida_fila
        jefes = {(c, f) for f, c in jefes}
        minijefes = {(c, f) for f, c in minijefes}
        registrar("Transformación aplicada: transpuesta del mapa.", VERDE)

    else:
        raise ValueError("La operación matricial seleccionada no es válida.")

    jefes = generar_posiciones_jefes(
        salida_fila, salida_columna,
        jefes | minijefes | {(jugador_fila, jugador_columna)},
        len(jefes)
    )
    for f in range(TAMANO):
        for c in range(TAMANO):
            visitados[f][c] = True
    salida_revelada = not jefes
    if jefes:
        registrar(
            f"Los {len(jefes)} jefes restantes cambiaron de posición y están cerca de la salida.",
            AMARILLO
        )
    else:
        registrar("¡Derrotaste a todos los jefes! La salida de la esquina está abierta.", AMARILLO)
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
    elif pos in minijefes:
        combate_minijefe(pos)
    elif (pos != (salida_fila, salida_columna)
            and random.randint(1, 100) <= probabilidad_minijefe(nf, nc)):
        registrar("La zona atrae a un minijefe errante.", "#8663A8")
        combate_minijefe(pos)
    else:
        if random.randint(1, 100) <= probabilidad_enemigo():
            combate_enemigo()

    if vida > 0 and not partida_terminada:
        explorar()
        if not salida_revelada and (jugador_fila, jugador_columna) == (salida_fila, salida_columna):
            registrar("Encontraste la salida, pero está sellada. Derrota a los tres jefes.", AMARILLO)
        if vida > 0 and not partida_terminada and comprobar_victoria():
            return
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
        esquinas_disponibles = [
            (f, c)
            for f, c in (
                (0, 0), (0, TAMANO - 1),
                (TAMANO - 1, 0), (TAMANO - 1, TAMANO - 1)
            )
            if (f, c) not in (
                jefes | minijefes
                | {(jugador_fila, jugador_columna), anterior_salida}
            )
        ]
        if esquinas_disponibles:
            salida_fila, salida_columna = random.choice(esquinas_disponibles)
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
        raiz.destroy()
        return True
    return False

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
        boton.configure(
            bg="#E8F0EA" if texto == nombre else PANEL,
            fg=AZUL if texto == nombre else TEXTO
        )
    if nombre == "Mapa":
        registrar("Mapa: ● eres tú, J son jefes, m son minijefes y S es la salida.", SUAVE)
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
        f"Movimientos: {movimientos}\nTurnos: {turnos}\n"
        f"Jefes derrotados: {jefes_derrotados}/3\nMinijefes restantes: {len(minijefes)}\n"
        f"Probabilidad de enemigo: {probabilidad_enemigo()}%\nCaras del dado: {caras_dado()}",
        parent=raiz
    )

def mostrar_opciones():
    messagebox.showinfo(
        "Opciones",
        "Controles:\nW/A/S/D o flechas: mover\nE: explorar\nR: descansar\nM: métricas\nI: mostrar ayuda\nG: guardar\nL: cargar\nQ: salir\n\n"
        "Mapa de 10 × 10. Hay 4 minijefes señalizados en una submatriz de 3 × 4 junto "
        "a la salida y 2 minijefes remotos para farmear. También pueden aparecer minijefes "
        "errantes: 30% de probabilidad en la submatriz y 5% fuera de ella. Cada minijefe "
        "tiene 2 puntos de resistencia y otorga experiencia; subir de nivel facilita los "
        "dados y reduce los encuentros normales. "
        "La salida aparece en una esquina y los jefes principales se agrupan cerca. "
        "La zona marcada arriba del centro usa siempre un dado de jefe del 1 al 4. "
        "Al vencer cada jefe debes cambiar dos filas, cambiar dos columnas o transponer "
        "la matriz de biomas; queda un jefe en la zona fácil y los demás se reubican cerca de la salida. "
        "La salida se abre al derrotar a los tres.",
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
        "minijefes": [list(pos) for pos in sorted(minijefes)],
        "salida_fila": salida_fila, "salida_columna": salida_columna,
        "salida_revelada": salida_revelada, "movimientos": movimientos, "turnos": turnos,
        "victoria": victoria, "partida_terminada": partida_terminada,
        "version": 4
    }
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        registrar("Partida guardada correctamente.", VERDE)
    except OSError as error:
        messagebox.showerror("Error al guardar", str(error), parent=raiz)

def cargar_partida():
    global nombre_jugador, mundo, visitados, jugador_fila, jugador_columna
    global vida, energia, nivel, experiencia, jefes, minijefes, jefes_derrotados
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
        version_guardada = datos["version"]
        if type(version_guardada) is not int or version_guardada not in (1, 2, 3, 4):
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

        nuevos_minijefes = set()
        if version_guardada >= 3:
            posiciones_minijefes = datos["minijefes"]
            if (not isinstance(posiciones_minijefes, list)
                    or len(posiciones_minijefes) > MINIJEFES_CERCA + MINIJEFES_LEJANOS):
                raise ValueError("La lista de minijefes no es válida.")
            for posicion in posiciones_minijefes:
                if (not isinstance(posicion, list) or len(posicion) != 2
                        or any(type(coordenada) is not int
                               or not 0 <= coordenada < TAMANO for coordenada in posicion)):
                    raise ValueError("Una posición de minijefe no es válida.")
                nuevos_minijefes.add(tuple(posicion))
            if (len(nuevos_minijefes) != len(posiciones_minijefes)
                    or nuevos_minijefes & nuevos_jefes
                    or (fila_jugador, columna_jugador) in nuevos_minijefes
                    or (fila_salida, columna_salida) in nuevos_minijefes):
                raise ValueError("Las posiciones de los minijefes son inconsistentes.")

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
        if version_guardada == 1:
            esquinas = (
                (0, 0), (0, TAMANO - 1),
                (TAMANO - 1, 0), (TAMANO - 1, TAMANO - 1)
            )
            if nueva_victoria:
                if not es_esquina(fila_jugador, columna_jugador):
                    fila_jugador, columna_jugador = min(
                        esquinas,
                        key=lambda pos: abs(pos[0] - fila_jugador)
                        + abs(pos[1] - columna_jugador)
                    )
                fila_salida, columna_salida = fila_jugador, columna_jugador
            elif (not es_esquina(fila_salida, columna_salida)
                    or (fila_jugador, columna_jugador) == (fila_salida, columna_salida)):
                opciones_salida = [
                    pos for pos in esquinas if pos != (fila_jugador, columna_jugador)
                ]
                fila_salida, columna_salida = random.choice(opciones_salida)

            if nuevos_jefes and any(
                not 1 <= abs(f - fila_salida) + abs(c - columna_salida) <= RADIO_JEFES_SALIDA
                or (f, c) == (fila_jugador, columna_jugador)
                for f, c in nuevos_jefes
            ):
                nuevos_jefes = posiciones_jefes_cerca_salida(
                    fila_salida, columna_salida,
                    {(fila_jugador, columna_jugador)}, len(nuevos_jefes)
                )
        if (nueva_salida_revelada != (len(nuevos_jefes) == 0)
                or not es_esquina(fila_salida, columna_salida)
                or (version_guardada < 4 and any(
                    not 1 <= abs(f - fila_salida) + abs(c - columna_salida) <= RADIO_JEFES_SALIDA
                    or (f, c) == (fila_jugador, columna_jugador)
                    for f, c in nuevos_jefes
                ))
                or (version_guardada >= 4 and (
                    len(nuevos_jefes & ZONA_FACIL) != (1 if nuevos_jefes else 0)
                    or any(
                        (f, c) not in ZONA_FACIL
                        and not 1 <= abs(f - fila_salida) + abs(c - columna_salida) <= RADIO_JEFES_SALIDA
                        for f, c in nuevos_jefes
                    )
                ))
                or (nueva_victoria and (
                    not nueva_partida_terminada or not nueva_salida_revelada
                    or (fila_jugador, columna_jugador) != (fila_salida, columna_salida)))
                or (nueva_partida_terminada and not nueva_victoria and nueva_vida != 0)
                or (not nueva_partida_terminada and nueva_vida == 0)):
            raise ValueError("El estado guardado de la aventura es inconsistente.")
        if version_guardada < 3:
            nuevos_minijefes = generar_minijefes(
                fila_salida, columna_salida,
                nuevos_jefes | {(fila_jugador, columna_jugador)}
            )
        if version_guardada < 4:
            nuevos_jefes = generar_posiciones_jefes(
                fila_salida, columna_salida,
                nuevos_jefes | nuevos_minijefes | {(fila_jugador, columna_jugador)},
                len(nuevos_jefes)
            )
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        messagebox.showerror("No se pudo cargar la partida", str(error), parent=raiz)
        return

    nombre_jugador = nombre.strip()
    mundo = nuevo_mundo
    visitados = nuevas_visitas
    jugador_fila, jugador_columna = fila_jugador, columna_jugador
    vida, energia = nueva_vida, nueva_energia
    nivel, experiencia = nuevo_nivel, nueva_experiencia
    jefes, minijefes = nuevos_jefes, nuevos_minijefes
    jefes_derrotados = jefes_derrotados_guardados
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
    ("⌖", "Mapa"),
    ("↗", "Movimiento"),
    ("◷", "Métricas"),
    ("☾", "Descansar"),
    ("↓", "Guardar"),
    ("↑", "Cargar"),
    ("⚙", "Opciones"),
    ("↗", "Salir"),
]

for icono, texto in opciones_menu:
    b = tk.Button(
        lateral, text=f"{icono}    {texto}", anchor="w",
        font=FUENTE_BOLD, fg=AZUL if texto == "Mapa" else TEXTO,
        bg="#E8F0EA" if texto == "Mapa" else PANEL,
        activebackground="#EEF3EF", activeforeground=TEXTO, relief="flat",
        padx=12, pady=7, cursor="hand2", bd=0,
        command=lambda t=texto: seleccionar_seccion(t)
    )
    b.pack(fill="x", padx=9, pady=2)
    b.bind(
        "<Enter>",
        lambda evento, boton=b, nombre=texto: boton.configure(
            bg="#E8F0EA" if nombre == seccion_actual else PANEL2
        )
    )
    b.bind(
        "<Leave>",
        lambda evento, boton=b, nombre=texto: boton.configure(
            bg="#E8F0EA" if nombre == seccion_actual else PANEL
        )
    )
    botones_menu.append((b, texto))

tk.Frame(lateral, bg=BORDE, height=1).pack(fill="x", padx=14, pady=14)
tk.Label(lateral, text="BIOMAS", font=("Segoe UI", 9, "bold"),
         fg=SUAVE, bg=PANEL).pack(anchor="w", padx=17, pady=(0, 8))

for bioma, texto in [
    ("bosque", "Bosque"),
    ("desierto", "Desierto"),
    ("nieve", "Nieve"),
    ("pantano", "Pantano"),
    ("montana", "Montaña"),
    ("pradera", "Pradera"),
]:
    fila_leyenda = tk.Frame(lateral, bg=PANEL)
    fila_leyenda.pack(fill="x", padx=15, pady=2)
    icono_bioma = tk.Canvas(fila_leyenda, width=24, height=24, bg=PANEL2,
                            highlightthickness=0)
    icono_bioma.pack(side="left")
    dibujar_icono_bioma(icono_bioma, bioma, 12, 12, 16)
    tk.Label(fila_leyenda, text=texto, fg=TEXTO, bg=PANEL,
             font=("Segoe UI", 9)).pack(side="left", padx=9)

def actualizar_leyenda_inferior():
    for hijo in leyenda.winfo_children():
        hijo.destroy()
    tk.Label(leyenda, text="● Tú", fg=AZUL, bg=PANEL, font=FUENTE_BOLD,
             padx=5, pady=7).pack(side="left")
    tk.Label(leyenda, text="● Jefe", fg=ROJO, bg=PANEL, font=FUENTE_BOLD,
             padx=5, pady=7).pack(side="left")
    tk.Label(leyenda, text="● Minijefe", fg="#8663A8", bg=PANEL,
             font=FUENTE_BOLD, padx=5, pady=7).pack(side="left")
    tk.Label(leyenda, text="● Salida", fg=AMARILLO, bg=PANEL, font=FUENTE_BOLD,
             padx=5, pady=7).pack(side="left")
    tk.Label(leyenda, text="Zona fácil superior: jefe 1–4 · 4 minijefes cerca · 2 remotos",
             fg=SUAVE, bg=PANEL,
             font=("Segoe UI", 9), padx=5, pady=7).pack(side="right")



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
