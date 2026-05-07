from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import ScreenManager


class Screen1(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name_input = MDTextField(
            hint_text="Escribe tu nombre",
            pos_hint={"center_x": 0.5, "center_y": 0.6},
            size_hint_x=0.7
        )

        btn = MDRaisedButton(
            text="Ir a la siguiente pantalla",
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            on_release=self.go_to_screen2
        )

        self.add_widget(self.name_input)
        self.add_widget(btn)

    def go_to_screen2(self, instance):
        name = self.name_input.text
        self.manager.get_screen('screen2').update_label(name)
        self.manager.current = 'screen2'



class Screen2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.label = MDLabel(
            text="",
            halign="center",
            pos_hint={"center_y": 0.6},
        )

        btn_back = MDRaisedButton(
            text="Regresar",
            pos_hint={"center_x": 0.5, "center_y": 0.3},
            on_release=self.go_back
        )

        self.add_widget(self.label)
        self.add_widget(btn_back)

    def update_label(self, name):
        self.label.text = f"Hola, {name} "

    def go_back(self, instance):
        self.manager.current = 'screen1'



class MyApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Screen1(name='screen1'))
        sm.add_widget(Screen2(name='screen2'))
        return sm


if __name__ == "__main__":
    MyApp().run()