import pyrebase
from kivymd.uix.snackbar import Snackbar
import datetime

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

def envia_tarefas_firebase(title, desc, prior):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime('%Y-%m-%d %H:%M:%S')
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
                    "Responsável": "Ninguém",
                    "Data_in": None,
                    "Data_fim": None,
                    "Data_criacao": agora_sem_milissegundos
                    }
            db.child("tasks").child(title.upper()).set(data, user['idToken'])
        except Exception:
            Snackbar(text="Erro ao enviar os dados!").open()
        else:
            Snackbar(text="Tarefa adicionada com sucesso!").open()
            return True
        
def inicia_tarefas_firebase(title, resp):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime('%Y-%m-%d %H:%M:%S')
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
        try:
            data = {
                    "Status": True,
                    "Responsável": resp,
                    "Data_in": agora_sem_milissegundos,
                    }
            db.child("tasks").child(title.upper()).update(data, user['idToken'])
        except Exception:
            Snackbar(text="Erro ao iniciar tarefa!").open()
        else:
            Snackbar(text="Tarefa iniciada com sucesso!").open()
            return True



   
            
                   
