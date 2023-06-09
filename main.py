import ctypes, sys
try:
    ctypes.pythonapi = ctypes.PyDLL("libpython%d.%d.so" % sys.version_info[:2])
except Exception:
    print("ERROR Loading ctypes.DLL")
from kivy.lang import Builder
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarCloseButton
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem,IconLeftWidget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from cadastro import envia_dados_firebase
from login import verifica_dados_firebase, atualiza_dados_app, limpar_dados_login
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDRectangleFlatIconButton
from tarefas import inicia_tarefas_firebase, finaliza_tarefas_firebase,envia_tarefas_firebase
from kivymd.font_definitions import theme_font_styles
import pyrebase
import json
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.core.text import LabelBase
from kivy.clock import mainthread
from kivymd.uix.card import MDCardSwipe
from time import sleep
from kivy_garden.zbarcam import ZBarCam
from tarefas import show_snackbar
from prices import abastecimento, add_abastecimento_firebase, is_valid_ean
from validade import adiciona_validade_da_busca, get_node_key
from kivy.utils import platform
import os
from barcode.writer import ImageWriter
import barcode
from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from kivymd.uix.datatables import MDDataTable
from kivy.app import App
from kivymd.uix.menu import MDDropdownMenu
from pyzbar.pyzbar import ZBarSymbol
from pyzbar.pyzbar import decode
from kivy.core.audio import SoundLoader
import datetime
import threading

from firebase import db, id_token
class FValidade(Screen):
    def access_key_data(self):
        validade_screen = self.manager.get_screen("tela_validade")
        key_data = validade_screen.key_data
        print(key_data)
        return key_data
class Validade(Screen):
    right_action_items = ListProperty([])
    selected_row = []
    data_tables = dict()
    row_data = []
    key_data = []
    num_col = 1
    setor = None
    initialized = False
    
    def on_enter(self):
        if not self.initialized:
            self.add_table()
    def add_table(self, refresh=False):
                app = App.get_running_app()
                self.setor = app.setor
                try:
                    validades = db.child(self.setor).child("validade").get(id_token).val()
                    row_data = []
                    index = 1
                    for key, value in validades.items():
                        key = key
                        cod = value.get("COD", "")
                        desc = value.get("Descricao", "")
                        curva = value.get("Curva", "")
                        qtd = value.get("QTD", "")
                        vencimento = value.get("Data_vencimento", "")
                        resp = value.get("Responsável", "")
                        data_add = value.get("Data_de_adição", "")
                        
                        row = (str(index), cod, desc, curva, qtd, vencimento, resp, data_add)
                        row_data.append(row)
                        index += 1
                        self.num_col += 1

                    row_data.sort(key=lambda x: datetime.datetime.strptime(x[5], "%d/%m/%Y"))
                    row_data = [(str(i), *row[1:]) for i, row in enumerate(row_data, 1)]

                    self.data_tables = MDDataTable(
                        background_color_header="#74DBFF",
                        padding=(0,0,0,0),
                        size_hint=(1, 1),
                        use_pagination=True,
                        rows_num=10,
                        check=True,
                        shadow_softness_size=2,
                        elevation = 0,
                        column_data=[
                            ("No.", dp(20), None, "Índice"),
                            ("COD", dp(20), None, "CÓDIGO"),
                            ("DESCRIÇÃO", dp(40)),
                            ("CURVA", dp(20), None, "CURVA DE VENDA"),
                            ("QTD", dp(20), None, "QUANTIDADE"),
                            ("VENC", dp(20), None, "DATA DE VENCIMENTO"),
                            ("RESP", dp(20), None, "RESPONSÁVEL"),
                            ("DATA/HR", dp(20), None, "DATA DE EXPORTAÇÃO"),
                        ],
                        row_data=row_data,
                    )
                    self.data_tables.bind(on_check_press=self.on_check_press)
                    self.data_tables = self.data_tables
                    self.ids.lista_validade.add_widget(self.data_tables)
                    if refresh:
                        show_snackbar("Atualizado com sucesso!")
                except Exception:
                    texto = "Verifique sua conexão!"
                    show_snackbar(texto)
                finally:
                    self.initialized = True
                    
        
    def on_check_press(self, instance_table, current_row):
        app = App.get_running_app()
        self.setor = app.setor
        self.selected_row = current_row
        self.right_action_items = [["table-edit", lambda x: app.edit_selected_row(self.selected_row[1], self.selected_row[2], self.selected_row[3], self.selected_row[4], self.selected_row[5])]]
        t = threading.Thread(target=self.get_key_data, args=(current_row,))
        t.start()
    def get_key_data(self, current_row):
        self.key_data = get_node_key(current_row[1],current_row[2],current_row[3],current_row[4],current_row[5], current_row[6], self.setor)

