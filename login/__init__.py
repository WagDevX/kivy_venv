import json
import pyrebase

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

def verifica_dados_firebase(self, user, password, logado_antes=False):
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        au = auth.sign_in_with_email_and_password("admin@admin.com.br", "123456") 
        try:
            aut = auth.sign_in_with_email_and_password(user, password)
        except Exception:
            self.show_alert_login()
        else:
            if logado_antes == False:
                nome_de_usuario = aut['displayName']
                user_ref = db.child('users').child(aut['displayName'])
                user_data = user_ref.get(au['idToken']).val()
                name = user_data['name']
                birth = user_data['birth']
                pnum = user_data['pnum']
                dados_login = {'nome_de_usuario': nome_de_usuario, 
                            'email': user, 
                            'senha': password,
                            'nome': name,
                            'nasc': birth,
                            'pnum': pnum}
                with open('dados_login.json', 'w') as f:
                    json.dump(dados_login, f)
                self.root.current = "main"
            else:
                self.root.current = "main"
            return True
def atualiza_dados_app(self):
    with open('dados_login.json', 'r') as f:
        dados_login = json.load(f)
    self.user = dados_login['nome_de_usuario']
    self.nam = dados_login['nome']
    self.mail = dados_login['email']
    self.nasc = dados_login['nasc']
    self.pnum = dados_login['pnum']
    self.root.get_screen('main').ids.username.text = f"{self.user}"
    self.root.get_screen('main').ids.mail.text = f"{self.mail}"
    self.root.get_screen('main').ids.pnum.text = f"{self.pnum}"
    self.root.get_screen('main').ids.birth.text = f"{self.nasc}"
    self.root.get_screen('main').ids.name.text = f"{self.nam}"

def limpar_dados_login():
    with open('dados_login.json', 'w') as f:
        json.dump({}, f)