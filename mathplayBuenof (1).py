import sqlite3
import random as rd
from datetime import datetime

from kivy.lang import Builder
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor

import os
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

from kivy.app import App

def _w():
    return Window.width

def pad_h():
    w = _w()
    if w < 400:   return dp(18)
    elif w < 700: return dp(28)
    else:          return dp(60)

def pad_v():
    h = Window.height
    if h < 600:   return dp(24)
    elif h < 900: return dp(48)
    else:          return dp(72)

def btn_height():
    return dp(44) if Window.height < 650 else dp(52)

def field_height():
    return dp(48) if Window.height < 650 else dp(56)

def font_titulo():
    return sp(22) if _w() < 400 else sp(28)

def font_boton():
    return sp(13) if _w() < 400 else sp(15)


C_VERDE       = get_color_from_hex("#16a34a")
C_VERDE_CLARO = get_color_from_hex("#C7F6D7")
C_VERDE_TEXTO = get_color_from_hex("#14532d")
C_AMBAR       = get_color_from_hex("#F0A820")
C_NARANJA     = get_color_from_hex("#E08020")
C_BLANCO      = get_color_from_hex("#ffffff")


Builder.load_string("""
#:import get_color_from_hex kivy.utils.get_color_from_hex

<MDScreen>:
    canvas.before:
        Color:
            rgba: get_color_from_hex("#f0fdf4")
        Rectangle:
            pos: self.pos
            size: self.size

<MDScrollView>:
    bar_width: 0
    do_scroll_x: False
""")


def titulo(texto):
    return MDLabel(
        text=texto,
        theme_text_color="Custom",
        text_color=C_VERDE_TEXTO,
        font_style="H5",
        bold=True,
        halign="center",
        size_hint_y=None,
        height=dp(52),
        font_size=font_titulo(),
    )


def campo(hint, password=False):
    return MDTextField(
        hint_text=hint,
        password=password,
        mode="rectangle",
        size_hint_y=None,
        height=field_height(),
        line_color_focus=C_VERDE,
        hint_text_color_focus=C_VERDE,
        font_size=font_boton(),
    )


def boton_primario(texto, callback):
    btn = MDFlatButton(
        text=texto,
        md_bg_color=C_VERDE_CLARO,
        theme_text_color="Custom",
        text_color=C_VERDE_TEXTO,
        size_hint=(1, None),
        height=btn_height(),
        font_size=font_boton(),
    )
    btn.bind(on_release=callback)
    return btn


def boton_secundario(texto, callback):
    btn = MDRaisedButton(
        text=texto,
        theme_text_color="Custom",
        md_bg_color=C_AMBAR,
        size_hint=(1, None),
        height=btn_height(),
        elevation=2,
        font_size=font_boton(),
    )
    btn.bind(on_release=callback)
    return btn


def boton_terciario(texto, callback):
    btn = MDFlatButton(
        text=texto,
        md_bg_color=C_NARANJA,
        theme_text_color="Custom",
        text_color=C_BLANCO,
        size_hint=(1, None),
        height=btn_height(),
        font_size=font_boton(),
    )
    btn.bind(on_release=callback)
    return btn


def boton_outline(texto, callback):
    btn = MDRaisedButton(
        text=texto,
        md_bg_color=C_VERDE_TEXTO,
        theme_text_color="Custom",
        text_color=C_BLANCO,
        size_hint=(1, None),
        height=btn_height(),
        font_size=font_boton(),
    )
    btn.bind(on_release=callback)
    return btn


def card_contenedor():
    c = MDCard(
        orientation="vertical",
        md_bg_color=(0, 0, 0, 0),
        elevation=0,
        padding=dp(20),
        spacing=dp(12),
        radius=[16, 16, 16, 16],
        size_hint_y=None,
    )
    c.bind(minimum_height=c.setter("height"))
    return c


def pantalla_scroll(screen):
    scroll = MDScrollView(size_hint=(1, 1))
    inner = MDBoxLayout(
        orientation="vertical",
        size_hint_y=None,
        spacing=dp(16),
    )
    inner.bind(minimum_height=inner.setter("height"))
    scroll.add_widget(inner)
    screen.add_widget(scroll)
    return scroll, inner


def spacer(h=16):
    return MDLabel(size_hint_y=None, height=dp(h))


def label_texto(texto, alto=None, halign="center"):
    lbl = MDLabel(
        text=texto,
        halign=halign,
        valign="top",
        text_size=(Window.width - dp(40), None),
        size_hint_y=None,
    )
    if alto:
        lbl.height = dp(alto)
    else:
        lbl.bind(texture_size=lambda inst, val: setattr(inst, "height", val[1] + dp(16)))
    return lbl


