from kivy.uix.filechooser import Screen
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL


class ChangePasswordScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = [
            'email', 'old_password', 'new_password', 'confirm_new_password'
        ]
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.email.focus = True
        return super().on_pre_enter(*args)
    
    def change_password(self):
        email = self.manager.get_screen('change_password').ids.email.text
        password = self.ids.old_password.text
        new_password = self.ids.new_password.text
        confirm_password = self.ids.confirm_new_password.text
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        url = API_BASE_URL + "/change_password"

        try:
            response = requests.post(
                url,
                json={"email": email, "new_password": new_password, "password":password, 'confirm_new_password':confirm_password},
            )
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.app.navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
                toast(data['message'])

        except Exception as e:
            toast(f"Error: {e}")