import sqlite3
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel


class mathplay(MDApp):

    def build(self):
        self.inicializar_db()

        self.sm = MDScreenManager()

        self.login_screen = MDScreen(name="login")
        layout_login = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        self.login_user = MDTextField(hint_text="Usuario")
        self.login_pass = MDTextField(hint_text="Contraseña", password=True)

        layout_login.add_widget(self.login_user)
        layout_login.add_widget(self.login_pass)

        layout_login.add_widget(
            MDRaisedButton(text="Iniciar Sesión", on_release=self.login)
        )
        layout_login.add_widget(
            MDRaisedButton(text="Ir a Registro", on_release=lambda x: self.cambiar("registro"))
        )

        self.login_screen.add_widget(layout_login)
        self.sm.add_widget(self.login_screen)

        self.reg_screen = MDScreen(name="registro")
        layout_reg = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        self.reg_user = MDTextField(hint_text="Nuevo Usuario")
        self.reg_pass = MDTextField(hint_text="Nueva Contraseña", password=True)

        layout_reg.add_widget(self.reg_user)
        layout_reg.add_widget(self.reg_pass)

        layout_reg.add_widget(
            MDRaisedButton(text="Registrarse", on_release=self.registrar)
        )
        layout_reg.add_widget(
            MDRaisedButton(text="Volver", on_release=lambda x: self.cambiar("login"))
        )

        self.reg_screen.add_widget(layout_reg)
        self.sm.add_widget(self.reg_screen)

        self.menu_screen = MDScreen(name="menu")
        layout_menu = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        layout_menu.add_widget(
            MDRaisedButton(text="Cursos", on_release=lambda x: self.cambiar("cursos"))
        )
        layout_menu.add_widget(
            MDRaisedButton(text="Mis cursos", on_release=self.ver_cursos)
        )
        layout_menu.add_widget(
            MDRaisedButton(text="Cerrar sesión", on_release=lambda x: self.cambiar("login"))
        )

        self.menu_screen.add_widget(layout_menu)
        self.sm.add_widget(self.menu_screen)

        self.cursos_screen = MDScreen(name="cursos")
        layout_cursos = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        cursos = ["Suma", "Resta", "Multiplicación", "División"]

        for curso in cursos:
            layout_cursos.add_widget(
                MDRaisedButton(
                    text=curso,
                    on_release=lambda x, c=curso: self.inscribirse(c)
                )
            )

        layout_cursos.add_widget(
            MDRaisedButton(text="Volver", on_release=lambda x: self.cambiar("menu"))
        )

        self.cursos_screen.add_widget(layout_cursos)
        self.sm.add_widget(self.cursos_screen)

        self.mis_cursos_screen = MDScreen(name="mis_cursos")
        self.layout_mis = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        self.mis_cursos_screen.add_widget(self.layout_mis)
        self.sm.add_widget(self.mis_cursos_screen)

        return self.sm

    def inicializar_db(self):
        conn = sqlite3.connect("mathplay.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario_nombre TEXT PRIMARY KEY,
            usuario_contrasena TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cursos (
            curso_id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso_nombre TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS inscripciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            curso TEXT
        )
        """)

        conn.commit()
        conn.close()

    def cambiar(self, pantalla):
        self.sm.current = pantalla

    def registrar(self, instance):
        user = self.reg_user.text
        password = self.reg_pass.text

        conn = sqlite3.connect("mathplay.db")
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO usuarios VALUES (?, ?)", (user, password))
            conn.commit()
            print("Usuario registrado")
        except:
            print("Usuario ya existe")

        conn.close()

    def login(self, instance):
        user = self.login_user.text
        password = self.login_pass.text

        conn = sqlite3.connect("mathplay.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE usuario_nombre=? AND usuario_contrasena=?", (user, password))
        resultado = cursor.fetchone()

        conn.close()

        if resultado:
            self.usuario_actual = user
            print("Login correcto")
            self.cambiar("menu")
        else:
            print("Datos incorrectos")

    def inscribirse(self, curso):
        conn = sqlite3.connect("mathplay.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO inscripciones (usuario, curso) VALUES (?, ?)", (self.usuario_actual, curso))
        conn.commit()
        conn.close()

        print(f"Inscrito en {curso}")

    def ver_cursos(self, instance):
        self.layout_mis.clear_widgets()

        conn = sqlite3.connect("mathplay.db")
        cursor = conn.cursor()

        cursor.execute("SELECT curso FROM inscripciones WHERE usuario=?", (self.usuario_actual,))
        cursos = cursor.fetchall()

        conn.close()

        for c in cursos:
            self.layout_mis.add_widget(MDLabel(text=c[0]))

        self.layout_mis.add_widget(
            MDRaisedButton(text="Volver", on_release=lambda x: self.cambiar("menu"))
        )

        self.cambiar("mis_cursos")


if __name__ == "__main__":
    mathplay().run()