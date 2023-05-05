from kivymd.app import MDApp
from kivy.lang import Builder
from pyzbar.pyzbar import ZBarSymbol
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.label import MDLabel
from time import sleep
 
 
KV = """
#:import ZBarCam kivy_garden.zbarcam.ZBarCam
#:import ZBarSymbol pyzbar.pyzbar.ZBarSymbol
MDBoxLayout:
	id:mybox
	orientation: 'vertical'
	size_hint_y: 0.45
	pos_hint:{"center_y":0.80}
	padding:20
	spacing:20
	ZBarCam:
		id:zbarcam
		code_types:ZBarSymbol.QRCODE.value,ZBarSymbol.EAN13.value
		on_symbols:app.on_symbols(*args)
 
"""
 
class Myapp(MDApp):
	def build(self):
		self.root = Builder.load_string(KV)
 
	def on_symbols(self,instance,symbols):
		if not symbols == "":
			for symbol in symbols:
				print("YOu Qr is : ",symbol.data.decode())
				snackbar = MDSnackbar(
                MDLabel(
                    text="You Qr is : {}".format(symbol.data.decode()),
                    theme_text_color="Custom",
                    text_color="#393231",
                ),
                y=24,
                pos_hint={"center_x": 0.5},
                size_hint_x=1,
                md_bg_color="AAFF00",
                )
				snackbar.open()
				sleep(1)
 
if __name__ == "__main__":
	Myapp().run()