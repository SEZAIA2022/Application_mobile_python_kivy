from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock, mainthread
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from kivymd.toast import toast
import uuid 
import threading
import time
from kivy.storage.jsonstore import JsonStore  # Importation de JsonStore
from config import API_BASE_URL
import requests



class CameraScreen(Screen):
    qr_data = StringProperty("")
    last_sent_data = None
    token = StringProperty("")  # Propriété pour stocker le token
    store = JsonStore('qr_data.json') 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.capture = None
        self.running = False
        self.camera_thread = None

    def on_enter(self):
        """Appelé lorsque l'écran devient actif."""
        self.start_camera()

    def start_camera(self):
        if not self.running:
            self.running = True
            self.camera_thread = threading.Thread(target=self.camera_loop, daemon=True)
            self.camera_thread.start()
            self.ids.scan_status.text = "Scanning QR Code..."

    def camera_loop(self):
        """Boucle de capture vidéo dans un thread séparé."""
        try:
            self.capture = cv2.VideoCapture(0)
            if not self.capture.isOpened():
                raise RuntimeError("Unable to open the camera.")
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Réduire la résolution
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            while self.running:
                ret, frame = self.capture.read()
                if not ret:
                    continue
                self.process_frame(frame)
                time.sleep(0.1)  # Ajustez selon les performances
        except Exception as e:
            self.update_status(f"Camera error: {str(e)}")

    @mainthread
    def process_frame(self, frame):
        """Traite et met à jour l'interface utilisateur."""
        prev_screen = self.app.get_previous_screen() 
        
        try:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded_objects = decode(gray_frame)

            for obj in decoded_objects:
                points = obj.polygon
                if len(points) == 4:
                    pts = [(point.x, point.y) for point in points]
                    cv2.polylines(frame, [np.array(pts, np.int32)], isClosed=True, color=(255, 0, 0), thickness=3)

                self.qr_data = obj.data.decode("utf-8")
                self.ids.scan_status.text = "QR Code Detected!"
                self.last_sent_data = self.qr_data
                # Créer un token unique pour cette transaction
                self.token = str(uuid.uuid4())
                if prev_screen == 'admin_screen':
                    url = API_BASE_URL + "/exist_qr"
                    response = requests.post(url,json={
                        'qr_code': self.qr_data  
                    })
                    message = response.json().get('message', '')
                    if response.status_code == 200:
                        next_screen = 'admin_screen'
                        toast(message)
                    else:
                        self.manager.get_screen('add_qrcode').ids.qr_code.text=self.qr_data
                        next_screen = 'add_qrcode'
                    
                    self.app.navigate(next_screen)
                    
                elif prev_screen == 'scan_screen':
                    next_screen = 'chatbot_welcome_screen'
                    # Sauvegarder le QR code et le token dans le fichier JSON via JsonStore
                    self.store.put('qr_code_data', qr_code=self.qr_data, token=self.token)
                    self.app.navigate(next_screen)

            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
            if "camera_image" in self.ids:
                self.ids.camera_image.texture = texture

        except Exception as e:
            self.update_status(f"Erreur de traitement: {str(e)}")

    @mainthread
    def update_status(self, message):
        """Mise à jour du statut d'interface utilisateur."""
        self.ids.scan_status.text = message

    def on_leave(self):
        """Appelé lorsque l'écran est quitté."""
        self.stop_camera()

    def stop_camera(self):
        self.running = False
        if self.capture:
            self.capture.release()
            self.capture = None
        if self.camera_thread:
            self.camera_thread.join()        