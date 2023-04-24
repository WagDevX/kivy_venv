import pyrebase
from pyrebaseConfig import firebaseConfig
import json

def envia_dados_firebase(self, nome, mail, pnum, passw, users, birth):
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()
        db = firebase.database()
        user = auth.sign_in_with_email_and_password("admin@admin.com", "123456") 
        try:
            auth.create_user_with_email_and_password(mail, passw)
            data = {"name": nome,
                    "birth": birth,
                    "email": mail,
                    "pnum": pnum,
                    "user": users
                    }
            db.child("users").child(users).set(data, user['idToken'])
        except Exception:
            self.show_alert_login()
        else:
            self.root.transition.direction = "right"
            self.root.current = "login"
            return True
        
