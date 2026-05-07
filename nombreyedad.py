import sqlite3
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager


def categoria_edad(edad):
    edad = int(edad)
    if edad < 12:
        return "Niño"
    elif edad < 18:
        return "Adolescente"
    else:
        return "Adulto"

def guardar_datos(nombre, edad, categoria):
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()

    cursor.execute("INSERT INTO usuarios (nombre, edad, categoria) VALUES (?, ?, ?)",
                   (nombre, edad, categoria))

    conexion.commit()

    cursor.execute("SELECT * FROM usuarios")
    datos = cursor.fetchall()
    print("DATOS EN LA BASE:")
    for fila in datos:
        print(fila)

    conexion.close()

def crear_bd():
    conexion = sqlite3.connect("usuarios.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        edad INTEGER,
        categoria TEXT
    )
    """)

    conexion.commit()
    conexion.close()



class Pantalla1(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.nombre = MDTextField(
            hint_text="Ingresa tu nombre",
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            size_hint_x=0.8
        )

        self.edad = MDTextField(
            hint_text="Ingresa tu edad",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint_x=0.8
        )

        btn = MDRaisedButton(
            text="Enviar",
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            on_release=self.validar
        )

        self.add_widget(self.nombre)
        self.add_widget(self.edad)
        self.add_widget(btn)

    def validar(self, obj):
        nombre = self.nombre.text
        edad = self.edad.text

        if nombre == "" or not edad.isdigit():
            print("Datos inválidos")
        else:
            cat = categoria_edad(edad)
            guardar_datos(nombre, edad, cat)

            self.manager.get_screen("pantalla2").mostrar(nombre, edad, cat)
            self.manager.current = "pantalla2"



class Pantalla2(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.label = MDLabel(
            text="",
            halign="center",
            pos_hint={"center_y": 0.6}
        )

        btn = MDRaisedButton(
            text="Regresar",
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            on_release=self.regresar
        )

        self.add_widget(self.label)
        self.add_widget(btn)

    def mostrar(self, nombre, edad, categoria):
        self.label.text = f"Hola {nombre}, tienes {edad} años\nEres: {categoria}"

    def regresar(self, obj):
        self.manager.current = "pantalla1"



class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()

        crear_bd()

        sm.add_widget(Pantalla1(name="pantalla1"))
        sm.add_widget(Pantalla2(name="pantalla2"))

        return sm

if __name__ == "__main__":
    MyApp().run()