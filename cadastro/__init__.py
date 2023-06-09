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

def envia_dados_firebase(self, nome, mail, pnum, passw, users, birth, setor):
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        try:
            auth.create_user_with_email_and_password(mail, passw)
            
        except Exception:
            self.show_alert_login()
        else:
            user = auth.sign_in_with_email_and_password(mail, passw) 
            auth.update_profile(user['idToken'],display_name=f"{users}")
            data = {"name": nome,
                    "birth": birth,
                    "email": mail,
                    "pnum": pnum,
                    "user": users,
                    "setor": setor
                    }
            db.child("users").child(users).set(data, user['idToken'])
            self.root.transition.direction = "right"
            self.root.current = "login"
            return True
        