def generar_preguntas_suma(nivel):
    """
    Suma: 10 preguntas con múltiples opciones.
    Nivel 1-5:  números pequeños (0-10)
    Nivel 6-10: números medianos (0-50)
    Nivel 11-15: números grandes (0-200)
    """
    preguntas = []
    for _ in range(10):
        if nivel <= 5:
            n1 = rd.randint(1, 9 + nivel)
            n2 = rd.randint(0, 9 + nivel)
        elif nivel <= 10:
            n1 = rd.randint(10, 25 + nivel * 2)
            n2 = rd.randint(5,  20 + nivel * 2)
        else:
            n1 = rd.randint(50, 100 + nivel * 5)
            n2 = rd.randint(20,  80 + nivel * 5)

        resp = n1 + n2
        distractores = _distractores(resp, 2, rango=max(5, resp // 5))
        opciones = _mezclar(resp, distractores)
        preguntas.append((f"{n1} + {n2}", resp, opciones))
    return preguntas


def generar_preguntas_resta(nivel):
    """
    Resta: resultado siempre >= 0.
    Nivel 1-5:  números pequeños
    Nivel 6-10: números medianos
    Nivel 11-15: números grandes
    """
    preguntas = []
    for _ in range(10):
        if nivel <= 5:
            n1 = rd.randint(nivel, 10 + nivel)
            n2 = rd.randint(0, n1)
        elif nivel <= 10:
            n1 = rd.randint(20, 50 + nivel * 2)
            n2 = rd.randint(5, n1)
        else:
            n1 = rd.randint(100, 200 + nivel * 5)
            n2 = rd.randint(10, n1)

        resp = n1 - n2
        distractores = _distractores(resp, 2, rango=max(5, resp // 5 + 2))
        opciones = _mezclar(resp, distractores)
        preguntas.append((f"{n1} - {n2}", resp, opciones))
    return preguntas


def generar_preguntas_multiplicacion(nivel):
    """
    Multiplicación progresiva.
    Nivel 1-5:  tablas 1-5
    Nivel 6-10: tablas 1-10
    Nivel 11-15: tablas 1-15
    """
    preguntas = []
    for _ in range(10):
        if nivel <= 5:
            n1 = rd.randint(1, 4 + nivel)
            n2 = rd.randint(1, 4 + nivel)
        elif nivel <= 10:
            n1 = rd.randint(2, 10)
            n2 = rd.randint(2, 10)
        else:
            n1 = rd.randint(3, 15)
            n2 = rd.randint(3, 15)

        resp = n1 * n2
        distractores = _distractores(resp, 2, rango=max(5, resp // 4 + 2))
        opciones = _mezclar(resp, distractores)
        preguntas.append((f"{n1} x {n2}", resp, opciones))
    return preguntas


def generar_preguntas_division(nivel):
    """
    División exacta (sin decimales).
    Nivel 1-5:  divisores 1-5
    Nivel 6-10: divisores 1-10
    Nivel 11-15: divisores 1-15
    """
    preguntas = []
    for _ in range(10):
        if nivel <= 5:
            divisor   = rd.randint(1, 4 + nivel)
            cociente  = rd.randint(1, 5 + nivel)
        elif nivel <= 10:
            divisor   = rd.randint(2, 10)
            cociente  = rd.randint(2, 12)
        else:
            divisor   = rd.randint(3, 15)
            cociente  = rd.randint(3, 20)

        dividendo = divisor * cociente
        distractores = _distractores(cociente, 2, rango=max(3, cociente // 2 + 2))
        opciones = _mezclar(cociente, distractores)
        preguntas.append((f"{dividendo} ÷ {divisor}", cociente, opciones))
    return preguntas


def _distractores(correcta, cantidad, rango=5):
    """Genera opciones incorrectas cercanas a la correcta."""
    vistos = {correcta}
    resultado = []
    intentos = 0
    while len(resultado) < cantidad and intentos < 200:
        candidato = correcta + rd.randint(-rango, rango)
        if candidato not in vistos and candidato >= 0:
            vistos.add(candidato)
            resultado.append(candidato)
        intentos += 1
    # Relleno de seguridad si el rango es muy estrecho
    extra = 1
    while len(resultado) < cantidad:
        candidato = correcta + extra
        if candidato not in vistos:
            resultado.append(candidato)
            vistos.add(candidato)
        extra += 1
    return resultado


def _mezclar(correcta, distractores):
    opciones = [correcta] + distractores
    rd.shuffle(opciones)
    return opciones



INTRODUCCIONES = {
    "Suma": {
        1: (
            "INTRODUCCIÓN A LA SUMA\n\n"
            "La suma sirve para juntar o agregar cantidades.\n\n"
            "¿Cómo se suma?\n"
            "1. Escribe los números uno debajo del otro,\n"
            "   alineando las unidades con unidades y\n"
            "   las decenas con decenas.\n\n"
            "2. Empieza siempre desde la derecha (unidades).\n\n"
            "3. Suma columna por columna.\n\n"
            "4. Si la suma de una columna es >= 10,\n"
            "   escribe el dígito de las unidades\n"
            "   y 'llevas' 1 a la siguiente columna.\n\n"
            "Ejemplo:\n"
            "  27 + 15\n"
            "  Unidades: 7+5=12 → escribes 2, llevas 1\n"
            "  Decenas:  2+1+1(llevada)=4\n"
            "  Resultado: 42\n\n"
            "En los niveles 1 al 5 los números son pequeños.\n"
            "¡Tómate tu tiempo!"
        ),
        6: (
            "SUMA — NIVEL VETERANO\n\n"
            "Ahora los números serán más grandes (hasta dos dígitos).\n\n"
            "Recuerda el proceso de llevar:\n"
            "  38 + 47\n"
            "  Unidades: 8+7=15 → escribes 5, llevas 1\n"
            "  Decenas:  3+4+1=8\n"
            "  Resultado: 85\n\n"
            "Consejo:\n"
            "  Redondea uno de los números al 10 más cercano,\n"
            "  suma, luego ajusta.\n"
            "  Ejemplo: 38+47 → 40+47=87 → 87-2=85\n\n"
            "¡Aplica lo aprendido!"
        ),
        11: (
            "SUMA — NIVEL EXPERTO\n\n"
            "Los números ahora pueden superar el 100.\n\n"
            "Ejemplo:\n"
            "  156 + 278\n"
            "  Unidades: 6+8=14 → escribes 4, llevas 1\n"
            "  Decenas:  5+7+1=13 → escribes 3, llevas 1\n"
            "  Centenas: 1+2+1=4\n"
            "  Resultado: 434\n\n"
            "Estrategia experta:\n"
            "  Descompón: 156+278 = (150+270)+(6+8) = 420+14 = 434\n\n"
            "¡Pon a prueba tus habilidades!"
        ),
    },

    "Resta": {
        1: (
            "INTRODUCCIÓN A LA RESTA\n\n"
            "La resta sirve para quitar o comparar cantidades.\n\n"
            "¿Cómo se resta?\n"
            "1. Escribe los números alineados (el mayor arriba).\n"
            "2. Empieza por las unidades (derecha).\n"
            "3. Si el dígito de arriba es menor que el de abajo,\n"
            "   pide prestado 1 a la columna siguiente.\n\n"
            "Ejemplo sencillo:\n"
            "  9 - 4 = 5\n\n"
            "Ejemplo con préstamo:\n"
            "  32 - 17\n"
            "  Unidades: 2 < 7, pides prestado → 12-7=5\n"
            "  Decenas:  3-1(prestado)-1=1\n"
            "  Resultado: 15\n\n"
            "En los niveles 1 al 5 no hay negativos.\n"
            "El número de arriba siempre será mayor o igual."
        ),
        6: (
            "RESTA — NIVEL VETERANO\n\n"
            "Los números son más grandes (hasta 2 dígitos).\n\n"
            "Ejemplo con préstamo en decenas:\n"
            "  73 - 46\n"
            "  Unidades: 3<6, pides prestado → 13-6=7\n"
            "  Decenas:  7-1-4=2\n"
            "  Resultado: 27\n\n"
            "Truco mental:\n"
            "  73-46 → 73-50=23 → 23+4=27\n"
            "  (Redondeamos 46 a 50 y ajustamos)"
        ),
        11: (
            "RESTA — NIVEL EXPERTO\n\n"
            "Números grandes, múltiples préstamos.\n\n"
            "Ejemplo:\n"
            "  504 - 267\n"
            "  Unidades: 4<7, pides al 0 de decenas,\n"
            "            pero también hay que pedir a centenas.\n"
            "  504 → la decena se convierte en 9\n"
            "        y la unidad en 14.\n"
            "  14-7=7, 9-6=3, 4-2=2\n"
            "  Resultado: 237\n\n"
            "Verifica: 267+237=504 ✓"
        ),
    },

    "Multiplicacion": {
        1: (
            "INTRODUCCIÓN A LA MULTIPLICACIÓN\n\n"
            "La multiplicación es una suma repetida.\n"
            "  3 x 4 = 3+3+3+3 = 12\n\n"
            "Tablas básicas que debes memorizar:\n"
            "  x1: cualquier número x 1 es sí mismo.\n"
            "  x2: doble del número.\n"
            "  x5: termina en 0 o 5.\n"
            "  x10: agrega un 0 al final.\n\n"
            "Ejemplo:\n"
            "  4 x 3\n"
            "  = 4+4+4 = 12\n\n"
            "Empieza con las tablas del 1 al 5."
        ),
        6: (
            "MULTIPLICACIÓN — NIVEL VETERANO\n\n"
            "Tablas del 1 al 10.\n\n"
            "Multiplicación por columnas:\n"
            "  23 x 4\n"
            "  Unidades: 3x4=12 → escribes 2, llevas 1\n"
            "  Decenas:  2x4=8 + 1(llevada)=9\n"
            "  Resultado: 92\n\n"
            "Truco: 23x4 = 20x4 + 3x4 = 80+12 = 92"
        ),
        11: (
            "MULTIPLICACIÓN — NIVEL EXPERTO\n\n"
            "Tablas hasta el 15 y productos de 2 dígitos.\n\n"
            "Ejemplo:\n"
            "  13 x 12\n"
            "  = 13x10 + 13x2\n"
            "  = 130 + 26\n"
            "  = 156\n\n"
            "Método FOIL mental:\n"
            "  (10+3)(10+2) = 100+20+30+6 = 156\n\n"
            "¡Combina estrategias!"
        ),
    },

    "Division": {
        1: (
            "INTRODUCCIÓN A LA DIVISIÓN\n\n"
            "La división reparte una cantidad en grupos iguales.\n"
            "  12 ÷ 3 = 4  (12 repartido en 3 grupos = 4 c/u)\n\n"
            "Partes de la división:\n"
            "  Dividendo ÷ Divisor = Cociente\n\n"
            "Pasos (división larga):\n"
            "  1. ¿Cuántas veces cabe el divisor en el dividendo?\n"
            "  2. Multiplica y resta.\n"
            "  3. Baja el siguiente dígito y repite.\n\n"
            "Ejemplo:\n"
            "  8 ÷ 2 = 4  (2x4=8 ✓)\n\n"
            "En los niveles 1-5 solo divisiones exactas sin resto."
        ),
        6: (
            "DIVISIÓN — NIVEL VETERANO\n\n"
            "Divisiones con dividendos más grandes.\n\n"
            "Ejemplo:\n"
            "  96 ÷ 8\n"
            "  ¿8 cabe en 9? Sí, 1 vez. 8x1=8. 9-8=1.\n"
            "  Baja el 6 → 16. ¿8 cabe en 16? 2 veces.\n"
            "  8x2=16. 16-16=0.\n"
            "  Resultado: 12\n\n"
            "Comprobación: 8x12=96 ✓"
        ),
        11: (
            "DIVISIÓN — NIVEL EXPERTO\n\n"
            "Dividendos de 3 dígitos.\n\n"
            "Ejemplo:\n"
            "  312 ÷ 12\n"
            "  ¿12 cabe en 31? Sí, 2 veces. 12x2=24. 31-24=7.\n"
            "  Baja el 2 → 72. ¿12 cabe en 72? 6 veces.\n"
            "  12x6=72. 72-72=0.\n"
            "  Resultado: 26\n\n"
            "Comprobación: 12x26=312 ✓\n\n"
            "Todas las divisiones son exactas (sin decimales)."
        ),
    },
}




GENERADORES = {
    "Suma":          generar_preguntas_suma,
    "Resta":         generar_preguntas_resta,
    "Multiplicacion": generar_preguntas_multiplicacion,
    "Division":      generar_preguntas_division,
}

CURSOS_LISTA = ["Suma", "Resta", "Multiplicacion", "Division"]


class MathplayApp(MDApp):

    
    usuario_actual  = ""
    curso_actual    = ""
    nivel_actual    = 1


    _preguntas      = []
    _indice         = 0
    _correctas      = 0
    _errores        = []


    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue     = "700"
        self.theme_cls.accent_palette  = "Amber"
        self.theme_cls.theme_style     = "Light"

        self.inicializar_db()

        self.sm = MDScreenManager()

        self._construir_login()
        self._construir_registro()
        self._construir_menu()
        self._construir_cursos()
        self._construir_mis_cursos()
        self._construir_pantalla_curso()   # pantalla reutilizable

        return self.sm

    def _construir_login(self):
        screen = MDScreen(name="login")
        _, inner = pantalla_scroll(screen)
        inner.padding = [pad_h(), pad_v(), pad_h(), dp(24)]

        inner.add_widget(titulo("Mathplay"))
        inner.add_widget(spacer(20))

        card = card_contenedor()
        self.login_user = campo("Usuario")
        self.login_pass = campo("Contraseña", password=True)
        card.add_widget(self.login_user)
        card.add_widget(spacer(4))
        card.add_widget(self.login_pass)
        card.add_widget(spacer(4))
        card.add_widget(boton_primario("Iniciar Sesión", self.login))
        card.add_widget(boton_outline("Crear cuenta", lambda x: self.cambiar("registro")))
        inner.add_widget(card)

        self.sm.add_widget(screen)

    def _construir_registro(self):
        screen = MDScreen(name="registro")
        _, inner = pantalla_scroll(screen)
        inner.padding = [pad_h(), pad_v(), pad_h(), dp(24)]

        inner.add_widget(titulo("Nueva Cuenta"))
        inner.add_widget(spacer(20))

        card = card_contenedor()
        self.reg_user = campo("Nuevo Usuario")
        self.reg_pass = campo("Nueva Contraseña", password=True)
        card.add_widget(self.reg_user)
        card.add_widget(spacer(4))
        card.add_widget(self.reg_pass)
        card.add_widget(spacer(4))
        card.add_widget(boton_primario("Registrarse", self.registrar))
        card.add_widget(boton_outline("Volver", lambda x: self.cambiar("login")))
        inner.add_widget(card)

        self.sm.add_widget(screen)

    def _construir_menu(self):
        screen = MDScreen(name="menu")
        _, inner = pantalla_scroll(screen)
        inner.padding = [pad_h(), pad_v(), pad_h(), dp(24)]

        inner.add_widget(titulo("Mathplay"))
        inner.add_widget(spacer(20))

        card = card_contenedor()
        card.add_widget(boton_terciario("Cursos",     lambda x: self.cambiar("cursos")))
        card.add_widget(boton_secundario("Mis cursos", self.abrir_mis_cursos))
        card.add_widget(boton_outline("Cerrar sesión", lambda x: self.cambiar("login")))
        inner.add_widget(card)

        self.sm.add_widget(screen)

    def _construir_cursos(self):
        screen = MDScreen(name="cursos")
        _, inner = pantalla_scroll(screen)
        inner.padding = [pad_h(), pad_v(), pad_h(), dp(24)]

        inner.add_widget(titulo("Elige tu curso"))
        inner.add_widget(spacer(20))

        card = card_contenedor()
        for curso in CURSOS_LISTA:
            card.add_widget(
                boton_primario(curso, lambda x, c=curso: self.inscribirse(c))
            )
        card.add_widget(boton_outline("Volver", lambda x: self.cambiar("menu")))
        inner.add_widget(card)

        self.sm.add_widget(screen)

    def _construir_mis_cursos(self):
        screen = MDScreen(name="mis_cursos")
        _, self._inner_mis = pantalla_scroll(screen)
        self._inner_mis.padding = [pad_h(), pad_v(), pad_h(), dp(24)]

        self._inner_mis.add_widget(titulo("Mis Cursos"))
        self._inner_mis.add_widget(spacer(20))

        self._layout_mis = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
        )
        self._layout_mis.bind(minimum_height=self._layout_mis.setter("height"))
        self._inner_mis.add_widget(self._layout_mis)

        self.sm.add_widget(screen)

    def _construir_pantalla_curso(self):
        """
        Pantalla genérica reutilizable para mostrar teoría,
        preguntas y resultados de cualquier curso/nivel.
        """
        screen = MDScreen(name="pantalla_curso")
        _, self._inner_curso = pantalla_scroll(screen)
        self._inner_curso.padding = [pad_h(), pad_v(), pad_h(), dp(24)]

        self._layout_curso = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(12),
        )
        self._layout_curso.bind(minimum_height=self._layout_curso.setter("height"))
        self._inner_curso.add_widget(self._layout_curso)

        self.sm.add_widget(screen)


    def inicializar_db(self):
        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                usuario_nombre     TEXT PRIMARY KEY,
                usuario_contrasena TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS inscripciones (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                curso   TEXT,
                UNIQUE(usuario, curso)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS progreso (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario      TEXT,
                curso        TEXT,
                nivel        INTEGER,
                intento      INTEGER,
                calificacion INTEGER,
                estrellas    INTEGER,
                aprobado     INTEGER,
                fecha        TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS nivel_actual (
                usuario TEXT,
                curso   TEXT,
                nivel   INTEGER DEFAULT 1,
                PRIMARY KEY (usuario, curso)
            )
        """)

        conn.commit()
        conn.close()


    def registrar(self, *args):
        user = self.reg_user.text.strip()
        pwd  = self.reg_pass.text.strip()

        if not user or not pwd:
            print("Campos vacíos")
            return

        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        try:
            cur.execute("INSERT INTO usuarios VALUES (?, ?)", (user, pwd))
            conn.commit()
            print("Usuario registrado:", user)
            self.cambiar("login")
        except sqlite3.IntegrityError:
            print("El usuario ya existe:", user)
        finally:
            conn.close()

    def login(self, *args):
        user = self.login_user.text.strip()
        pwd  = self.login_pass.text.strip()

        if not user or not pwd:
            print("Campos vacíos")
            return

        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        cur.execute(
            "SELECT * FROM usuarios WHERE usuario_nombre=? AND usuario_contrasena=?",
            (user, pwd),
        )
        resultado = cur.fetchone()
        conn.close()

        if resultado:
            self.usuario_actual = user
            self.cambiar("menu")
        else:
            print("Datos incorrectos")


    def inscribirse(self, curso):
        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO inscripciones (usuario, curso) VALUES (?, ?)",
                (self.usuario_actual, curso),
            )
            # Crear registro de nivel_actual si no existe
            cur.execute(
                "INSERT OR IGNORE INTO nivel_actual (usuario, curso, nivel) VALUES (?, ?, 1)",
                (self.usuario_actual, curso),
            )
            conn.commit()
            print(f"Inscrito en {curso}")
        except sqlite3.IntegrityError:
            print(f"Ya inscrito en {curso}")
        finally:
            conn.close()


    def abrir_mis_cursos(self, *args):
        self._layout_mis.clear_widgets()

        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        cur.execute(
            "SELECT curso FROM inscripciones WHERE usuario=?",
            (self.usuario_actual,),
        )
        cursos = cur.fetchall()
        conn.close()

        if not cursos:
            self._layout_mis.add_widget(
                label_texto("No estás inscrito en ningún curso.\nVe a Cursos para inscribirte.", 80)
            )
        else:
            for (nombre,) in cursos:
                nivel = self._obtener_nivel(nombre)
                etapa = self._etapa_texto(nivel)
                btn   = boton_primario(
                    f"{nombre}  |  Nivel {nivel}/15  [{etapa}]",
                    lambda x, c=nombre: self.entrar_curso(c),
                )
                self._layout_mis.add_widget(btn)

        self._layout_mis.add_widget(spacer(8))
        self._layout_mis.add_widget(
            boton_outline("Volver", lambda x: self.cambiar("menu"))
        )
        self.cambiar("mis_cursos")

    def _obtener_nivel(self, curso):
        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        cur.execute(
            "SELECT nivel FROM nivel_actual WHERE usuario=? AND curso=?",
            (self.usuario_actual, curso),
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
        # Si no existe, creamos con nivel 1
        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO nivel_actual (usuario, curso, nivel) VALUES (?, ?, 1)",
            (self.usuario_actual, curso),
        )
        conn.commit()
        conn.close()
        return 1

    def _etapa_texto(self, nivel):
        if nivel <= 5:   return "Principiante"
        elif nivel <= 10: return "Veterano"
        else:             return "Experto"


    def entrar_curso(self, curso):
        self.curso_actual = curso
        self.nivel_actual = self._obtener_nivel(curso)
        self._mostrar_intro_si_corresponde()

    def _mostrar_intro_si_corresponde(self):
        """Muestra introducción en niveles 1, 6 y 11."""
        if self.nivel_actual in (1, 6, 11):
            self._mostrar_intro()
        else:
            self._iniciar_nivel()

    def _mostrar_intro(self):
        lc = self._layout_curso
        lc.clear_widgets()

        nivel_intro = self.nivel_actual  # 1, 6 o 11
        texto = INTRODUCCIONES.get(self.curso_actual, {}).get(nivel_intro, "")

        lc.add_widget(titulo(f"Curso de {self.curso_actual}"))
        lc.add_widget(spacer(10))
        lc.add_widget(label_texto(texto))
        lc.add_widget(spacer(12))
        lc.add_widget(
            boton_primario(
                f"Comenzar Nivel {self.nivel_actual}",
                lambda x: self._iniciar_nivel(),
            )
        )
        lc.add_widget(
            boton_outline("Volver", lambda x: self.cambiar("mis_cursos"))
        )
        self.cambiar("pantalla_curso")


    def _iniciar_nivel(self):
        generador      = GENERADORES[self.curso_actual]
        self._preguntas = generador(self.nivel_actual)
        self._indice    = 0
        self._correctas = 0
        self._errores   = []
        self._mostrar_pregunta()

    def _mostrar_pregunta(self):
        lc = self._layout_curso
        lc.clear_widgets()

        texto, correcta, opciones = self._preguntas[self._indice]
        etapa = self._etapa_texto(self.nivel_actual)

        lc.add_widget(
            label_texto(
                f"Curso: {self.curso_actual}  |  Nivel {self.nivel_actual}/15  [{etapa}]\n"
                f"Pregunta {self._indice + 1}/10\n\n"
                f"¿Cuánto es {texto}?",
                alto=160,
            )
        )

        for op in opciones:
            lc.add_widget(
                boton_primario(
                    str(op),
                    lambda x, r=op: self._validar_respuesta(r),
                )
            )
        self.cambiar("pantalla_curso")

    def _validar_respuesta(self, respuesta):
        texto, correcta, opciones = self._preguntas[self._indice]

        if respuesta == correcta:
            self._correctas += 1
        else:
            self._errores.append((texto, respuesta, correcta))

        self._indice += 1

        if self._indice < 10:
            self._mostrar_pregunta()
        else:
            self._finalizar_nivel()


    def _finalizar_nivel(self):
        nota = self._correctas

        if nota == 10:   estrellas = 3
        elif nota >= 8:  estrellas = 2
        elif nota >= 6:  estrellas = 1
        else:            estrellas = 0

        aprobado = nota >= 8

        # Guardar progreso
        self._guardar_progreso(nota, estrellas, aprobado)

        # Si aprobó, subir nivel (máximo 15)
        if aprobado and self.nivel_actual < 15:
            nuevo_nivel = self.nivel_actual + 1
            self._actualizar_nivel(nuevo_nivel)
        # Si llegó a nivel 5, 10 o 15 y aprobó → certificado disponible
        nivel_cert = self.nivel_actual if aprobado else None

        lc = self._layout_curso
        lc.clear_widgets()

        etapa = self._etapa_texto(self.nivel_actual)
        stars = "★" * estrellas + "☆" * (3 - estrellas)

        msg = (
            f"Resultado: {nota}/10\n"
            f"Estrellas: {stars}\n\n"
            f"Nivel {self.nivel_actual}/15 — {etapa}\n"
        )
        if aprobado:
            if self.nivel_actual < 15:
                msg += f"\n¡Aprobaste! Avanzas al nivel {self.nivel_actual + 1}."
            else:
                msg += "\n¡Felicidades! Completaste todos los niveles."
        else:
            msg += f"\nNecesitas 8 o más para avanzar. ¡Inténtalo de nuevo!"

        lc.add_widget(label_texto(msg, alto=200))

        # Botón reintentar
        lc.add_widget(
            boton_primario("Reintentar nivel", lambda x: self._iniciar_nivel())
        )

        # Botón siguiente nivel si aprobó y no es el último
        if aprobado and self.nivel_actual < 15:
            sig = self.nivel_actual + 1
            lc.add_widget(
                boton_secundario(
                    f"Ir al nivel {sig}",
                    lambda x: self._ir_siguiente_nivel(),
                )
            )

        # Certificado en niveles de corte
        if aprobado and self.nivel_actual in (5, 10, 15):
            cert_etapa = {5: "Principiante", 10: "Veterano", 15: "Experto"}[self.nivel_actual]
            lc.add_widget(
                boton_secundario(
                    f"Generar Certificado {cert_etapa}",
                    lambda x, e=cert_etapa: self._generar_certificado(nota, e),
                )
            )

        lc.add_widget(boton_outline("Volver", lambda x: self.cambiar("mis_cursos")))

        # Mostrar errores
        if self._errores:
            txt = "Errores cometidos:\n\n"
            for preg, tu_resp, corr in self._errores:
                txt += f"  {preg}\n  Tu respuesta: {tu_resp}  |  Correcta: {corr}\n\n"
            lc.add_widget(label_texto(txt))

        self.cambiar("pantalla_curso")

    def _ir_siguiente_nivel(self):
        # nivel_actual ya fue incrementado en DB; recargar
        self.nivel_actual = self._obtener_nivel(self.curso_actual)
        self._mostrar_intro_si_corresponde()

    def _guardar_progreso(self, nota, estrellas, aprobado):
        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM progreso WHERE usuario=? AND curso=? AND nivel=?",
            (self.usuario_actual, self.curso_actual, self.nivel_actual),
        )
        intento = cur.fetchone()[0] + 1

        cur.execute("""
            INSERT INTO progreso
            (usuario, curso, nivel, intento, calificacion, estrellas, aprobado, fecha)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.usuario_actual,
            self.curso_actual,
            self.nivel_actual,
            intento,
            nota,
            estrellas,
            1 if aprobado else 0,
            datetime.now().strftime("%d/%m/%Y %H:%M"),
        ))

        conn.commit()
        conn.close()

    def _actualizar_nivel(self, nuevo_nivel):
        conn = sqlite3.connect("mathplay.db")
        cur  = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO nivel_actual (usuario, curso, nivel) VALUES (?, ?, ?)",
            (self.usuario_actual, self.curso_actual, nuevo_nivel),
        )
        conn.commit()
        conn.close()

    def _generar_certificado(self, nota, etapa):
        nombre_archivo = (
            f"certificado_{self.usuario_actual}_{self.curso_actual}_{etapa}.pdf"
        )
        nombre_archivo = nombre_archivo.replace(" ", "_")

        # ── Paleta de colores ──────────────────────────────────────────────
        VERDE_BOSQUE  = HexColor("#2E7D32")
        VERDE_MENTA   = HexColor("#6CC17A")
        CAFE_BUHO     = HexColor("#D2691E")
        AMARILLO_SOL  = HexColor("#F5C842")
        VERDE_PALIDO  = HexColor("#E8F5E9")
        LIMA_CLARO    = HexColor("#9CCC65")
        BLANCO        = HexColor("#FFFFFF")

        # ── Página horizontal ─────────────────────────────────────────────
        ancho, alto = landscape(letter)   # ~792 × 612 pts
        c = rl_canvas.Canvas(nombre_archivo, pagesize=landscape(letter))
        cx = ancho / 2                    # centro horizontal

        # ── Fondo degradado simulado con rectángulos ───────────────────────
        c.setFillColor(VERDE_PALIDO)
        c.rect(0, 0, ancho, alto, fill=1, stroke=0)

        # Banda superior (Verde Bosque)
        c.setFillColor(VERDE_BOSQUE)
        c.rect(0, alto - 90, ancho, 90, fill=1, stroke=0)

        # Banda inferior (Verde Menta)
        c.setFillColor(VERDE_MENTA)
        c.rect(0, 0, ancho, 55, fill=1, stroke=0)

        # Acento lateral izquierdo (Café Búho)
        c.setFillColor(CAFE_BUHO)
        c.rect(0, 0, 18, alto, fill=1, stroke=0)

        # Acento lateral derecho (Lima Claro)
        c.setFillColor(LIMA_CLARO)
        c.rect(ancho - 18, 0, 18, alto, fill=1, stroke=0)

        # Rectángulo interior decorativo (borde doble)
        c.setStrokeColor(VERDE_BOSQUE)
        c.setLineWidth(3)
        c.rect(38, 68, ancho - 76, alto - 140, fill=0, stroke=1)
        c.setStrokeColor(AMARILLO_SOL)
        c.setLineWidth(1.5)
        c.rect(44, 74, ancho - 88, alto - 152, fill=0, stroke=1)

        # ── Estrellas decorativas en esquinas ─────────────────────────────
        def estrella(cx_s, cy_s, r=10):
            import math
            puntos = []
            for i in range(5):
                ang_ext = math.radians(90 + i * 72)
                ang_int = math.radians(90 + i * 72 + 36)
                puntos.append((cx_s + r * math.cos(ang_ext), cy_s + r * math.sin(ang_ext)))
                puntos.append((cx_s + r * 0.4 * math.cos(ang_int), cy_s + r * 0.4 * math.sin(ang_int)))
            p = c.beginPath()
            p.moveTo(*puntos[0])
            for pt in puntos[1:]:
                p.lineTo(*pt)
            p.close()
            c.drawPath(p, fill=1, stroke=0)

        c.setFillColor(AMARILLO_SOL)
        for sx, sy in [(70, alto - 105), (ancho - 70, alto - 105),
                       (70, 90), (ancho - 70, 90)]:
            estrella(sx, sy, 12)

        # ── Título en banda superior ───────────────────────────────────────
        c.setFillColor(BLANCO)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(cx, alto - 58, "CERTIFICADO DE LOGRO")

        # Subtítulo debajo de la banda
        c.setFont("Helvetica-BoldOblique", 13)
        c.setFillColor(VERDE_BOSQUE)
        c.drawCentredString(cx, alto - 110, "✦  Mathplay Academy  ✦")

        # Línea doble decorativa
        c.setStrokeColor(CAFE_BUHO)
        c.setLineWidth(2)
        c.line(100, alto - 122, ancho - 100, alto - 122)
        c.setStrokeColor(AMARILLO_SOL)
        c.setLineWidth(0.8)
        c.line(100, alto - 127, ancho - 100, alto - 127)

        # ── Cuerpo del certificado ─────────────────────────────────────────
        c.setFont("Helvetica", 13)
        c.setFillColor(HexColor("#333333"))
        c.drawCentredString(cx, alto - 168, "Este certificado acredita que:")

        # Nombre del usuario (destacado)
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(VERDE_BOSQUE)
        c.drawCentredString(cx, alto - 215, self.usuario_actual)

        # Línea bajo el nombre
        nombre_ancho = c.stringWidth(self.usuario_actual, "Helvetica-Bold", 28)
        c.setStrokeColor(CAFE_BUHO)
        c.setLineWidth(1.5)
        c.line(cx - nombre_ancho / 2, alto - 222, cx + nombre_ancho / 2, alto - 222)

        # Texto descriptivo
        c.setFont("Helvetica", 14)
        c.setFillColor(HexColor("#222222"))
        c.drawCentredString(
            cx, alto - 262,
            f"ha completado satisfactoriamente el nivel  {etapa.upper()}"
        )
        c.drawCentredString(
            cx, alto - 288,
            f"del curso de  {self.curso_actual}"
        )

        # ── Insignia de calificación ───────────────────────────────────────
        # Círculo Amarillo Sol
        c.setFillColor(AMARILLO_SOL)
        c.circle(cx, alto - 358, 40, fill=1, stroke=0)
        c.setStrokeColor(CAFE_BUHO)
        c.setLineWidth(2.5)
        c.circle(cx, alto - 358, 40, fill=0, stroke=1)

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(VERDE_BOSQUE)
        c.drawCentredString(cx, alto - 352, f"{nota}/10")
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#444444"))
        c.drawCentredString(cx, alto - 368, "Calificación")

        # Estrellas de calificación
        if nota == 10:   estrellas_n = 3
        elif nota >= 8:  estrellas_n = 2
        else:            estrellas_n = 1
        c.setFillColor(AMARILLO_SOL)
        for i in range(estrellas_n):
            estrella(cx - 30 + i * 30, alto - 412, 9)
        c.setFillColor(HexColor("#CCCCCC"))
        for i in range(estrellas_n, 3):
            estrella(cx - 30 + i * 30, alto - 412, 9)

        # ── Fecha ──────────────────────────────────────────────────────────
        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor("#555555"))
        fecha = datetime.now().strftime("%d de %B de %Y")
        c.drawCentredString(cx, alto - 442, f"Fecha de emisión: {fecha}")

    
        # Sello circular central en banda inferior
        c.setFillColor(VERDE_BOSQUE)
        c.circle(cx, 55, 28, fill=1, stroke=0)
        c.setFillColor(AMARILLO_SOL)
        c.circle(cx, 55, 28, fill=0, stroke=1)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(BLANCO)
        c.drawCentredString(cx, 58, "MATHPLAY")
        c.drawCentredString(cx, 48, "✓ OFICIAL")

        c.save()

        # Confirmación en pantalla
        lc = self._layout_curso
        lc.clear_widgets()
        lc.add_widget(titulo("Certificado Generado"))
        lc.add_widget(spacer(10))
        lc.add_widget(
            label_texto(
                f"Archivo guardado como:\n{nombre_archivo}\n\n"
                f"Curso: {self.curso_actual}\n"
                f"Nivel: {etapa}\n"
                f"Usuario: {self.usuario_actual}",
                alto=200,
            )
        )
        lc.add_widget(boton_outline("Volver", lambda x: self.cambiar("mis_cursos")))


    def cambiar(self, pantalla):
        self.sm.current = pantalla



if __name__ == "__main__":
    MathplayApp().run()