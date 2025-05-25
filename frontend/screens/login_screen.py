from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout 
import requests
from kivy.app import App
from config import API_BASE_URL


class LoginScreen(Screen):
    
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = [
            'password_input', 'user_input'
        ]
        super().__init__(**kw)
        
    def on_pre_enter(self, *args):
        self.manager.get_screen('menu_screen').ids.profile.disabled = True
        self.manager.get_screen('menu_screen').ids.logout.disabled = True
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        self.ids.user_input.focus = True
        return super().on_pre_enter(*args)

    def login_action(self):
        username = self.ids.user_input.text
        password = self.ids.password_input.text
        url = API_BASE_URL + "/login"
        # Envoie les informations d'identification au backend Flask
        response = requests.post(url, json={
            'username': username,
            'password':password
})
        data = response.json()
        if response.status_code == 200:    
            if data['role'] == 'admin':
                    self.manager.get_screen('menu_screen').ids.profile.disabled = False
                    self.manager.get_screen('menu_screen').ids.logout.disabled = False
                    self.app.navigate("admin_screen")  # Redirige vers la page administration
            elif data['role'] == 'user':
                    self.manager.get_screen('menu_screen').ids.profile.disabled = False
                    self.manager.get_screen('menu_screen').ids.logout.disabled = False
                    self.app.navigate("scan_screen")  # Redirige vers la page utilisateur        
        else:
            self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
            self.app.show_popup("Erreur", data['message'])