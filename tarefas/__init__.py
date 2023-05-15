import pyrebase
import datetime
from kivymd.uix.snackbar import MDSnackbar,MDSnackbarCloseButton
from kivymd.uix.label import MDLabel

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

def envia_tarefas_firebase(title, desc, prior, setor):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime("%d/%m/%y %H:%M")
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
        try:
            data = {"Titulo": title,
                    "Descricao": desc,
                    "Prioridade": prior,
                    "Status": False,
                    "Finalizada": False,
                    "Responsável": "Ninguém ainda!",
                    "Data_in": "None",
                    "Data_fim": "None",
                    "Data_criacao": agora_sem_milissegundos
                    }
            db.child(setor).child("tasks").push(data, user['idToken'])
        except Exception:
            texto = "Erro ao adicionar tarefa!"
            show_snackbar(texto)
        else:
            texto = "Adicionado com sucesso!"
            show_snackbar(texto)
            return True
        
def inicia_tarefas_firebase(key,title,desc, prio, resp, setor):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime("%d/%m/%y %H:%M")
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
        try:
            data = {"Titulo": title,
                    "Descricao": desc,
                    "Prioridade": prio,
                    "Status": True,
                    "Finalizada": False,
                    "Responsável": resp,
                    "Data_in": agora_sem_milissegundos,
                    "Data_fim": "None",
                    }
            db.child(setor).child("tasks").child(key).set(data, user['idToken'])
        except Exception:
            texto = "Erro ao iniciar tarefa!"
            show_snackbar(texto)
        else:
            texto = "Iniciado com sucesso!"
            show_snackbar(texto)
            return True
        
def show_snackbar(textosnack):
    snackbar = MDSnackbar(
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
    snackbar.open()

def finaliza_tarefas_firebase(key,title,desc, prio, resp, data_in,setor):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime("%d/%m/%y %H:%M")
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
        try:
            data = {"Titulo": title,
                    "Descricao": desc,
                    "Prioridade": prio,
                    "Status": True,
                    "Finalizada": True,
                    "Responsável": resp,
                    "Data_fim": agora_sem_milissegundos,
                    "Data_in": data_in,
                    }
            db.child(setor).child("tasks").child(key).set(data, user['idToken'])
        except Exception:
            texto = "Erro ao finalizar tarefa!"
            show_snackbar(texto)
        else:
            texto = "Finalizado com sucesso!"
            show_snackbar(texto)
            return True            
                   
