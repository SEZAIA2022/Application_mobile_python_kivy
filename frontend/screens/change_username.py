from kivy.uix.filechooser import Screen
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL

class ChangeUsernameScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = ['password', 'user_change', 'new_user_change']
        super().__init__(**kw)

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.user_change.focus = True
        return super().on_pre_enter(*args)
    
    def change_username(self):
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        username = self.ids.user_change.text
        new_username = self.ids.new_user_change.text
        password = self.ids.password.text
        url = API_BASE_URL + "/change_username"
        try:
            
            response = requests.post(
                url,
                json={"username": username,"new_username": new_username, "password": password},
            )
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.manager.get_screen('success_screen').ids.label_title.text = "Username changed "
                self.manager.get_screen('success_screen').ids.label_content.text = "[i]Congratulations ! Your username has been changed successfully.[/i]"
                App.get_running_app().navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
                toast(data['message'])
        except Exception as e:
            toast(f"Error: {e}")