from kivy.uix.filechooser import Screen
from kivy.app import App


class MenuScreen(Screen):
    def __init__(self, **kw):
        self.app = App.get_running_app()
        super().__init__(**kw)
    def logout(self):
        self.manager.get_screen('login_screen').ids.user_input.text = ""
        self.manager.get_screen('login_screen').ids.password_input.text = ""
        self.app.navigate("login_screen")
