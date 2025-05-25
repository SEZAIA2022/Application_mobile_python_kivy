from kivy.uix.screenmanager import Screen  
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL

class AddQrCode(Screen):
    
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = ['user_qr', 'location_qr', "qr_code"]
        super().__init__(**kw)
       
    def on_pre_enter(self, *args):
        self.manager.get_screen('menu_screen').ids.profile.disabled = False
        self.manager.get_screen('menu_screen').ids.logout.disabled = False
        self.app.reset_input_colors((0, 0, 0, 0.38) , False, self.fields)
        self.ids.user_qr.focus = True 
        return super().on_pre_enter(*args)
   
    def add_qr(self):
        # Récupération des données saisies par l'utilisateur
        user_data = {
            "username": self.ids.user_qr.text,
            "location": self.ids.location_qr.text,
            "qr_code": self.ids.qr_code.text
        }
        url = API_BASE_URL + "/add_qr"
        # Envoi de la requête POST pour l'inscription
        response = requests.post(url, json=user_data)
        data = response.json()

        if response.status_code == 200:
            self.app.navigate("admin_screen")
            toast(data['message'])

        else:
            self.app.reset_input_colors((1, 0, 0, 1) , True, self.fields)
            toast(data['message'])

        
