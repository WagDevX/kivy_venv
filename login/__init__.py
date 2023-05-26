import json
import pyrebase




firebaseConfig = {
    "apiKey": "",
    "authDomain": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": "",
    "databaseURL": ""
  }

def verifica_dados_firebase(self, user, password, logado_antes=False):
        if logado_antes:
            self.root.current = "main"
            return
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        au = auth.sign_in_with_email_and_password("admin@admin.com.br", "123456") 
        try:
            aut = auth.sign_in_with_email_and_password(user, password)
            if logado_antes == False:
                nome_de_usuario = aut['displayName']
                user_ref = db.child('users').child(aut['displayName'])
                user_data = user_ref.get(au['idToken']).val()
                name = user_data['name']
                birth = user_data['birth']
                pnum = user_data['pnum']
                setor = user_data['setor']
                dados_login = {'nome_de_usuario': nome_de_usuario, 
                            'email': user, 
                            'senha': password,
                            'nome': name,
                            'nasc': birth,
                            'pnum': pnum,
                            'setor': setor}
                with open('dados_login.json', 'w') as f:
                    json.dump(dados_login, f)   
                self.root.current = "main"
        except Exception:
            self.show_alert_login()
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
    self.setor = dados_login['setor']
    self.usuario_logado = self.user
    self.setor = self.setor
    self.root.get_screen('main').ids.username.text = f"{self.user}"
    self.root.get_screen('main').ids.mail.text = f"{self.mail}"
    self.root.get_screen('main').ids.pnum.text = f"{self.pnum}"
    self.root.get_screen('main').ids.birth.text = f"{self.nasc}"
    self.root.get_screen('main').ids.name.text = f"{self.nam}"
    self.root.get_screen('main').ids.setor.text = f"{self.setor}"

def limpar_dados_login():
    with open('dados_login.json', 'w') as f:
        json.dump({}, f)
