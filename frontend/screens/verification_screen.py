import jwt
from kivy.uix.filechooser import Screen
import requests
from kivy.app import App
from kivymd.toast import toast
from config import API_BASE_URL
SECRET_KEY = "SEZAIA2022"

class VerificationScreen(Screen):
    token = None  # Pour stocker temporairement le token JWT
    def __init__(self, **kw):
        super().__init__(**kw)  # Assurez-vous que l'écran est initialisé avant
        self.app = App.get_running_app()
        self.fields = ['otp_input_1', 'otp_input_2', 'otp_input_3', 'otp_input_4']

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.otp_input_1.focus = True 
        return super().on_pre_enter(*args)

    def verify_action(self):
        prev_screen = self.app.get_previous_screen()  # Maintenant, cet appel fonctionnera
        otp = self.ids.otp_input_1.text + self.ids.otp_input_2.text + self.ids.otp_input_3.text + self.ids.otp_input_4.text
        # Récupérer les valeurs des champs de saisie
        if prev_screen == 'forget_screen':
            url = API_BASE_URL + "/verify_forget"
            response = requests.post(url, json={
                "otp": otp,
                "token": self.token  # Envoi du token pour vérifier l'OTP
            })
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.app.navigate("create_password_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)    
                self.ids.otp_input_1.focus = True    
                toast(data['message'])
        elif prev_screen == 'register_screen':
            email = self.manager.get_screen('register_screen').ids.email_register.text
            url = API_BASE_URL + "/verify_register"
            response = requests.post(url, json={
                "email": email,
                "otp": otp,
                "token": self.token  # Envoi du token pour vérifier l'OTP
            })
            data = response.json()
            if response.status_code == 200:
                self.manager.get_screen('success_screen').ids.label_title.text = "New account created "
                self.manager.get_screen('success_screen').ids.label_content.text = "[i]Congratulations ! Your account has been created successfully.[/i]"
                self.app.navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields) 
                self.ids.otp_input_1.focus = True    
                toast(data['message'])
        elif prev_screen == 'change_email':
            new_email = self.manager.get_screen('change_email').ids.new_email_change.text
            url = API_BASE_URL + "/verify_change_email"
            response = requests.post(url, json={
                "email":new_email,
                "otp": otp,
                "token": self.token  # Envoi du token pour vérifier l'OTP
            })
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.manager.get_screen('success_screen').ids.label_title.text = "Email changed "
                self.manager.get_screen('success_screen').ids.label_content.text = "[i]Congratulations ! Your email has been changed successfully.[/i]"
                self.app.navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)     
                self.ids.otp_input_1.focus = True   
                toast(data['message'])
        elif prev_screen == 'delete_account':
            email = self.manager.get_screen('delete_account').ids.email_delete.text
            url = API_BASE_URL + "/delete_account"
            response = requests.post(url, json={
                "email":email,
                "otp": otp,
                "token": self.token  # Envoi du token pour vérifier l'OTP
            })
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.manager.get_screen('success_screen').ids.label_title.text = "Account Deleted "
                self.manager.get_screen('success_screen').ids.label_content.text = "[i]Your account has been deleted successfully.[/i]"
                self.app.navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)     
                self.ids.otp_input_1.focus = True   
                toast(data['message'])
    
    def resend_otp(self):
        token = self.token  # Assurez-vous que le token est accessible ici
        prev_screen = self.app.get_previous_screen()  # Maintenant, cet appel fonctionnera

        try:
            # Décodage du JWT
            payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
            
            # Récupération de l'email en fonction de l'écran précédent
            if prev_screen == 'forget_screen':
                email = payload['email']
            elif prev_screen == 'register_screen':
                email = self.manager.get_screen('register_screen').ids.email_register.text
            elif prev_screen == 'change_email':
                email = self.manager.get_screen('change_email').ids.new_email_change.text
            elif prev_screen == 'delete_account':
                email = self.manager.get_screen('delete_account').ids.email_delete.text

            self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
            url = API_BASE_URL + "/resend_otp"        
            
            try:
                response = requests.post(url, json={"token": token, 'email': email})
                
                if response.status_code == 200:
                    self.ids.otp_input_1.focus = True
                    data = response.json()
                    toast(data["message"])
                    # Mettre à jour le token après avoir reçu la réponse
                    self.token = data["token"]  # Le nouveau token est envoyé avec la réponse
                else:
                    data = response.json()  # Si l'API retourne une erreur, nous la récupérons ici
                    toast(data["message"])
                    
            except requests.exceptions.RequestException as e:
                toast(f"Error during API call: {str(e)}")
            except ValueError:
                toast("Error: Malformed response, the server did not return JSON.")
            
        except jwt.ExpiredSignatureError:
            self.app.navigate("delete_account")
            toast("The token has expired. Please log in again.")
        except jwt.InvalidTokenError:
            toast("Invalid token. Please log in and try again.")
        except Exception as e:
            toast(f"An unexpected error occurred: {str(e)}")


        