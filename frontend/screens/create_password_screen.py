from kivy.uix.filechooser import Screen
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL


class CreatePasswordScreen(Screen): 
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = [
            'password_forget', 'confirm_password_forget'
        ]
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.password_forget.focus = True
        return super().on_pre_enter(*args)
    
    def reset_action(self):
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        email = self.manager.get_screen('forget_screen').ids.email_forget.text
        password = self.ids.password_forget.text
        confirm_password = self.ids.confirm_password_forget.text
        url = API_BASE_URL + "/change-password"
        try:
            response = requests.post(
                url,
                json={"email": email, "new_password": password, "confirm_password" : confirm_password},
            )
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.app.navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), False, self.fields)
                toast(data['message'])
        except Exception as e:
            toast(data['message'])