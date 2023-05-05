from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.add_widget(Button(text="Ir para a tela secundária", on_press=self.switch_to_secondary))

    def switch_to_secondary(self, *args):
        self.manager.switch_to(SecondaryScreen())

class SecondaryScreen(Screen):
    def __init__(self, **kwargs):
        super(SecondaryScreen, self).__init__(**kwargs)
        self.add_widget(Button(text="Voltar para a tela principal", on_press=self.switch_to_main))

    def switch_to_main(self, *args):
        self.manager.switch_to(MainScreen())

class MyScreenManager(ScreenManager):
    pass

class MyApp(App):
    def build(self):
        sm = MyScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SecondaryScreen(name='secondary'))
        return sm

MyApp().run()
