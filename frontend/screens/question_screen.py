import requests
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.toast import toast
from config import API_BASE_URL

class QuestionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.fields = ['new_question_text']
        self.selected_questions = []  # Stocke les IDs des questions cochées
        self.table = None  # Stocke la table

    def on_pre_enter(self):
        """Charge les questions à l'entrée de l'écran"""
        self.app.reset_input_colors((0, 0, 0, 0.38), True, self.fields)
        self.ids.new_question_text.focus = True
        self.load_questions()

    def load_questions(self):
        """Charge les questions depuis l'API et met à jour le tableau"""
        url = f"{API_BASE_URL}/questions"
        try:
            response = requests.get(url)
            questions = response.json()
            if response.status_code == 200:
                
                if isinstance(questions, list) and all('id' in q and 'text' in q for q in questions):
                    row_data = [(str(q["id"]), q["text"]) for q in questions]

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
                            ("[color=#FFFFFF]Questions[/color]", dp(150)),
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
                    toast(questions['message'])
            else:
                toast(questions['message'])

        except requests.exceptions.RequestException as e:
            print(f"Error while loading users: {e}")

    def row_checked(self, instance_table, current_row):
        """Gère la sélection des questions avec les cases à cocher"""
        try:
            question_id = current_row[0]  # Récupérer l'ID (première colonne)
            if question_id in self.selected_questions:
                self.selected_questions.remove(question_id)
            else:
                self.selected_questions.append(question_id)
        except Exception as e:
            print(f"Error during selection: {e}")

    def add_question(self):
        """Ajoute une nouvelle question via l'API"""
        new_question_text = self.ids.new_question_text.text.strip()
        if not new_question_text:
            toast("Please enter a question.")
            return

        url = f"{API_BASE_URL}/add_question"
        try:
            response = requests.post(url, json={"text": new_question_text})
            data = response.json()
            if response.status_code == 201:
                toast(data['message'])
                self.app.reset_input_colors((0, 0, 0, 0.38) , True, self.fields)
                self.load_questions()  # Recharge la liste des questions
            else:
                self.app.reset_input_colors((1, 0, 0, 1) , True, self.fields)
                toast(data['message'])
        except requests.exceptions.RequestException as e:
            print(f"Error while adding users: {e}")

    def delete_question(self):
        """Supprime les questions sélectionnées"""
        if not self.selected_questions:
            toast("No question selected for deletion")
            return

        for question_id in self.selected_questions:
            url = f"{API_BASE_URL}/delete_question/{question_id}"

            try:
                response = requests.delete(url)
                data = response.json()
                if response.status_code == 200:
                    toast(data['message'])
                else:
                    toast(data['message'])

            except requests.exceptions.RequestException as e:
                print(f"Error while deleting users: {e}")

        self.selected_questions.clear()
        self.load_questions()  # Recharge la liste après suppression
