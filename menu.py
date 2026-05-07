from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout


class MyApp(MDApp):
    def build(self):
        screen = Screen()

        # ---------- Barra superior simulada ----------
        toolbar = BoxLayout(
        orientation='horizontal',
        size_hint_y=None,
        height=50,
        padding=10,
        spacing=10,
        pos_hint={"top": 1} 
    )

        python_btn = MDIconButton(
            icon='language-python',
            on_release=lambda x: print("Python presionado")
        )

        title = MDLabel(
            text='Mi aplicación',
            halign='center',
            valign='middle',
        )

        settings_btn = MDIconButton(
            icon='cog',
            on_release=lambda x: print("Configuración presionada")
        )

        menu_btn = MDIconButton(icon='dots-vertical')

        # ---------- Label principal ----------
        self.label = MDLabel(
            text="Selecciona una opción",
            halign="center",
            pos_hint={"center_y": 0.5},
        )

        # ---------- Menú desplegable ----------
        menu = MDDropdownMenu(
            caller=menu_btn,
            items=[
                {
                    "text": "Inicio",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="Inicio": self.menu_callback(menu, x),
                },
                {
                    "text": "Configuración",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="Configuración": self.menu_callback(menu, x),
                },
                {
                    "text": "Acerca de",
                    "viewclass": "OneLineListItem",
                    "on_release": lambda x="Acerca de": self.menu_callback(menu, x),
                },
            ],
            width_mult=3,
        )

        menu_btn.bind(on_release=lambda x: menu.open())

        # ---------- Barra ----------
        toolbar.add_widget(python_btn)
        toolbar.add_widget(title)
        toolbar.add_widget(settings_btn)
        toolbar.add_widget(menu_btn)

        # Agregar al screen
        screen.add_widget(toolbar)
        screen.add_widget(self.label)

        return screen

    # ---------- FUNCIÓN PRINCIPAL ----------
    def menu_callback(self, menu, text):
        self.label.text = f"{text}" 
        print(f"{text}")  
        menu.dismiss()


if __name__ == "__main__":
    MyApp().run()