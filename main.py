from kivy.lang import Builder
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarCloseButton
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem,OneLineRightIconListItem,IconLeftWidget
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
from kivy.properties import StringProperty
from kivy.core.text import LabelBase
from kivy.clock import mainthread
from kivymd.uix.card import MDCardSwipe
from time import sleep
from kivy_garden.zbarcam import ZBarCam
from tarefas import show_snackbar
from prices import abastecimento, add_abastecimento_firebase
from kivy.utils import platform
import os
from barcode.writer import ImageWriter
import barcode
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex
from kivy.animation import Animation






class Telaprice(Screen):
    def on_kv_post(self, base_widget):
        self.ids.zbarcam.stop()

    def on_enter(self):
        #self.ids.zbarcam.ids['xcamera']._camera.start()
        self.ids.zbarcam.start()

    def on_leave(self):
        self.ids.zbarcam.stop()
        #self.ids.zbarcam.ids['xcamera']._camera.stop()

class Principal(Screen):
    pass

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

firebaseConfig = {
    "apiKey": "AIzaSyCvJ9mXa6vY6EwPiXOY1o7KjMye22k0OJA",
    "authDomain": "inventariocob.firebaseapp.com",
    "projectId": "inventariocob",
    "storageBucket": "inventariocob.appspot.com",
    "messagingSenderId": "802697439429",
    "appId": "1:802697439429:web:846552f1ba89ed60aa68ac",
    "measurementId": "G-0SRYWQ5YJ3",
    "databaseURL": "https://inventariocob-default-rtdb.firebaseio.com"
  }

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
    '''def on_kv_post(self, base_widget):
        # Carrega o arquivo JSON em um dicionário
        with open('seu_arquivo.json',encoding='utf-8') as f:
            data = json.load(f)

        # Loop através de cada item do dicionário
        for key, value in data.items():
            self.ids.rv.data.append(
                {
                    "text": str(key),
                    "secondary_text": str(value['descricao']),
                    "callback": lambda x: x,
                    "secondary_font_style": "Caption",
                    "_txt_left_pad": "2dp",
                }
            )'''
    
    def lista_a_procura(self, text="", search=False):
        self.ids.rv.data = []

        with open('seu_arquivo.json',encoding='utf-8') as f:
            produtos = json.load(f)

        for ean, produto in produtos.items():
            if search:
                if text.upper() in produto['descricao'].upper():
                    self.ids.rv.data.append(
                        {
                            "source": 'wsol_icon.png',
                            "text": ean,
                            "secondary_text": produto['descricao'],
                            #"callback": lambda x: x,
                            "secondary_font_style": "Caption",
                            "_txt_left_pad": "2dp",
                        }
                    )
            else:
                self.ids.rv.data.append(
                    {
                        "source": 'wsol_icon.png',
                        "text": ean,
                        "secondary_text": produto['descricao'],
                        "callback": lambda x: x,

                    }
                )

class ListaItemsComImg(TwoLineListItem):
    pass
    
class CustomButton(IconLeftWidget):
    def __init__(self, **kwargs):
        self.ean = kwargs.pop('ean')
        super().__init__(**kwargs)

