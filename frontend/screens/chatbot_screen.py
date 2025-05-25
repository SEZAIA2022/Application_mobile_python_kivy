from kivy.uix.codeinput import TextInput
import requests
from kivy.uix.settings import text_type
from kivy.clock import Clock
from kivy.uix.filechooser import Screen
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton  # Ajout du bouton
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App
from kivymd.toast import toast
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Line
from config import API_BASE_URL
import json
from kivy.app import App
from kivy.storage.jsonstore import JsonStore


def calculate_size_hint_x(text):
    """
    Calcule size_hint_x en fonction de la longueur du texte.
    """
    base_length = 10  # Longueur de base pour un ajustement minimal
    max_size_hint = 0.75  # Taille maximale
    min_size_hint = 0.22  # Taille minimale
    scale_factor = 0.05  # Facteur de mise à l'échelle

    size_hint_x = min_size_hint + (len(text) - base_length) * scale_factor
    return max(min_size_hint, min(size_hint_x, max_size_hint))


# Widgets personnalisés
class Command(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "Poppins"
    font_size = 17


class Response(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "Poppins"
    font_size = 17


class ChatBotScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.question_index = 0
        self.final_message = "Thank you for answering all the questions!"
        self.responses = []  # Liste pour stocker les réponses de l'utilisateur

    def on_enter(self):
        self.questions_db = self.get_all_questions()
        self.question_index = 0
        self.ask_question()
    
    # Fonction pour récupérer toutes les questions depuis l'API en une seule requête
    def get_all_questions(self):
        url = API_BASE_URL + "/questions"
        try:
            response = requests.get(url) 
            if response.status_code == 200:
                return response.json()  # Retourne les questions sous forme de liste
            else:
                print(response.json().get("message", "Error retrieving questions."))
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error while retrieving the questions: {e}")
            return []


    def ask_question(self):
        # Vérifier s'il reste des questions
        if self.question_index < len(self.questions_db):
            current_screen = self.manager.get_screen(self.manager.current)
            question = self.questions_db[self.question_index]['text']  # Récupère la question actuelle
            self.ids.button_no.disabled= False
            self.ids.button_yes.disabled= False
            self.ids.button_no.opacity= 1
            self.ids.button_yes.opacity= 1
            self.ids.btn_chat.disabled= True
            current_screen.chat_list.add_widget(Command(text=question, size_hint_x=calculate_size_hint_x(question), halign="left"))
        else:
            self.display_final_message()

    def response(self, value, *args):
        username = self.manager.get_screen('login_screen').ids.user_input.text
        if self.app.store.exists('qr_code_data'):
            qr_code = self.app.store.get('qr_code_data')['qr_code']
        if value.lower() in ["yes", "no"]:
            current_question = self.questions_db[self.question_index]
            self.responses.append({
                "question_id": current_question['id'],
                "response": value,
                "username": username,
                "qr_code": qr_code
            })
            self.question_index += 1
            if self.question_index < len(self.questions_db):
                self.ask_question()
            else:
                self.display_final_message()
        else:
            toast("Please respond with 'yes' or 'no' only.")

    def send(self, value):
        current_screen = self.manager.get_screen(self.manager.current)
        self.ids.button_no.disabled= True
        self.ids.button_yes.disabled= True
        current_screen.chat_list.add_widget(Response(text=value, size_hint_x=calculate_size_hint_x(value), halign="center"))
        Clock.schedule_once(lambda dt: self.response(value), 2)

    def display_final_message(self):
        current_screen = self.manager.get_screen(self.manager.current)
        current_screen.chat_list.add_widget(Command(text=self.final_message, size_hint_x=calculate_size_hint_x(self.final_message), halign="left"))
        self.ids.button_no.disabled= True
        self.ids.button_yes.disabled= True
        self.ids.button_no.opacity= 0
        self.ids.button_yes.opacity= 0
        self.ids.btn_chat.disabled= False
        self.ids.btn_chat.opacity= 1

    def on_finish(self, instance=None):
        try:
            store = JsonStore("responses.json")
            store.put("user_responses", responses=self.responses)
            App.get_running_app().navigate("rendez_vous")
        
        except Exception as e:
            print(f"Error storing responses: {e}")
            toast("An error occurred while storing responses. Please try again.")
    
    def on_leave(self):
        self.ids.chat_list.clear_widgets()
        self.question_index = 0
        self.responses = []
        self.ids.button_no.disabled = False
        self.ids.button_yes.disabled = False
        self.ids.btn_chat.disabled= True
        self.ids.btn_chat.opacity= 0


