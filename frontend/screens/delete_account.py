from kivy.uix.filechooser import Screen
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL

class DeleteAccountScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = ['password', 'email_delete', 'confirm_password']
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.email_delete.focus = True
        return super().on_pre_enter(*args)
    
    def delete_account(self):
        email = self.ids.email_delete.text
        confirm_password=self.ids.confirm_password.text
        password = self.ids.password.text
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        url = API_BASE_URL + "/verify_delete_account"

        try:
            response = requests.post(
                url,  
                json={"email": email, "password": password, "confirm_password": confirm_password},
            )
            data = response.json()
            if response.status_code == 200:
                token = data.get('token')
                self.manager.get_screen('verification_screen').token = token
                toast(data['message'])
                self.app.navigate("verification_screen")
            else :
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
                toast(data['message'])
        except Exception as e:
            toast(f"Error: {e}")