class InventApp(MDApp):
    overlay_color = get_color_from_hex("#6042e4")
    add_abastecimento_firebase = add_abastecimento_firebase
    widgets = {}
    widgets_precos = {}
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
    user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 

    usuario_logado = None
    dialog = None
    dialog2 = None
    dialog3 = None
    login_checked = False

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

    def on_stop(self):
        self.my_stream.close()
    
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(Builder.load_file('login.kv'))
        self.tela_principal =(Builder.load_file('main.kv'))
        self.tela_cadastro = (Builder.load_file('cadastro.kv')) 
        self.screen_manager.add_widget(Builder.load_file('tarefas.kv'))
        self.tela_prices = (Builder.load_file('./prices/precificacao.kv'))
        self.screen_manager.add_widget(self.tela_cadastro)
        self.screen_manager.add_widget(self.tela_prices)
        self.screen_manager.add_widget(self.tela_principal)
        return self.screen_manager
    
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
        envia_tarefas_firebase(title, description, priority)

    def verifica_campos_cadastro(self):
        # obtém, os valores dos campos de entrada
        nome = self.root.get_screen('cadastro').ids.name.text
        nascimento = self.root.get_screen('cadastro').ids.birth.text
        celular = self.root.get_screen('cadastro').ids.pnum.text
        email = self.root.get_screen('cadastro').ids.mail.text
        usuario = self.root.get_screen('cadastro').ids.user.text
        senha = self.root.get_screen('cadastro').ids.password.text
        confirmar_senha = self.root.get_screen('cadastro').ids.password_confirm.text

        # verificar se todos os campos estão preenchidos
        if nome == '' or nascimento == '' or celular == '' or email == '' or usuario == '' or senha == '' or confirmar_senha == '':
            self.show_error_dialog('Todos os campos são obrigatórios!')
            return

        # verificar se as senhas coincidem
        if senha != confirmar_senha:
            self.show_error_dialog('As senhas digitadas não coincidem!')
            return

        # se todos os campos estiverem preenchidos e as senhas coincidirem, enviar dados ao Firebase
        if self.envia_dados_firebase(nome, email, celular, senha, usuario, nascimento):
            self.show_snackbar('Cadastrado com sucesso!')

    def show_error_dialog(self, message):
        dialog = MDDialog(
            title="Erro",
            text=message,
            size_hint=(0.7, None),
            auto_dismiss=True
        )
        dialog.open()
    
    def dialogo_confirmacao_tarefa(self,widget, title, desc, prio, resp,  status=False):
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
                        on_press=lambda *args: inicia_tarefas_firebase(widget.id, title, desc, prio, self.usuario_logado), 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                ],
            )
            confirmation_dialog.open()
        else:
            return
        
    def dialogo_adiciona_item_da_lista(self, ean, qtd, desc):
        confirmation_dialog = MDDialog(
                title="ADICIONAR",
                text="Deseja adicionar o produto onde?",
                buttons=[
                    MDFlatButton(
                        text="ABASTECIMENTO", 
                        on_release=lambda *args: abastecimento(self,ean, qtd, desc)
                    ),
                ],
            )
        confirmation_dialog.open()

    def dialogo_finaliza_tarefa(self,widget, title, desc, prio, data_in, resp,  status=False):
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
                        on_press=lambda *args: finaliza_tarefas_firebase(widget.id, title, desc, prio, self.usuario_logado, data_in), 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                ],
            )
            confirmation_dialog.open()
        else:
            return

    def on_start(self):
        if platform =='android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE,Permission.CAMERA])
        add_abastecimento_firebase(self)
        self.add_all_items_from_firebase()
        self.my_stream = self.db.child("tasks").stream(self.stream_handler, self.user['idToken'])
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

    def ir_para_login(self, *args):
        limpar_dados_login()
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
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(title="SELECIONE A DATA",min_year=1950, max_year=2023,radius=[26, 26, 26, 26], size=(200, 200))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()  

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
            tasks_layout = self.root.get_screen('main').ids.tasks_ongoing
            tasks_layout2 = self.root.get_screen('main').ids.tasks
            tasks_layout.remove_widget(self.widgets[key])
            tasks_layout2.remove_widget(self.widgets[key])

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
            text=botao,
            icon=ico,
            line_color=(0, 0, 0, 0),
            pos_hint={"bottom": 1, "left": 1},
            id=key,
            on_press=lambda *args: self.dialogo_confirmacao_tarefa(task_button,titulo_widget.text, descricao_widget.text, priodidade_widget.text, resp_widget.text, status),
        )
        layout.add_widget(task_button)

        finish_button = MDRectangleFlatIconButton(
            text=botaof,
            icon=icof,
            line_color=(0, 0, 0, 0),
            pos_hint={"bottom": 1, "right": 1},
            id=key,
            on_press=lambda *args: self.dialogo_finaliza_tarefa(finish_button,titulo_widget.text, descricao_widget.text, priodidade_widget.text, data_in,resp_widget.text ,status_fim),
        )
        tasks_layout = self.root.get_screen('main').ids.tasks
        if status == True:
            layout.add_widget(finish_button)
        if status == True:
            tasks_layout = self.root.get_screen('main').ids.tasks_ongoing
        if status_fim == True:
            tasks_layout = self.root.get_screen('main').ids.tasks_finished
    
        card.add_widget(layout)
        tasks_layout.add_widget(card)
        self.widgets[key] = card

    def add_prices(self, ean, qtd):
        try:
            eani = str(ean)
            ean13 = barcode.get_barcode_class('ean13')
            barcode_image = ean13(eani, writer=ImageWriter())
            barcode_image.save(filename=os.path.join(os.getcwd(), "prices", ean))
        except Exception:
            self.show_error_dialog('Verifique o código e tente novamente!')
            return
        else:
            try:
                if qtd == "":
                    qtd = 1
                else:
                    qtd = int(qtd)
                user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")

                ean_data = self.db.child("precos").child(ean).get(user['idToken']).val()

                if ean_data:
                    ean_qtd = ean_data.get('Quantidade', 0)
                    nova_qtd = ean_qtd + qtd
                    data = {"Quantidade": nova_qtd}
                    self.db.child("precos").child(ean).update(data, user['idToken'])
                else:
                    data = {"Quantidade": qtd, "User": self.usuario_logado}
                    self.db.child("precos").child(ean).set(data, user['idToken'])

                items = self.root.get_screen('main').ids.md_list.children
                if ean in self.widgets_precos:
                    print('widget já criado')
                    for item in items:
                        print(item)
                        if isinstance(item, MDCard):
                            for child in item.children:
                                if isinstance(child, TwoLineAvatarIconListItem):
                                    print('widget achado')
                                    ean_data = self.db.child("precos").child(ean).get(user['idToken']).val()
                                    nova_qtd = ean_data.get('Quantidade', 0)
                                    child.secondary_text = f"QTD: {nova_qtd}"
                                    break 
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
                        id=ean,
                        text=f"Quantidade: {qtd}",
                        secondary_text = f"Usuário: {self.usuario_logado}",
                        font_style = "H5",
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
            user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
            all_items = self.db.child("precos").get(user['idToken'])
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
                        id=ean,
                        ean=ean,
                        on_press=self.delete_item
                    ),
                    id=ean,
                    text=f"QUANTIDADE NECESSÁRIA: {qtd}",
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
            show_snackbar("Erro o carregar EANS")
        else:
            return True

    def delete_item(self, button):
        ean = button.ean
        print(button.ean)
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
        self.db.child("precos").child(ean).remove(user['idToken'])
        parent_item = button.parent.parent.parent.parent
        parent_item.parent.remove_widget(parent_item)
        show_snackbar("Iten excluído!")

    def delete_item_2(self, ean):
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
        self.db.child("precos").child(ean).remove(user['idToken'])
        file_path = os.path.join(os.getcwd(), "prices", ean  + '.png')
        os.remove(file_path)
        show_snackbar("Itens excluídos!")

    def delete_item_abastecimento(self, button):
        ean = button.ean
        user = self.auth.sign_in_with_email_and_password("admin@admin.com", "123456")
        self.db.child("abastecimento").child(ean).remove(user['idToken'])
        parent_item = button.parent.parent
        parent_item.parent.remove_widget(parent_item)

    def delete_selected_item(self, instance):
        selection_list = self.root.get_screen('main').ids.md_list
        selected_items = selection_list.get_selected_list_items()

        for item in selected_items:
            selection_list.remove_widget(item)
            ean = item.children[1].id
            self.delete_item_2(ean)
        self.root.get_screen('main').ids.md_list.unselected_all()

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
