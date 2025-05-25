from kivy.uix.filechooser import Screen
import requests
from kivymd.toast import toast
from kivy.app import App
from config import API_BASE_URL

class ChangeNumberScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        self.fields = [
            'password', 'country_code_change', 'new_country_code_change', 
            'phone_change', 'new_phone_change'
        ]
        super().__init__(**kw)
    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.country_code_change.focus = True 
        return super().on_pre_enter(*args)
    def change_number(self):
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        phone = self.ids.phone_change.text
        code = self.ids.country_code_change.text
        new_code = self.ids.new_country_code_change.text
        new_phone = self.ids.new_phone_change.text
        password = self.ids.password.text
        url = API_BASE_URL + "/change_number"
        try:
            
            response = requests.post(
                url, 
                json={"phone": phone,"new_phone": new_phone,"code":code, "new_code":new_code ,"password": password},
            )
            data = response.json()
            if response.status_code == 200:
                toast(data['message'])
                self.manager.get_screen('success_screen').ids.label_title.text = "Phone number changed "
                self.manager.get_screen('success_screen').ids.label_content.text = "[i]Congratulations ! Your phone number has been changed successfully.[/i]"
                App.get_running_app().navigate("success_screen")
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
                toast(data['message'])
        except Exception as e:
            toast(f"Error: {e}")