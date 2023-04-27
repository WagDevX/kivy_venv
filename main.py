from kivy.lang import Builder
from kivymd.uix.snackbar import Snackbar
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from cadastro import envia_dados_firebase
from login import verifica_dados_firebase, atualiza_dados_app
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.button import MDRectangleFlatIconButton
from tarefas import inicia_tarefas_firebase
from kivymd.font_definitions import theme_font_styles
import pyrebase
import json
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


class Content(BoxLayout):
    pass

class Tab(MDFloatLayout, MDTabsBase):
    pass

class ScreenListItems(Screen):
    pass 

class ListaItemsComImg(TwoLineAvatarIconListItem):
    pass
    

class InventApp(MDApp):
    usuario_logado = None
    dialog = None
    dialog2 = None
    dialog3 = None
    login_checked = False

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(Builder.load_file('login.kv'))
        self.screen_manager.add_widget(Builder.load_file('main.kv'))
        self.tela_cadastro = (Builder.load_file('cadastro.kv')) 
        self.screen_manager.add_widget(Builder.load_file('tarefas.kv'))
        self.screen_manager.add_widget(self.tela_cadastro)
        return self.screen_manager
    
    def dialogo_confirmacao_tarefa(self,widget, bot=True):
        if bot == False:
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
                        on_release=lambda *args: inicia_tarefas_firebase(widget.id, self.usuario_logado) and confirmation_dialog.dismiss() 
                    ),
                ],
            )
            confirmation_dialog.open()
        
    def show_confirmation_dialog(self):
        if not self.dialog3:
            self.dialog3 = MDDialog(
                title="ADICIONAR TAREFA:",
                type="custom",
                content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_press=self.fechar_dialogo3
                    ),
                    MDFlatButton(
                        text="ADICIONAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        self.dialog3.open()
    def on_start(self):
        self.pega_tarefas_firebase(True)
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
        date_dialog = MDDatePicker(title="SELECIONE A DATA",min_year=1950, max_year=2023, font_name="Kumbh Sans",radius=[26, 26, 26, 26], size=(200, 200))
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()  

    def adicionar_tarefa(self, titulo, descricao, prioridade, responsavel, status, login=False):
        tasks_layout = self.root.get_screen('main').ids.tasks
        for child in tasks_layout.children:
            if child.id == titulo:
                Snackbar(text="Nenhuma tarefa nova!").open()
                print(f"O widget com ID '{titulo}' já existe na tela.")
                return
        if status == True:
            ico = "check-all"
            botao = "Tarefa iniciada"
            bot  = True
        else:
            ico = "clock-check"
            botao = "Iniciar tarefa"
            bot  = False
        if '1' in prioridade:
            prio = "ff1100"
        elif '2' in prioridade:
            prio = "5B8900"
        elif '3' in prioridade:
            prio = "007989"
        card = MDCard(
            md_bg_color=prio,
            height=200,
            size_hint=(1, None),
            padding=10,
            id=titulo,
        )
        layout = MDRelativeLayout()

        titulo_widget = TwoLineListItem(
            id=titulo,
            pos_hint={"top": 1, "right": 1},
            font_style="H5",
            text=titulo,
            secondary_text=f"{responsavel} está fazendo!",
        )
        layout.add_widget(titulo_widget)

        descricao_widget = MDLabel(
            pos_hint={"center_x": 0.5, "center_y": 0.43},
            text=descricao,
            font_style="Subtitle1",
            padding=15,
        )
        layout.add_widget(descricao_widget)

        task_button = MDRectangleFlatIconButton(
            text=botao,
            icon=ico,
            line_color=(0, 0, 0, 0),
            pos_hint={"bottom": 1, "left": 1},
            id=titulo,
            on_press=lambda *args: self.dialogo_confirmacao_tarefa(task_button,bot),
        )
        layout.add_widget(task_button)

        card.add_widget(layout)
        tasks_layout = self.root.get_screen('main').ids.tasks
        tasks_layout.add_widget(card)
        if login == False:
            Snackbar(text="Tarefas adicionadas com sucesso!").open() 
         
    def pega_tarefas_firebase(self, logado=False):
            firebase = pyrebase.initialize_app(firebaseConfig)
            auth = firebase.auth()
            db = firebase.database()
            au = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
            user_ref = db.child('tasks')
            task_data = user_ref.get(au['idToken']).val()
            dados_tarefas = []
            sorted_tasks = sorted(task_data.items(), key=lambda x: x[1]['Prioridade'])
            for task_id, task_data in sorted_tasks:
                Descricao = task_data["Descricao"]
                Finalizada = task_data["Finalizada"]
                Prioridade = task_data["Prioridade"]
                Responsável = task_data["Responsável"]
                Status = task_data["Status"]
                Titulo = task_data["Titulo"]
                self.adicionar_tarefa(Titulo, Descricao, Prioridade, Responsável, Status, logado)
                tarefa = {'Descricao': Descricao, 
                    'Finalizada': Finalizada, 
                    'Prioridade': Prioridade,
                    'Responsável': Responsável,
                    'Status': Status,
                    'Titulo': Titulo}
                dados_tarefas.append(tarefa)
                with open('dados_tarefas.json', 'w') as f:
                    json.dump(dados_tarefas, f)
            

InventApp().run()
