import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.utils import platform

if platform == 'android':
    from plyer import usb_hid


class EANApp(App):

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10)
        
        self.ean_input = TextInput(multiline=False)
        layout.add_widget(self.ean_input)
        
        send_button = Button(text="Enviar", on_press=self.send_ean)
        layout.add_widget(send_button)
        
        return layout
    
    def send_ean(self, instance):
        ean_code = self.ean_input.text.strip()
        
        if platform == 'android':
            usb_hid.type_string(ean_code)


if __name__ == '__main__':
    EANApp().run()
