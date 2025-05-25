import smtplib
from kivymd.uix.list import OneLineListItem
from kivy.uix.screenmanager import Screen
from kivy.app import App
from config import API_BASE_URL
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.menu import MDDropdownMenu
import requests
import json
from kivy.storage.jsonstore import JsonStore
from kivymd.toast import toast


def send_response_to_api(question_id, response_text, username, qr_code):
    url = f"{API_BASE_URL}/save_response"
    try:
        data = {'question_id': question_id, 'response': response_text, 'username': username, 'qr_code': qr_code}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(response.json().get('message', 'Response saved successfully.'))
        else:
            print(f"Error saving response: {response.json().get('message', 'Unknown error.')}")
            toast(f"Error: {response.json().get('message', 'Unknown error.')}")
    except requests.exceptions.RequestException as e:
        print(f"Error while communicating with the API: {e}")
        toast(f"API request error: {e}")

def send_ask(username, qr_code, tech_name, date, comment):
    url = f"{API_BASE_URL}/send_ask"
    try:
        data = {'username': username, 'qr_code': qr_code, 'tech_name': tech_name, 'date': date, 'comment': comment}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(response.json().get('message', 'Request sent successfully.'))
        else:
            print(f"Error sending ask: {response.json().get('message', 'Unknown error.')}")
            toast(f"Error: {response.json().get('message', 'Unknown error.')}")
    except requests.exceptions.RequestException as e:
        print(f"Error while communicating with the API: {e}")
        toast(f"API request error: {e}")
def send_info_email(to_email, message):
    sender_email = "hseinghannoum@gmail.com"
    sender_password = "ehybppmrmbueakgo"
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        message = f"Subject: Votre demande de maintenance\n\nVotre code OTP est : {message}"
        server.sendmail(sender_email, to_email, message)

def get_email(username):
    url = API_BASE_URL + "/email"  # L'URL de votre API Flask

    # Données envoyées au serveur sous forme de JSON
    data = {'username': username}

    try:
        # Envoi de la requête POST avec les données
        response = requests.post(url, json=data)

        # Si la requête est réussie
        if response.status_code == 200:
            # Récupération de l'email depuis la réponse JSON
            email = response.json().get('email')
            return email
        else:
            # Si l'utilisateur n'est pas trouvé ou il y a une erreur
            message = response.json().get('message', 'Unknown error')
            return None

    except requests.exceptions.RequestException as e:
        print(f"Une erreur est survenue lors de la requête : {e}")
        return None

class RendezVous(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = App.get_running_app()
        self.fields = ['date_label']
        self.techniciens = []  # Stocke la liste des techniciens globalement

    def city_menu_callback(self, text_item):
        if "city_label" in self.ids:
            self.ids.city_label.text = text_item
            self.ids.tech_label.text = ""
            self.update_technicians_list()  # Met à jour la liste des techniciens lorsque la ville change
        self.menu.dismiss()

    def tech_menu_callback(self, text_item):
        if "tech_label" in self.ids:
            self.ids.tech_label.text = text_item  # Mise à jour de l'étiquette du technicien
        self.menu.dismiss()


    def update_technicians_list(self):
        """
        Met à jour la liste des techniciens en fonction de la ville sélectionnée.
        """
        # Filtrer les techniciens en fonction de la ville sélectionnée
        selected_city = self.ids.city_label.text if "city_label" in self.ids else ""
        tech_city = [
            tech['name'] for tech in self.techniciens 
            if tech.get('ville') and tech['ville'] == selected_city
        ]
        
        # Création des éléments du menu pour les techniciens
        menu_techs = [
            {
                "text": tech,  
                "viewclass": "OneLineListItem",
                "on_release": lambda x=tech: self.tech_menu_callback(x)
            } for tech in tech_city
        ]
        
        # Vérifie si `tech_label` existe dans `self.ids` avant de créer le menu
        if "tech_label" in self.ids:
            self.tech = MDDropdownMenu(
                caller=self.ids.tech_label,
                position="bottom",
                items=menu_techs,
                hor_growth= 'right',
                width_mult=4
                
            )
        else:
            print("Attention : `tech_label` n'est pas trouvé dans self.ids.")

    def on_pre_enter(self, *args):
        # Reset des couleurs des champs de saisie
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)

        # Récupération des techniciens via l'API
        url = f"{API_BASE_URL}/techniciens"  # URL correcte de l'API Flask
        try:
            response = requests.get(url)
            response.raise_for_status()  # Vérifie les erreurs HTTP
            self.techniciens = response.json()  # Convertir en JSON et stocker dans une variable d'instance
        except requests.exceptions.RequestException as e:
            print(f"Error fetching technicians: {e}")
            toast(f"Error fetching technicians: {e}")

        # Récupération des villes des techniciens
        cities = [tech['ville'] for tech in self.techniciens if 'ville' in tech]

        # Création des éléments du menu pour les villes
        menu_cities = [
            {
                "text": city, 
                "viewclass": "OneLineListItem",
                "on_release": lambda x=city: self.city_menu_callback(x)
            } for city in cities
        ]

        # Vérifie si `city_label` existe dans `self.ids` avant d'assigner `caller`
        if "city_label" in self.ids:
            self.menu = MDDropdownMenu(
                caller=self.ids.city_label,
                position="bottom",
                items=menu_cities,
                hor_growth= 'right',
                width_mult=4
            )
        else:
            print("Attention : `city_label` n'est pas trouvé dans self.ids.")

        # Initialisation de la liste des techniciens pour la première ville sélectionnée
        self.update_technicians_list()
        
    def on_save(self, instance, value, date_range):
        if "date_label" in self.ids:
            self.ids.date_label.text = str(value)

    def on_cancel(self, instance, value):
        if "date_label" in self.ids:
            self.ids.date_label.text = "you clicked cancel"

    def show_date_picker(self):
        if not hasattr(self, "date_dialog"):  # Vérifie si le Date Picker existe déjà
            self.date_dialog = MDDatePicker()
            self.date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        self.date_dialog.open()
  

    def save(self, instance=None):
        try:
            # Charger les réponses stockées
            store = JsonStore("responses.json")
            if store.exists("user_responses"):

                responses = store.get("user_responses")["responses"]
                
                # Envoyer chaque réponse à l'API
                for response_data in responses:
                    username = response_data['username']
                    qr_code = response_data['qr_code']
                    email = get_email(username)
                    send_response_to_api(
                        response_data['question_id'],
                        response_data['response'],
                        response_data['username'],
                        response_data['qr_code']
                    )
                date = self.ids.date_label.text
                comment = self.ids.text_input.text
                tech_name = self.ids.tech_label.text
                send_ask(username, qr_code, tech_name, date, comment)
                send_info_email(email, username)
                # Mise à jour de l'interface utilisateur
                self.manager.get_screen('success_screen').ids.label_title.text = "Your request has been successfully registered!"
                self.manager.get_screen('success_screen').ids.label_content.text = "Responses sent successfully."
                
                # Navigation vers la page de succès
                App.get_running_app().navigate("success_screen")
            
            else:
                toast("No responses found. Please fill the form first.")
        
        except Exception as e:
            print(f"Error sending responses: {e}")
            toast("An error occurred while sending responses. Please try again.")
