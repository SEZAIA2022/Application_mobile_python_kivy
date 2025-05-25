from kivy.uix.filechooser import Screen
from kivy.uix.behaviors.touchripple import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.toast import toast
from kivy.uix.popup import Popup
import requests
from kivy.app import App  # Importer la classe App
from config import API_BASE_URL

class ForgetPasswordScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = ['email_forget']
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.email_forget.focus = True
        return super().on_pre_enter(*args)
    def verification_action(self):
        email = self.ids.email_forget.text
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        url = API_BASE_URL + "/forgot_password"
        # Envoie les informations d'identification au backend Flask
        response = requests.post(url, json={
            'email': email  
        })
        data = response.json()

        if response.status_code == 200:
            # Récupération du token JWT
            token = response.json().get('token')
            # Sauvegarder le token dans un endroit sûr
            self.manager.get_screen('verification_screen').token = token
            toast(data['message'])
            self.app.navigate("verification_screen")
        else:
            self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
            self.app.show_popup("Erreur", data['message'])