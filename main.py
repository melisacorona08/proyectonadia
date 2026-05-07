from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton

class MyApp(MDApp):
    def build(self):
        return MDRectangleFlatButton(
            text="Hola, mundo!",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

MyApp().run()