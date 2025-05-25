from kivy.uix.screenmanager import Screen  
import requests
from kivy.app import App
from kivymd.toast import toast
from config import API_BASE_URL

class RegisterScreen(Screen):
    
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.fields = [
            "password_register", "confirm_password_register", "user_register", "email_register",
            "country_code", "phone_register", "address_register", "city_register", "postal_code_register"
        ]
        self.fields_pass = ["password_register", "confirm_password_register"]
        self.fields_user = ["user_register", "email_register"]

    def on_pre_enter(self, *args):
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.user_register.focus = True
        return super().on_pre_enter(*args)


    def verification_action(self):
        self.app.reset_input_colors((0, 0, 0, 0.38), False, self.fields)
        user_data = {
            "username": self.ids.user_register.text,
            "email": self.ids.email_register.text,
            "password": self.ids.password_register.text,
            "confirm_password": self.ids.confirm_password_register.text,
            "address": self.ids.address_register.text,
            "number": self.ids.phone_register.text,
            "postal_code": self.ids.postal_code_register.text,
            "city": self.ids.city_register.text,
            "country_code": self.ids.country_code.text,
        }

        url = f"{API_BASE_URL}/register"
        response = requests.post(url, json=user_data)
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            self.app.show_popup("Error", "Invalid server response.")
            return

        if response.status_code == 200:
            token = data.get('token')
            if token:
                self.manager.get_screen('verification_screen').token = token
                toast(data['message'])
                self.app.navigate("verification_screen")
            else:
                toast(data['message'])

        elif response.status_code == 450:
            self.app.reset_input_colors((1, 0, 0, 1), True, self.fields_pass)
            toast(data['message'])
            # Effacer les champs concernés
            for field in self.fields_pass:
                self.ids[field].text = ""

        elif response.status_code == 400 and data.get('status') == 'error':
            field_mapping = {
                'username': 'user_register',
                'email': 'email_register',
                'country_code': 'country_code',
                'number': 'phone_register',
                'address': 'address_register',
                'city': 'city_register',
                'postal_code': 'postal_code_register',
                'password': 'password_register',
                'confirm_password': 'confirm_password_register',
            }
            fields_in_error = []

            for error in data.get('errors', []):
                field_value = error.get('field')

                # Si 'field' est une liste
                if isinstance(field_value, list):
                    for field in field_value:
                        if field in field_mapping:
                            fields_in_error.append(field_mapping[field])
                
                # Si 'field' est une chaîne (cas simple)
                elif isinstance(field_value, str):
                    if field_value in field_mapping:
                        fields_in_error.append(field_mapping[field_value])

            self.app.reset_input_colors((1, 0, 0, 1), True, fields_in_error)
            self.app.show_popup("Error", data.get('message', 'Invalid input fields.'))

            # Effacer les champs concernés
            for field in fields_in_error:
                if field:  # Vérifier que le champ est valide
                    self.ids[field].text = ""

        else:
            error_message = data.get('message', 'An unexpected error occurred.')
            self.app.show_popup("Error", error_message)
