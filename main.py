from kivy.lang import Builder
from modelos import Produtos
from kivy.core.text import LabelBase
LabelBase.register(name='Kumbh Sans', fn_regular='./fonts/Kumbh Sans.ttf')

from kivymd.app import MDApp
from random import sample, choice
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
import json
from cadastro import envia_dados_firebase
from login import *
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.icon_definitions import md_icons


class Tab(MDFloatLayout, MDTabsBase):
    pass

class ScreenListItems(Screen):
    
    def on_kv_post(self, base_widget):
        p = Produtos.select(Produtos.ean, Produtos.descricao) \
        .order_by(Produtos.descricao)

        for row in p.dicts():
            
            sample_images = [
                'wsol_icon.png'
            ]

            self.ids.rv.data.append(
                {
                    #viewclass": "ItemImage",
                    #ImageLeftWidget": choice(sample_images),
                    "source": './images/{}'.format(choice(sample_images)),
                    "text": str(row['ean']),
                    "secondary_text": str(row['descricao']),
                    "callback": lambda x: x,
                }
            )
    def lista_a_procura(self, text="", search=False):
        
        self.ids.rv.data = []
        p = Produtos.select(Produtos.ean, Produtos.descricao) \
        .order_by(Produtos.descricao)
        for row in p.dicts():
            if search:
                if (text.upper() in str(row['ean']).upper() or (text.upper() in str(row['descricao']))):
                    self.ids.rv.data.append(
                        {
                            #viewclass": "ItemImage",
                            #ImageLeftWidget": choice(sample_images),
                            "source": 'wsol_icon.png',
                            "text": str(row['ean']),
                            "secondary_text": str(row['descricao']),
                            "callback": lambda x: x,
                        }
                        )     

class ListaItemsComImg(TwoLineAvatarIconListItem):
    source =StringProperty()
        
class ScreenNovaTela(Screen):
    pass
        

class InventApp(MDApp):

    dialog = None
    dialog2 = None
    login_checked = False

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(Builder.load_file('login.kv'))
        self.screen_manager.add_widget(Builder.load_file('main.kv'))
        self.tela_cadastro = (Builder.load_file('./cadastro/cadastro.kv')) 
        self.screen_manager.add_widget(self.tela_cadastro)
        return self.screen_manager
     
        
    def on_start(self):
        if not self.login_checked:
            with open('dados_login.json', 'r') as f:
                dados_login = json.load(f)
                if 'email' in dados_login and 'senha' in dados_login:
                    email = dados_login['email']
                    senha = dados_login['senha']
                    if email.strip() and senha.strip():
                        self.login_checked = True
                        self.verifica_dados_firebase(email, senha, logado=True)
                    

       
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Tem certeza que deseja deslogar?",
                buttons=[
                    MDFlatButton(
                        text="SIM",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.ir_para_login
                    ),
                    MDFlatButton(
                        text="NÃO",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.fechar_dialogo
                    ),
                ],
            )
        self.dialog.open()

    def show_alert_login(self):
        if not self.dialog2:
            self.dialog2 = MDDialog(
                text="Verifique os dados e tente novamente!",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.fechar_dialogo2
                    ),
                ],
            )
        self.dialog2.open()

    def fechar_dialogo2(self, *args):
        self.dialog2.dismiss()

    def fechar_dialogo(self, *args):
        self.dialog.dismiss()

    def ir_para_login(self, *args):
        self.dialog.dismiss()
        self.root.current = "login"
        self.root.transition.direction = "right"

    def verifica_dados_firebase(self, user, password, logado=False):
        verifica_dados_firebase(self, user, password, logado_antes=logado)
        atualiza_dados_app(self)
        

    def envia_dados_firebase(self, nome, mail, pnum, passw, users, birth):
        if envia_dados_firebase(self, nome, mail, pnum, passw, users, birth):
            return True

    def on_save(self, instance, value, date_range):
        print(instance, value, date_range)
        self.root.get_screen('cadastro').ids.birth.text = value.strftime('%d/%m/%Y')
        

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''

    def show_date_picker(self):
        date_dialog = MDDatePicker(title="SELECIONE A DATA",min_year=1950, max_year=2023, font_name="Kumbh Sans",radius=[26, 26, 26, 26], size=(200, 200))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()    
    
InventApp().run()
