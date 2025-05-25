import requests
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from screens import (HomeScreen, LoginScreen, RegisterScreen, ForgetPasswordScreen,CreatePasswordScreen, SuccessScreen, ScanScreen, CameraScreen, 
                     AdminScreen, ChatBotWelcomeScreen, ChatBotScreen, VerificationScreen, MenuScreen, ProfileScreen, AboutScreen, TermsOfUseScreen, 
                     LanguageScreen, PrivacyScreen, ChangeUsernameScreen, ChangeEmailScreen, ChangePasswordScreen, ChangeNumberScreen, DeleteAccountScreen,
                     AddQrCode, QuestionScreen, ShowClientScreen, RendezVous)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.text import LabelBase
from kivymd.toast import toast
from kivy.uix.textinput import TextInput
import re
import sys
from kivy.storage.jsonstore import JsonStore
import os


# Ajouter le dossier racine au PYTHONPATH
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

LabelBase.register(name="Poppins", fn_regular="assets/Poppins-Regular.ttf")

class MyApp(MDApp):
    store = JsonStore('qr_data.json') 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_history = []  # Initialisation de l'historique ici
        self.exit_attempt = False 

    def move_focus(self, current_field: TextInput, next_field: TextInput, prev_field: TextInput):
        """
        Gère la navigation automatique entre les champs.
        - Passe au champ suivant après saisie.
        - Revient au champ précédent après suppression.
        """
        if len(current_field.text) > 1:
            current_field.text = current_field.text[:1]

        if len(current_field.text) == 1 and next_field:
            next_field.focus = True  # Aller au champ suivant

        elif len(current_field.text) == 0 and prev_field:
            prev_field.focus = True  # Retourner au champ précédent

    def filter_spaces_and_tabs(self, instance, value):
        # Supprimer les espaces et les tabulations du texte saisi
        instance.text = value.replace(" ", "").replace("\t", "")
    def open_menu(self):
        MDApp.get_running_app().navigate("menu_screen")
    
    def add_screens(self):
        screen_classes = [
            (HomeScreen, "home_screen"),
            (LoginScreen, "login_screen"),
            (RegisterScreen, "register_screen"),
            (ForgetPasswordScreen, "forget_screen"),
            (CreatePasswordScreen, "create_password_screen"),
            (SuccessScreen, "success_screen"),
            (ScanScreen, "scan_screen"),
            (CameraScreen, "camera_screen"),
            (AdminScreen, "admin_screen"),
            (ChatBotWelcomeScreen, "chatbot_welcome_screen"),
            (ChatBotScreen, "chatbot_screen"),
            (VerificationScreen, "verification_screen"),
            (MenuScreen, "menu_screen"),
            (ProfileScreen, "profile_screen"),
            (AboutScreen, "about_screen"),
            (TermsOfUseScreen, "terms_of_use_screen"),
            (LanguageScreen, "language_screen"),
            (PrivacyScreen, "privacy_screen"),
            (ChangeUsernameScreen, "change_username"),
            (ChangeEmailScreen, "change_email"),
            (ChangePasswordScreen, "change_password"),
            (ChangeNumberScreen, "change_number"),
            (DeleteAccountScreen, "delete_account"),
            (AddQrCode, "add_qrcode"),
            (QuestionScreen, "question_screen"),
            (ShowClientScreen, "show_client_screen"),
            (RendezVous, "rendez_vous")
        ]

        for cls, name in screen_classes:
            self.screen_manager.add_widget(cls(name=name))

        for _, kv_name in screen_classes:
            kv_file_path = os.path.join(os.path.dirname(__file__), 'screens', f'{kv_name}.kv')
            if os.path.exists(kv_file_path) and os.path.getsize(kv_file_path) > 0:
                # print(f"Chargement du fichier : {kv_file_path}")
                # try:
                Builder.load_file(kv_file_path)
                # except Exception as e:
                #     print(f"Erreur lors du chargement du fichier {kv_file_path}: {e}")
                #     raise  # Relance l'exception pour arrêter l'exécution et afficher la trace complète
            else:
                print(f"Le fichier {kv_file_path} n'existe pas ou est vide.")
    
    def build(self):
        self.title = "SEZAIA"
        self.icon = "assets/sezaia_logo.jpg"
        self.theme_cls.primary_palette = "Blue"
        self.screen_history = []
        self.screen_manager = ScreenManager()
        self.screen_manager.transition.direction = "right"
        Builder.load_file("widgets/widget.kv")
        self.add_screens()
        return Builder.load_file('myapp.kv')
   

    def navigate(self, screen_name):
        # Enregistrer l'écran actuel dans l'historique avant de naviguer
        if self.root.current != "":
            self.screen_history.append(self.root.current)
        # Naviguer vers la nouvelle page
        self.root.current = screen_name

    def go_back(self):
        # Vérifier si l'historique contient des pages précédentes
        if self.screen_history:
            # Revenir à l'écran précédent enregistré dans l'historique
            previous_screen = self.screen_history.pop()
            self.root.current = previous_screen
            self.screen_manager.transition.direction = "right" 
        else:
            if not self.exit_attempt:
                # Première tentative de retour : demander confirmation
                self.exit_attempt = True
                toast("Click again to exit")
            else:
                # Deuxième tentative : quitter l'application
                self.get_running_app().stop()

    def get_previous_screen(self):
        """ Récupère le dernier écran visité sans le retirer de l'historique """
        if self.screen_history:
            return self.screen_history[-1]  # Renvoie le dernier écran sans le supprimer
        return None  # Aucun écran précédent disponible

    def show_popup(self, title, message):
        # Crée un BoxLayout pour organiser les éléments verticalement
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Crée un AnchorLayout pour centrer le message
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        message_label = Label(text= str(message), size_hint_y=None, height=100, halign='center', valign='middle')
        anchor.add_widget(message_label)
        content.add_widget(anchor)

        # Crée un bouton pour fermer le pop-up
        close_button = Button(text="Close", size_hint_y=None, height=50)
        close_button.bind(on_press=self.close_popup)
        content.add_widget(close_button)

        # Crée le Popup avec le titre, le contenu, et la taille
        self.popup = Popup(title=title, content=content, size_hint=(0.6, 0.4))
        self.popup.open()

    def close_popup(self, instance):
        # Ferme le Popup
        self.popup.dismiss()

    def reset_input_colors(self,color,clear,fields):
        screen = self.root.get_screen(self.root.current)
        for field_id in fields:
            field_widget = screen.ids.get(field_id) 
            if field_widget:
                field_widget.line_color_normal = color
                field_widget.text_color_normal = color
                field_widget.hint_text_color_normal = color
                field_widget.icon_right_color_normal = color
            if clear == True:
                field_widget.text = ""

if __name__ == "__main__":
    Window.clearcolor = (1, 1, 1, 1) 
    MyApp().run()