class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()
    id = StringProperty()

class TypeMapElement(MDBoxLayout):
    cols = NumericProperty()
    selected = BooleanProperty(False)
    icon = StringProperty()
    title = StringProperty()

class Telaprice(Screen):

    def on_pre_enter(self, *args):
        if not hasattr(self, 'cam_adicionada'):
            self.zbarcam = ZBarCam(
                code_types=[ZBarSymbol.QRCODE, ZBarSymbol.EAN13],
                #on_symbols=partial(self.on_symbols, self),
            )
            # Adicione o widget à tela
            self.zbarcam.bind(symbols=self.on_symbols)
            self.ids.mybox.add_widget(self.zbarcam)
            self.cam_adicionada = True
        else:
            self.zbarcam.start()
    
    def on_symbols(self, instance, symbols):
        print('funcionando')
        for symbol in symbols:
            print(symbol.data.decode())
        if not symbols == "":
            for symbol in symbols:
                self.ids.price_ean.text = symbol.data.decode()
                sound = SoundLoader.load("som_de_beep.wav")
                if sound:
                    print("Sound found at %s" % sound.source)
                    print("Sound is %.3f seconds" % sound.length)
                    sound.play()
                sleep(1)

    def on_leave(self):
        self.zbarcam.stop()
        

class Principal(Screen):
    widgets = {}
    
    def dialogo_finaliza_tarefa(self,widget, title, desc, prio, data_in, resp,  status=False):
        self.usuario_logado = self.ids.username.text
        if resp != self.usuario_logado:
            return
        if status == False:
            confirmation_dialog = MDDialog(
                title="Confirmação",
                text="Você tem certeza de que deseja finalizar a tarefa?",
                buttons=[
                    MDFlatButton(
                        text="Cancelar", 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="Sim", 
                        on_press=lambda *args: finaliza_tarefas_firebase(widget.id, title, desc, prio, self.ids.username.text, data_in, self.ids.setor.text), 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                ],
            )
            confirmation_dialog.open()
        else:
            return
        
    def dialogo_inicia_tarefa(self,widget, title, desc, prio, resp,  status=False):
        if status == False:
            confirmation_dialog = MDDialog(
                title="Confirmação",
                text="Você tem certeza de que deseja iniciar a tarefa?",
                buttons=[
                    MDFlatButton(
                        text="Cancelar", 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="Sim", 
                        on_press=lambda *args: inicia_tarefas_firebase(widget.id, title, desc, prio, self.ids.username.text, self.ids.setor.text), 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                ],
            )
            confirmation_dialog.open()
        else:
            return

    def show_snackbar(self, textosnack):
            self.snackbar = MDSnackbar(
            MDLabel(
                text=textosnack,
                theme_text_color="Custom",
                text_color="#393231",
            ),
            MDSnackbarCloseButton(
                icon="check",
                theme_text_color="Custom",
                text_color="#8E353C",
                _no_ripple_effect=True,
            ),
            y=80,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            md_bg_color="AAFF00",
            )
            self.snackbar.open()

    def adicionar_tarefa(self,key, titulo, descricao, prioridade, responsavel, status, status_fim, data_in, data_fin):
        if status == True:
            ico = "clock-check"
            botao = f"{data_in}"
        else:
            ico = "clock-alert"
            botao = "Iniciar tarefa"
        if status_fim == True:
            icof = "check-all"
            botaof = f"{data_fin}"
        else:
            icof = "checkbox-marked-outline"
            botaof = "Finalizar"

        if '1' in prioridade:
            pri = '1'
            prio = "#abbdf2"
        elif '2' in prioridade:
            pri = '2'
            prio = "#d5def8"
        elif '3' in prioridade:
            pri = '3'
            prio = "#eaeefb"
        if key in self.widgets:
            tasks_layout = self.ids.tasks_ongoing
            tasks_layout2 = self.ids.tasks
            tasks_layout3 = self.ids.tasks_finished
            tasks_layout.remove_widget(self.widgets[key])
            tasks_layout2.remove_widget(self.widgets[key])
            tasks_layout3.remove_widget(self.widgets[key])

        card = MD3Card(
            md_bg_color=prio,
        )
        layout = MDRelativeLayout()

        titulo_widget = TwoLineListItem(
            id=key,
            _txt_left_pad = "0dp",
            _txt_bot_pad = "10dp",
            pos_hint={"top": 1.05, "right": 1},
            font_style="H5",
            text=titulo,
            secondary_text=f"Reponsável: {responsavel}!",
        )
        layout.add_widget(titulo_widget)

        descricao_widget = MDLabel(
            font_name = "Kumbh",
            pos_hint={"top": 0.92, "left": 1},
            text=descricao,
            font_style="Subtitle1",
        )
        layout.add_widget(descricao_widget)

        priodidade_widget = MDLabel(
            pos_hint={"center_x": 0.51, "center_y": 0.43},
            text=pri,
            font_style="Subtitle1",
            opacity="0.0",
        )
        layout.add_widget(priodidade_widget)

        resp_widget = MDLabel(
            pos_hint={"middle": 1, "left": 1},
            text=responsavel,
            font_style="Subtitle1",
            opacity="0.0",
        )
        layout.add_widget(resp_widget)

        task_button = MDRectangleFlatIconButton(
            font_name = 'Kumbh',
            text=botao,
            icon=ico,
            line_color=(0, 0, 0, 0),
            pos_hint={"bottom": 1, "left": 1},
            id=key,
            on_press=lambda *args: self.dialogo_inicia_tarefa(task_button,titulo_widget.text, descricao_widget.text, priodidade_widget.text, resp_widget.text, status),
        )
        layout.add_widget(task_button)

        finish_button = MDRectangleFlatIconButton(
            font_name = 'Kumbh',
            text=botaof,
            icon=icof,
            line_color=(0, 0, 0, 0),
            pos_hint={"bottom": 1, "right": 1},
            id=key,
            on_press=lambda *args: self.dialogo_finaliza_tarefa(finish_button,titulo_widget.text, descricao_widget.text, priodidade_widget.text, data_in,resp_widget.text ,status_fim),
        )
        tasks_layout = self.ids.tasks
        if status == True:
            layout.add_widget(finish_button)
        if status == True:
            tasks_layout = self.ids.tasks_ongoing
        if status_fim == True:
            tasks_layout = self.ids.tasks_finished
    
        card.add_widget(layout)
        tasks_layout.add_widget(card)
        self.widgets[key] = card

    @mainthread
    def stream_handler(self, message):
        try:
            print(message["event"]) 
            caminho = message["path"]
            id = caminho.lstrip("/") 
            data = message["data"]
            if caminho == "/":
                for k, i in data.items():
                    self.adicionar_tarefa(k,i["Titulo"],i["Descricao"],i["Prioridade"],i["Responsável"],i["Status"],i["Finalizada"], i["Data_in"], i["Data_fim"])
            else:
                self.adicionar_tarefa(id,data["Titulo"],data["Descricao"],data["Prioridade"],data["Responsável"],data["Status"],data["Finalizada"], data["Data_in"], data["Data_fim"])
                texto = "Tarefas atualizadas!"
                self.show_snackbar(texto)
        except Exception:
            texto = "Erro de conexão!"
            self.show_snackbar(texto)

    def on_enter(self, *args):
        if not hasattr(self, 'stream_executed'):
            setor = self.ids.setor.text
            self.my_stream = db.child(setor).child("tasks").stream(self.stream_handler, id_token)
            self.stream_executed = True
    
    def close_stream(self):
        self.my_stream.close()

class Tarefas(Screen):
    pass

class Telalogin(Screen):
    pass

class Telacadastro(Screen):
    pass

class SwipeToDeleteItem(MDCardSwipe):
    text = StringProperty()

class userconfigscreen(Screen):
    pass

class MD3Card(MDCard):
    text = StringProperty()

class MD4Card(MDCard):
    text = StringProperty()

class MD2Card(MDCard):
    text = StringProperty()

class Content(BoxLayout):
    pass

class Tab(MDFloatLayout, MDTabsBase):
    pass

class ScreenListItems(Screen):
    def search_products(self, text="", search=False, products=None):
        self.ids.rv.data = []

        if products is None:
            with open('DADOS_PRODUTOS.json', encoding='utf-8') as f:
                products = json.load(f)

        keywords = set(text.upper().replace('.', '').split())

        self.ids.rv.data = [
            {
                "source": 'wsol_icon.png',
                "text": ean,
                "secondary_text": product['descricao'],
                "secondary_font_style": "Caption",
                "_txt_left_pad": "2dp",
            }
            for ean, product in products.items()
            if (search and keywords.intersection(set(product['descricao'].upper().replace('.', '').split()))) or not search
        ]

class ListaItemsComImg(TwoLineListItem):
    pass
    
class CustomButton(IconLeftWidget):
    def __init__(self, **kwargs):
        self.ean = kwargs.pop('ean')
        super().__init__(**kwargs)

class InventApp(MDApp):
    setor = None
    overlay_color = get_color_from_hex("#6042e4")
    add_abastecimento_firebase = add_abastecimento_firebase
    widgets = {}
    widgets_precos = {}
    usuario_logado = None
    dialog = None
    dialog2 = None
    dialog3 = None
    login_checked = False
        
    def on_stop(self):
        Principal.close_stream
        
    def set_active_element(self, instance, setor_escolhido):
        for element in self.root.get_screen('cadastro').ids.grid_container.children:
            if instance == element:
                element.selected = True
                self.root.get_screen('cadastro').ids.setor.text = setor_escolhido
            else:
                element.selected = False    
    
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(Builder.load_file('./login/login.kv'))
        self.tela_principal =(Builder.load_file('main.kv'))
        self.tela_cadastro = (Builder.load_file('./cadastro/cadastro.kv')) 
        self.tela_recuperacao = (Builder.load_file('./login/recuperacao.kv')) 
        self.screen_manager.add_widget(Builder.load_file('./tarefas/tarefas.kv'))
        self.tela_prices = (Builder.load_file('./prices/precificacao.kv'))
        self.tela_validade = (Builder.load_file('./validade/validade.kv'))
        self.tela_fazer_validade = (Builder.load_file('./validade/fazer_validade.kv'))
        self.tela_editar_validade = (Builder.load_file('./validade/editar_validade.kv'))
        self.screen_manager.add_widget(self.tela_cadastro)
        self.screen_manager.add_widget(self.tela_prices)
        self.screen_manager.add_widget(self.tela_principal)
        self.screen_manager.add_widget(self.tela_recuperacao)
        self.screen_manager.add_widget(self.tela_validade)
        self.screen_manager.add_widget(self.tela_fazer_validade)
        self.screen_manager.add_widget(self.tela_editar_validade)
        return self.screen_manager
    
    def edit_selected_row(self, cod, desc, curv, qtd, val):
        self.root.transition.direction = "left"
        self.root.current = "editar_validade"
        self.root.get_screen('editar_validade').ids.ean_ou_in.text = cod
        self.root.get_screen('editar_validade').ids.val_desc.text = desc
        self.root.get_screen('editar_validade').ids.val_curva.text = curv
        self.root.get_screen('editar_validade').ids.val_qtd.text = qtd
        self.root.get_screen('editar_validade').ids.data_vencimento.text = val
    
    def go_to_main_screen(self):
        self.root.transition.direction = "right"
        self.root.current = "main"

    def envia_email_recup_senha(self, email):
        self.auth.send_password_reset_email(email)
    
    def on_symbols(self,instance,symbols):
        if not symbols == "":
            for symbol in symbols:
                self.root.get_screen('prices_add').ids.price_ean.text = symbol.data.decode()
            
    def validate_task_fields(self):
        title = self.root.get_screen('tasks_send').ids.task_title.text.strip()
        description = self.root.get_screen('tasks_send').ids.task_description.text.strip()
        priority = self.root.get_screen('tasks_send').ids.priority.text.strip()

        if not title or not description or not priority:
            # Caso algum campo esteja vazio, exibe uma mensagem de erro
            self.show_error_dialog("Por favor, preencha todos os campos.")
            return

        if priority not in ["1", "2", "3"]:
            # Caso a prioridade não seja 1, 2 ou 3, exibe uma mensagem de erro
            self.show_error_dialog("Por favor, selecione uma prioridade válida (1, 2 ou 3).")
            return

        # Caso todos os campos estejam preenchidos corretamente, envia a tarefa para o Firebase
        envia_tarefas_firebase(title, description, priority, self.setor)

    def verifica_campos_cadastro(self):
        # obtém, os valores dos campos de entrada
        nome = self.root.get_screen('cadastro').ids.name.text
        nascimento = self.root.get_screen('cadastro').ids.birth.text
        celular = self.root.get_screen('cadastro').ids.pnum.text
        email = self.root.get_screen('cadastro').ids.mail.text
        usuario = self.root.get_screen('cadastro').ids.user.text
        password_widget = self.root.get_screen('cadastro').ids.password
        senha = password_widget.ids.text_field.text
        confirm_password_widget = self.root.get_screen('cadastro').ids.password_confirm
        confirmar_senha = confirm_password_widget.ids.text_field.text
        setor = self.root.get_screen('cadastro').ids.setor.text
        self.root.get_screen('cadastro').ids.botao_cadastrar.disabled = True
        self.root.get_screen('cadastro').ids.botao_cadastrar.text = 'Cadastrando'

        # verificar se todos os campos estão preenchidos
        if nome == '' or nascimento == '' or celular == '' or email == '' or usuario == '' or senha == '' or confirmar_senha == '' or setor == '':
            self.show_error_dialog('Todos os campos são obrigatórios!')
            self.root.get_screen('cadastro').ids.botao_cadastrar.disabled = False
            self.root.get_screen('cadastro').ids.botao_cadastrar.text = 'Cadastrar'
            return

        # verificar se as senhas coincidem
        if senha != confirmar_senha:
            self.show_error_dialog('As senhas digitadas não coincidem!')
            self.root.get_screen('cadastro').ids.botao_cadastrar.disabled = False
            self.root.get_screen('cadastro').ids.botao_cadastrar.text = 'Cadastrar'
            return
        
        def execute_later(dt):
            if self.envia_dados_firebase(nome, email, celular, senha, usuario, nascimento, setor):
                self.show_snackbar('Cadastrado com sucesso!')
            self.root.get_screen('cadastro').ids.botao_cadastrar.disabled = False
            self.root.get_screen('cadastro').ids.botao_cadastrar.text = 'Cadastrar'
        Clock.schedule_once(execute_later, 0.5)

    def show_error_dialog(self, message):
        dialog = MDDialog(
            title="Erro",
            text=message,
            size_hint=(0.7, None),
            auto_dismiss=True
        )
        dialog.open()
        
    def dialogo_adiciona_item_da_lista(self, ean, qtd, desc):
        confirmation_dialog = MDDialog(
                title="ADICIONAR",
                text="Deseja adicionar o produto onde?",
                buttons=[
                    MDFlatButton(
                        text="ABASTECIMENTO", 
                        on_release=lambda *args: abastecimento(self,ean, qtd, desc)
                    ),
                    MDFlatButton(
                        text="VALIDADE", 
                        on_release=lambda *args: adiciona_validade_da_busca(self,ean,desc),
                        on_press=lambda *args: confirmation_dialog.dismiss() 
                    ),
                ],
            )
        confirmation_dialog.open()

    def on_start(self):
        if platform =='android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE,Permission.CAMERA])
        if not self.login_checked:
            try:
                with open('dados_login.json', 'r') as f:
                    dados_login = json.load(f)
                    if 'email' in dados_login and 'senha' in dados_login:
                        email = dados_login['email']
                        senha = dados_login['senha']
                        user = dados_login['nome_de_usuario']
                        if email.strip() and senha.strip() and user.strip():
                            self.login_checked = True
                            self.usuario_logado = user
                            self.verifica_dados_firebase(email, senha, logado=True)
            except Exception:
                pass
                    
    def show_alert_dialog_logout(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Tem certeza que deseja deslogar?",
                buttons=[
                    MDFlatButton(
                        text="SIM",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.fazer_log_out
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

    def show_snackbar(self, textosnack):
            self.snackbar = MDSnackbar(
            MDLabel(
                text=textosnack,
                theme_text_color="Custom",
                text_color="#393231",
            ),
            MDSnackbarCloseButton(
                icon="check",
                theme_text_color="Custom",
                text_color="#8E353C",
                _no_ripple_effect=True,
            ),
            y=80,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            md_bg_color="AAFF00",
            )
            self.snackbar.open()

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

    def fechar_dialogo3(self, *args):
        self.dialog3.dismiss()

    def fechar_dialogo(self, *args):
        self.dialog.dismiss()

    def fazer_log_out(self, *args):
        self.root.get_screen('main').ids.tasks.clear_widgets()
        self.root.get_screen('main').ids.md_list.clear_widgets()
        self.root.get_screen('main').ids.lista_abastecimento.clear_widgets()
        limpar_dados_login()
        self.dialog.dismiss()
        self.root.current = "login"
        self.root.transition.direction = "right"

    def verifica_dados_firebase(self, user, password, logado=False):
        spinner = MDSpinner(size_hint=(None, None), size=(dp(48), dp(48)),
                       pos_hint={'center_x': 0.5, 'center_y': .33},
                       determinate=False,
                       determinate_time=1)
        self.root.get_screen('login').ids.login_page.add_widget(spinner)
        self.root.get_screen('login').ids.botao_logar.disabled = True
        self.root.get_screen('login').ids.botao_logar.text = 'Aguarde'
        def execute_later(dt):
            verifica_dados_firebase(self, user, password, logado_antes=logado)
            atualiza_dados_app(self)
            add_abastecimento_firebase(self)
            self.add_all_items_from_firebase()

            self.root.get_screen('login').ids.login_page.remove_widget(spinner)
            self.root.get_screen('login').ids.botao_logar.disabled = False
            self.root.get_screen('login').ids.botao_logar.text = 'Log in'

        Clock.schedule_once(execute_later, 1)
        
    def envia_dados_firebase(self, nome, mail, pnum, passw, users, birth, setor):
        if envia_dados_firebase(self, nome, mail, pnum, passw, users, birth, setor):
            return True

    def on_save(self, instance, value, date_range):
        print(instance, value, date_range)
        self.root.get_screen('cadastro').ids.birth.text = value.strftime('%d/%m/%Y')
        
    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(title="SELECIONE A DATA",min_year=1950, max_year=2023,radius=[26, 26, 26, 26], size=(200, 200))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()  

    def add_prices(self, ean, qtd):
        if is_valid_ean(ean) is False:
            self.show_error_dialog('Digite um ean válido!')
            return
        try:
            if qtd == "":
                qtd = 1
            else:
                qtd = int(qtd)
            ean_data = db.child(self.setor).child("precos").child(ean).get(id_token).val()

            if ean_data:
                ean_qtd = ean_data.get('Quantidade', 0)
                nova_qtd = ean_qtd + qtd
                data = {"Quantidade": nova_qtd}
                db.child(self.setor).child("precos").child(ean).update(data, id_token)
            else:
                data = {"Quantidade": qtd, "User": self.usuario_logado}
                db.child(self.setor).child("precos").child(ean).set(data, id_token)

            if ean in self.widgets_precos:
                grid_layout = self.widgets_precos[ean].children[0]
                items = grid_layout.children
                card = self.widgets_precos[ean]
                for item in items:
                    if isinstance(item, TwoLineAvatarIconListItem):
                        print('widget achado')
                        ean_data = db.child(self.setor).child("precos").child(ean).get(id_token).val()
                        nova_qtd = ean_data.get('Quantidade', 0)
                        item.text = f"QUANTIDADE: {nova_qtd}"
                        show_snackbar("Quantidade atualizada!")
            else:
                eani = str(ean)
                ean13 = barcode.get_barcode_class('ean13')
                barcode_image = ean13(eani, writer=ImageWriter())
                barcode_image.save(filename=os.path.join(os.getcwd(), "prices", ean))
                card = MD4Card(
                    md_bg_color="FFFFFF",
                    id=ean
                )
                layout = GridLayout(cols=1)
                item = TwoLineAvatarIconListItem(
                    CustomButton(
                        icon="delete-circle-outline",
                        on_press=self.delete_item,
                        ean=ean
                    ),
                    text=f"QUANTIDADE: {qtd}",
                    secondary_text = f"Usuário: {self.usuario_logado}",
                    font_style = "Subtitle1",
                    _no_ripple_effect = True
                )
                layout.add_widget(item)
                ean_layout = Image(source=f'prices/{ean}.png', allow_stretch=True)
                layout.add_widget(ean_layout)

                card.add_widget(layout)
                self.root.get_screen('main').ids.md_list.add_widget(card)
                item.ean = ean
                show_snackbar("Adicionado com sucesso!")
                self.widgets_precos[ean] = card
        except Exception:
            self.show_error_dialog('Verifique o código e tente novamente!')

    def add_all_items_from_firebase(self):
        try:
            for item in list(self.root.get_screen('main').ids.md_list.children):
                self.root.get_screen('main').ids.md_list.remove_widget(item)
            all_items = db.child(self.setor).child("precos").get(id_token)
            for ean, data in all_items.val().items():
                qtd = data.get("Quantidade")
                user_l = data.get("User")

                ean13 = barcode.get_barcode_class('ean13')
                barcode_image = ean13(ean, writer=ImageWriter())
                barcode_image.save(filename=os.path.join(os.getcwd(), "prices", ean))

                card = MD4Card(
                md_bg_color="FFFFFF",
                id=ean
                )
                layout = GridLayout(cols=1)
                item = TwoLineAvatarIconListItem(
                    CustomButton(
                        icon="delete-circle-outline",
                        ean=ean,
                        on_press=self.delete_item
                    ),
                    text=f"QUANTIDADE: {qtd}",
                    secondary_text = f"Usuário: {user_l}",
                    font_style = "Subtitle1",
                    _no_ripple_effect = True
                )
                layout.add_widget(item)
                ean_layout = Image(source=f'prices/{ean}.png', allow_stretch=True)
                layout.add_widget(ean_layout)
                card.add_widget(layout)
                self.root.get_screen('main').ids.md_list.add_widget(card)
                item.ean = ean
                self.widgets_precos[ean] = card
        except Exception:
            pass
        else:
            return True

    def delete_item(self, button):
        ean = button.ean
        db.child(self.setor).child("precos").child(ean).remove(id_token)
        parent_item = button.parent.parent.parent.parent
        parent_item.parent.remove_widget(parent_item)
        show_snackbar("Iten excluído!")

    def delete_item_2(self, eans):
        try:
            updates = {}
            for ean in eans:
                updates[ean] = None
                file_path = os.path.join(os.getcwd(), "prices", ean  + '.png')
                os.remove(file_path)
            db.child(self.setor).child("precos").update(updates, id_token)
            show_snackbar("Itens excluídos!")
        except Exception:
            pass

    def delete_item_abastecimento(self, button):
        ean = button.ean
        db.child(self.setor).child("abastecimento").child(ean).remove(id_token)
        parent_item = button.parent.parent
        parent_item.parent.remove_widget(parent_item)
        show_snackbar("Item excluído!")

    def delete_selected_item(self, instance):
        selection_list = self.root.get_screen('main').ids.md_list
        self.root.get_screen('main').ids.toolbar.right_action_items = [["dots-horizontal-circle"], ["dots-vertical"]]
        self.root.get_screen('main').ids.toolbar.right_action_items.disabled = True
        selected_items = selection_list.get_selected_list_items()
        self.root.get_screen('main').ids.toolbar.title =f"Excluindo {len(selected_items)} itens, aguarde"

        def execute_later(dt):
            for item in selected_items:
                selection_list.remove_widget(item)
            eans = [item.children[1].id for item in selected_items]
            self.delete_item_2(eans)
            self.root.get_screen('main').ids.md_list.unselected_all()
        Clock.schedule_once(execute_later, 1)

    def set_selection_mode(self, instance_selection_list, mode):
        if mode:
            md_bg_color = self.overlay_color
            left_action_items = [
                [
                    "close",
                    lambda x: self.tela_principal.ids.md_list.unselected_all(),
                ]
            ]
            right_action_items = [["trash-can", lambda x: self.delete_selected_item(x)], ["dots-vertical"]]
        else:
            md_bg_color = (0, 0, 0, 1)
            left_action_items = [["menu"]]
            right_action_items = [["dots-vertical"]]
            self.root.get_screen('main').ids.toolbar.title = "Itens a precificar"

        Animation(md_bg_color=md_bg_color, d=0.2).start(self.root.get_screen('main').ids.toolbar)
        self.root.get_screen('main').ids.toolbar.left_action_items = left_action_items
        self.root.get_screen('main').ids.toolbar.right_action_items = right_action_items

    def on_selected(self, instance_selection_list, instance_selection_item):
        self.root.get_screen('main').ids.toolbar.title = str(
            len(instance_selection_list.get_selected_list_items())
        )

    def on_unselected(self, instance_selection_list, instance_selection_item):
        if instance_selection_list.get_selected_list_items():
            self.root.get_screen('main').ids.toolbar.title = str(
                len(instance_selection_list.get_selected_list_items())
            )

    LabelBase.register(name='Kumbh',
                        fn_regular='KumbhSans.ttf')
InventApp().run()
