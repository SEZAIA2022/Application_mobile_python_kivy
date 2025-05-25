from kivy.uix.filechooser import Screen
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL

class ChangeEmailScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = ['password', 'email_change', 'new_email_change']
        super().__init__(**kw)


    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.email_change.focus = True 
        return super().on_pre_enter(*args)
    def change_email(self):
        email = self.ids.email_change.text
        new_email = self.ids.new_email_change.text
        password = self.ids.password.text
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        url = API_BASE_URL + "/change_email"
        try:
            response = requests.post(
                url,
                json={"email": email, "new_email": new_email, "password": password},
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
        