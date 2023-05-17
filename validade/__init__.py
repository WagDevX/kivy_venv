
import pyrebase
import datetime
from tarefas import show_snackbar

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

def envia_validade_firebase(cod, desc, curva, qtd, vencimento, resp, setor):
        agora = datetime.datetime.now()
        agora_sem_milissegundos = agora.strftime("%d/%m/%y %H:%M")
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
        try:
            data = {"COD": cod,
                    "Descricao": desc,
                    "Curva": curva,
                    "QTD": qtd,
                    "Data_vencimento": vencimento,
                    "Responsável": resp,
                    "Data_de_adição": agora_sem_milissegundos
                    }
            db.child(setor).child("validade").push(data, user['idToken'])
        except Exception:
            texto = "Erro ao adicionar validade!"
            show_snackbar(texto)
        else:
            texto = "Adicionado com sucesso!"
            show_snackbar(texto)
            return True
        
