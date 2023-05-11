from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import Button
from android import Android

class USBKeyboardEmulatorApp(App):
    def build(self):
        self.android = Android()
        self.android.toggle_usb(True)  # Habilita a emulação de teclado USB
        self.ean_list = ['1234567890', '0987654321', '1122334455']  # Lista de EANs a serem enviados
        self.index = 0  # Índice da lista de EANs
        Clock.schedule_interval(self.send_ean, 1)  # Envie um EAN a cada segundo
        return Button(text='Enviar EANs')

    def send_ean(self, dt):
        if self.index < len(self.ean_list):
            ean = self.ean_list[self.index]
            self.android.usb_write(ean)  # Envia o EAN atual
            Clock.schedule_once(lambda dt: self.android.usb_write('\n'), 0.1)  # Envia o evento da tecla Enter
            self.index += 1
        else:
            Clock.unschedule(self.send_ean)  # Para de enviar EANs quando a lista acabar

if __name__ == '__main__':
    USBKeyboardEmulatorApp().run()


