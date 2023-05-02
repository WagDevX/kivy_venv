from kivy.lang import Builder
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarCloseButton
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem
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

class Content(BoxLayout):
    pass

class Tab(MDFloatLayout, MDTabsBase):
    pass

class ScreenListItems(Screen):
    pass
    
    '''def on_kv_post(self, base_widget):
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
            )'''
    '''def lista_a_procura(self, text="", search=False):
        
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
                        )'''     

class ListaItemsComImg(TwoLineAvatarIconListItem):
    pass
    '''source =StringProperty()'''
    
    
class InventApp(MDApp):
    widgets = {}
    
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
        print(message["event"]) 
        caminho = message["path"] 
        data = message["data"]
        if caminho == "/":
            for i in data.values():
                self.adicionar_tarefa(i["Titulo"],i["Descricao"],i["Prioridade"],i["Responsável"],i["Status"],i["Finalizada"], i["Data_in"], i["Data_fim"])
        else:
            self.adicionar_tarefa(data["Titulo"],data["Descricao"],data["Prioridade"],data["Responsável"],data["Status"], data["Finalizada"],data["Data_in"],data["Data_fim"])


    def on_stop(self):
        self.my_stream.close()

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(Builder.load_file('login.kv'))
        self.screen_manager.add_widget(Builder.load_file('main.kv'))
        self.tela_cadastro = (Builder.load_file('cadastro.kv')) 
        self.screen_manager.add_widget(Builder.load_file('tarefas.kv'))
        self.screen_manager.add_widget(self.tela_cadastro)
        return self.screen_manager

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

    def show_error_dialog(self, message):
        dialog = MDDialog(
            title="Erro",
            text=message,
            size_hint=(0.7, None),
            height="200dp",
            auto_dismiss=True
        )
        dialog.open()
    
    def dialogo_confirmacao_tarefa(self,widget, desc, prio, resp,  status=False):
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
                        on_press=lambda *args: inicia_tarefas_firebase(widget.id, desc, prio, self.usuario_logado), 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                ],
            )
            confirmation_dialog.open()
        else:
            return
        
    def dialogo_finaliza_tarefa(self,widget, desc, prio, data_in,  status=False):
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
                        on_press=lambda *args: finaliza_tarefas_firebase(widget.id, desc, prio, self.usuario_logado, data_in), 
                        on_release=lambda *args: confirmation_dialog.dismiss()
                    ),
                ],
            )
            confirmation_dialog.open()
        else:
            return
        
    def on_start(self):
        self.my_stream = self.db.child("tasks").stream(self.stream_handler, self.user['idToken'])
        '''for k, v in data.items():
            for l, i in v.items():
                titulo = i[7]
                status = i[6]
                responsavel = i[5]
                prioridade = i[4]
                descricao = i[2]
                self.adicionar_tarefa(titulo, descricao, prioridade, responsavel, status)'''
        #self.pega_tarefas_firebase()
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
            y=24,
            pos_hint={"center_x": 0.5},
            size_hint_x=1,
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

    def adicionar_tarefa(self, titulo, descricao, prioridade, responsavel, status, status_fim, data_in, data_fin):
        tasks_layout = self.root.get_screen('main').ids.tasks
        if status == True:
            ico = "clock-check"
            botao = f"Iniciado {data_in}"
        else:
            ico = "clock-alert"
            botao = "Iniciar tarefa"
        if status_fim == True:
            icof = "check-all"
            botaof = f"Finalizado {data_fin}"
        else:
            icof = "checkbox-marked-outline"
            botaof = "Finalizar"

        if '1' in prioridade:
            pri = '1'
            prio = "#f8f5f4"
        elif '2' in prioridade:
            pri = '2'
            prio = "#f8f5f4"
        elif '3' in prioridade:
            pri = '3'
            prio = "#f8f5f4"
        if titulo.upper() in self.widgets:
            tasks_layout = self.root.get_screen('main').ids.tasks
            tasks_layout.remove_widget(self.widgets[titulo.upper()])

        card = MD3Card(
            md_bg_color=prio,
        )
        layout = MDRelativeLayout()

        titulo_widget = TwoLineListItem(
            id=titulo,
            pos_hint={"top": 1, "right": 1},
            font_style="H5",
            text=titulo,
            secondary_text=f"Reponsável: {responsavel}!",
        )
        layout.add_widget(titulo_widget)

        descricao_widget = MDLabel(
            pos_hint={"middle": 1, "left": 20},
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
            id=titulo,
            on_press=lambda *args: self.dialogo_confirmacao_tarefa(task_button, descricao_widget.text, priodidade_widget.text, resp_widget.text, status),
        )
        layout.add_widget(task_button)

        finish_button = MDRectangleFlatIconButton(
            text=botaof,
            icon=icof,
            line_color=(0, 0, 0, 0),
            pos_hint={"bottom": 1, "right": 1},
            id=titulo,
            on_press=lambda *args: self.dialogo_finaliza_tarefa(task_button, descricao_widget.text, priodidade_widget.text, data_in, status_fim),
        )
        if status == True:
            layout.add_widget(finish_button)
        if status == True:
            tasks_layout = self.root.get_screen('main').ids.tasks_ongoing
        if status_fim == True:
            tasks_layout = self.root.get_screen('main').ids.tasks_finished
    
        card.add_widget(layout)
        tasks_layout.add_widget(card)
        self.widgets[titulo.upper()] = card
        texto = "Tarefas atualizadas!"
        self.show_snackbar(texto)
         
    LabelBase.register(name='Kumbh',
                        fn_regular='KumbhSans.ttf')
InventApp().run()
