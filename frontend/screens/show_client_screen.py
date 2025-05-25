import requests
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.toast import toast
from config import API_BASE_URL

class ShowClientScreen(Screen):
    def __init__(self, **kwargs):
        self.app = App.get_running_app()
        self.fields=['new_user_text','new_email_text']
        self.selected_users = []  # Stocke les IDs des usernames cochées
        self.table = None  # Stocke la table
        self.role = ""
        super().__init__(**kwargs)
        

    def on_pre_enter(self):
        """Charge les users à l'entrée de l'écran"""
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        # self.ids.new_user_text.focus = True 
        self.load_users()

    def load_users(self):
        """Charge les users depuis l'API et met à jour le tableau"""
        url = f"{API_BASE_URL}/users"
        try:
            response = requests.get(url)
            users = response.json()
            if response.status_code == 200:

                if isinstance(users, list) and all('id' in q and 'role' in q and 'username' in q and 'email' in q for q in users):
                    row_data = [(str(q["id"]),  q["role"], q["username"], q["email"]) for q in users]

                    # Supprime l'ancienne table si elle existe
                    if self.table:
                        self.ids.table_container.remove_widget(self.table)

                    # Création du tableau
                    self.table = MDDataTable(
                        pos_hint={"center_x": 0.5, "center_y": 0.5},
                        size_hint=(0.9, 0.8),
                        background_color_header=(0.16, 0.25, 0.37, 1),
                        use_pagination=True,
                        check=True,
                        column_data=[
                            ("[color=#FFFFFF]Id[/color]", dp(30)),
                            ("[color=#FFFFFF]role[/color]", dp(20)),
                            ("[color=#FFFFFF]username[/color]", dp(40)),
                            ("[color=#FFFFFF]email[/color]", dp(60))
                            
                        ],
                        sorted_on="Schedule",
                        sorted_order="ASC",
                        elevation=2,
                        row_data=row_data
                    )

                    # Liaison des événements
                    self.table.bind(on_check_press=self.row_checked)

                    # Ajout du tableau à l'interface
                    self.ids.table_container.add_widget(self.table)
                else:
                    toast(users['message'])
            else:
                toast(users['message'])

        except requests.exceptions.RequestException as e:
            print(f"Error while loading users: {e}")

    def row_checked(self, instance_table, current_row):
        """Gère la sélection des users avec les cases à cocher"""
        try:
            if len(current_row) > 0:  # Vérifier que la ligne contient des données
                user_id = current_row[0]  # Récupérer l'ID (première colonne)
                if user_id in self.selected_users:
                    self.selected_users.remove(user_id)
                else:
                    self.selected_users.append(user_id)
        except Exception as e:
            print(f"Error during selection: {e}")

    def add_user(self):
        """Ajoute une nouvelle user via l'API"""
        new_user = self.ids.new_user_text.text.strip()
        new_email = self.ids.new_email_text.text.strip()
        role = self.role
        url = f"{API_BASE_URL}/add_user"
        try:
            response = requests.post(url, json={"username": new_user, "email": new_email, 'role': role})
            data = response.json()
            if response.status_code == 200:
                self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
                toast(data['message'])
                self.load_users()  # Recharge la liste des users
            else:
                self.app.reset_input_colors((1, 0, 0, 1), True, self.fields)
                toast(data['message'])
        except requests.exceptions.RequestException as e:
            print(f"Error while adding users: {e}")

    def delete_user(self):
        """Supprime les users sélectionnées"""
        if not self.selected_users:
            toast("No question selected for deletion")
            return


        for user_id in self.selected_users:
            url = f"{API_BASE_URL}/delete_user/{user_id}"
            try:
                response = requests.delete(url)
                data = response.json()
                if response.status_code == 200:
                    toast(data['message'])
                else:
                    toast(data['message'])
            except requests.exceptions.RequestException as e:
                print(f"Error while deleting users: {e}")

        self.selected_users.clear()
        self.load_users()  # Recharge la liste après suppression

    def on_checkbox_active(self, instance, value):
        """Callback pour gérer l'activation des cases à cocher."""
        if instance == self.ids.admin_checkbox:
            if self.ids.admin_checkbox.active:
                self.role = "admin"
                print(self.ids.admin.text)
                # Désactiver la case utilisateur si la case admin est activée
                self.ids.user_checkbox.active = False
        elif instance == self.ids.user_checkbox:
            if self.ids.user_checkbox.active:
                self.role = "user"
                print(self.ids.user.text)
                # Désactiver la case admin si la case utilisateur est activée
                self.ids.admin_checkbox.active = False

