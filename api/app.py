import os
from kivy.uix.filechooser import error
import jwt
from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime, timedelta
import random
import smtplib
import bcrypt
import re  # Pour valider le format des emails
from flask_cors import CORS  # Importation de CORS
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialisation de l'application Flask
app = Flask(__name__)
# Appliquer CORS à toute l'application
CORS(app)
# Clé secrète pour l'encodage et le décodage du JWT
SECRET_KEY = "SEZAIA2022"
# Mémoire temporaire pour les OTP
otp_storage = {}
# Mémoire temporaire pour les Informations de register
register_otp_storage = {}
# Configuration de la connexion à la base de données MySQL
db_config = {
    'user': 'root',        # Nom d'utilisateur MySQL
    'password': 'root',    # Mot de passe MySQL
    'host': '127.168.100.229',   # Hôte MySQL
    'database': 'projet_sezaia'  # Nom de la base de données
}


def parse_french_date(date_str):
    try:
        print(f"Original input date_str: {date_str}")

        # Extraire la date et l'heure (on enlève le jour de la semaine)
        parts = date_str.split(", ")
        if len(parts) < 2:
            raise ValueError("Format de date invalide.")

        date_part = parts[1]  # e.g. "02 June 16:43 08:00"
        # Prendre les 3 derniers éléments : jour, mois, heure (on suppose dernier est le bon)
        date_tokens = date_part.strip().split()

        # Gérer le cas où deux heures sont présentes (ex: "02 June 16:43 08:00")
        if len(date_tokens) >= 3:
            day = date_tokens[0]
            month = date_tokens[1]
            hour = date_tokens[-1]  # prendre la dernière heure
        else:
            raise ValueError("Format de date invalide")

        current_year = datetime.now().year
        full_date_str = f"{day} {month} {hour} {current_year}"

        # Parser
        dt = datetime.strptime(full_date_str, "%d %B %H:%M %Y")
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    except Exception as e:
        print("Error parsing date:", e)
        return None

# Fonction pour hasher un mot de passe
def hash_password(password: str) -> str:
    """
    Cette fonction prend un mot de passe en texte clair et le hache en utilisant bcrypt.
    """
    # Générer un "salt" (sel) pour rendre le hachage unique
    salt = bcrypt.gensalt()
    # Hacher le mot de passe avec le salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Fonction pour vérifier un mot de passe
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Cette fonction prend un mot de passe en texte clair et un mot de passe haché,
    puis vérifie s'ils correspondent.
    """
    # Comparer le mot de passe en clair avec le mot de passe haché
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# Fonction pour valider le mot de passe
def is_valid_password(password):
    import re
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

# Fonction d'envoi d'email avec OTP
def send_otp_email(to_email, otp):
    sender_email = "hseinghannoum@gmail.com"
    sender_password = "ehybppmrmbueakgo"
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        message = f"Subject: Votre code OTP\n\nVotre code OTP est : {otp}"
        server.sendmail(sender_email, to_email, message)

# Fonction pour obtenir la connexion à la base de données
def get_db_connection():
    """Établit une connexion à la base de données."""
    return mysql.connector.connect(**db_config)


@app.route('/api/endpoint', methods=['GET'])
def my_endpoint():
    return {"message": "Hello, world!"}


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': "No data received."}), 400
    
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username or email and password required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, username))
        users = cursor.fetchone()
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

    if not users:
        return jsonify({'status': 'error', 'message': "Incorrect username or password."}), 404

    try:
        hashed_password = users[2].encode('utf-8') if isinstance(users[2], str) else users[2]
        if verify_password(password, hashed_password):
            role = users[7]
            user = users[1]
            email = users[3]
            return jsonify({'status': 'success', 'message': "Login successful!", 'role': role, 'user': user, 'email': email}), 200
        else:
            return jsonify({'status': 'error', 'message': "Incorrect username or password."}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Processing error: {str(e)}'}), 500


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    required_fields = ["username", "email", "password", "confirm_password", "number", "address", "country_code", "city", "postal_code"]
    errors = []

    # Validation des champs obligatoires
    for field in required_fields:
        if not data.get(field):
            errors.append({'field': field, 'message': f"The field '{field.replace('_', ' ').capitalize()}' is required."})

    # Validation email
    email = data.get("email", "").strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    print(f"email register: {email}")  # DEBUG: Afficher l'email reçu
    if email and not re.match(email_regex, email):
        errors.append({'field': 'email', 'message': 'Invalid email format.'})

    # Validation mot de passe
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    if not is_valid_password(password):
        errors.append({'field': 'password', 'message': "Password must be at least 8 characters long, include an uppercase letter, a number, and a special character."})
    elif password != confirm_password:
        errors.append({'field': 'confirm_password', 'message': "Passwords do not match."})

    if errors:
        return jsonify({'status': 'error', 'message': 'Validation errors.', 'errors': errors}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérification si username ou email existe déjà dans users
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (data["username"], data["email"]))
        if cursor.fetchone():
            return jsonify({'status': 'error', 'message': "Username or email already exists."}), 400

        # Vérification si l'utilisateur est dans registred_users
        cursor.execute("SELECT * FROM registred_users WHERE username = %s OR email = %s", (data["username"], data["email"]))
        user_registred = cursor.fetchone()
        if not user_registred:
            return jsonify({'status': 'error', 'message': "Username or email can't be used."}), 400
        role = user_registred[3]

        # Génération OTP + hash password + expiration + tentatives
        otp = str(random.randint(1000, 9999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        password_hash = hash_password(password)
        if isinstance(password_hash, bytes):
            password_hash = password_hash.decode('utf-8')

        # Stockage sécurisé côté serveur
        register_otp_storage[email] = {
            'username': data['username'],
            'email': email,
            'password_hash': password_hash,
            'number': data['number'],
            'address': data['address'],
            'postal_code': data['postal_code'],
            'city': data['city'],
            'country_code': data['country_code'],
            'role': role,
            'otp': otp,
            'expires_at': expires_at,
            'attempts': 0
        }

        # Synchronisation avec otp_storage pour que resend_otp fonctionne
        otp_storage[email] = {
            'otp': otp,
            'expires_at': expires_at,
            'attempts': 0
        }

        send_otp_email(email, otp)

        return jsonify({"message": "OTP sent to your email."}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Server error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/verify_register', methods=['POST'])
def verify_register():
    data = request.get_json()
    otp = data.get('otp')
    email = data.get('email')
    if not otp:
        return jsonify({'status': 'error', 'message': 'OTP and email are required.'}), 400

    record = register_otp_storage.get(email)
    print(f"email record: {email}, record_otp: {record['otp']}")  # DEBUG: Afficher l'email et le record
    if not record:
        return jsonify({'status': 'error', 'message': 'No OTP found for this email.'}), 404
    
    MAX_ATTEMPTS = 5
    if record['attempts'] >= MAX_ATTEMPTS:
        del register_otp_storage[email]
        return jsonify({'status': 'error', 'message': 'Too many attempts. OTP blocked.'}), 429

    if datetime.utcnow() > record['expires_at']:
        del register_otp_storage[email]
        return jsonify({'status': 'error', 'message': 'OTP expired.'}), 400

    if record['otp'] != otp:
        record['attempts'] += 1
        return jsonify({'status': 'error', 'message': 'Incorrect OTP.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert l'utilisateur dans la base
        cursor.execute("""
            INSERT INTO users 
                (username, email, password_hash, phone_number, address, role, ville, code_postal, indicatif_telephonique)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            record['username'],
            record['email'],
            record['password_hash'],
            record['number'],
            record['address'],
            record['role'],
            record['city'],
            record['postal_code'],
            record['country_code']
        ))
        conn.commit()

        del register_otp_storage[email]

        return jsonify({'status': 'success', 'message': 'User successfully verified and registered.'}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f"MySQL error: {err}"}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def is_email_taken(new_email):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT 1 FROM users WHERE email = %s LIMIT 1"
        cursor.execute(query, (new_email,))
        result = cursor.fetchone()
        return result is not None  # True si email existe
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return True  # En cas d'erreur, on considère l'email comme pris par sécurité
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 🔍 Recherche l'utilisateur par email ou username
def get_user_by_email(email):
    # Chercher d'abord en base users
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT id, username, email FROM users WHERE email = %s OR username = %s"
        cursor.execute(query, (email, email))
        row = cursor.fetchone()

        if row:
            user = {
                'id': row[0],
                'username': row[1],
                'email': row[2]
            }
            return user

        # Si pas trouvé en base, chercher dans register_otp_storage
        record = register_otp_storage.get(email)
        if record:
            user = {
                'id': None,  # Pas encore en base
                'username': record['username'],
                'email': record['email']
            }
            return user

        return None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = get_user_by_email(email)
    if not user:
        return jsonify({'status': 'error', 'message': "User not found."}), 404
    email = user['email']
    print(f"email: {email}")  # DEBUG: Afficher l'email reçu
    if not email:
        return jsonify({'status': 'error', 'message': "Email or username required."}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'status': 'error', 'message': "User not found."}), 404

    otp = str(random.randint(1000, 9999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    otp_storage[email] = {'otp': otp, 'expires_at': expires_at,'attempts': 0}

    try:
        send_otp_email(user['email'], otp)
        return jsonify({'status': 'success', 'message': "OTP sent to your email."})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/verify_forget', methods=['POST'])
def verify_forget():
    data = request.get_json()
    otp = data.get('otp')
    email = data.get('email')
    user = get_user_by_email(email)
    if not user:
        return jsonify({'status': 'error', 'message': "User not found."}), 404
    email = user['email']
    print(f"email: {email}")  # DEBUG: Afficher l'email reçu
    if not otp or not email:
        return jsonify({'status': 'error', 'message': "OTP and email/username are required."}), 400

    record = otp_storage.get(user["email"])
    if not record:
        return jsonify({'status': 'error', 'message': "No OTP found for this user."}), 404

    # Limite des tentatives fixée à 5 par exemple
    MAX_ATTEMPTS = 5
    if record['attempts'] >= MAX_ATTEMPTS:
        del otp_storage[email]  # suppression pour bloquer définitivement ou temporairement
        return jsonify({'status': 'error', 'message': 'Too many attempts. OTP blocked.'}), 429

    if datetime.utcnow() > record['expires_at']:
        del otp_storage[email]
        return jsonify({'status': 'error', 'message': "OTP expired."}), 400

    if record['otp'] != otp:
        record['attempts'] += 1  # <-- Incrémenter ici
        return jsonify({'status': 'error', 'message': "Incorrect OTP."}), 400


    del otp_storage[email]
    return jsonify({'status': 'success', 'message': "User successfully verified."}), 200


@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    data = request.get_json()
    email = data.get('email')
    previous_page = data.get('previous_page')

    if not email:
        return jsonify({'status': 'error', 'message': "Email is required."}), 400

    user = get_user_by_email(email)

    new_otp = str(random.randint(1000, 9999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    if user:
        if previous_page == "SignUpActivity":
            # Mise à jour register_otp_storage
            record = register_otp_storage.get(email)
            if not record:
                return jsonify({'status': 'error', 'message': "User not found in registration storage."}), 404
            record['otp'] = new_otp
            record['expires_at'] = expires_at
            record['attempts'] = 0
            print(f"[DEBUG] OTP updated in register_otp_storage for {email}: {register_otp_storage[email]}")
        else:
            # Mise à jour otp_storage
            old_record = otp_storage.get(email, {})
            otp_storage[user["email"]] = {
                'otp': new_otp,
                'expires_at': expires_at,
                'attempts': 0,
                'new_email': old_record.get('new_email')
            }
            print(f"[DEBUG] OTP updated in otp_storage for {user['email']}: {otp_storage[user['email']]}")

    try:
        send_otp_email(user['email'], new_otp)
        print(f"[INFO] New OTP sent to {email}: {new_otp}")
        return jsonify({'status': 'success', 'message': "New OTP sent to your email."}), 200
    except Exception as e:
        print("Error sending OTP:", str(e))
        return jsonify({'status': 'error', 'message': f"Server error: {str(e)}"}), 500


@app.route('/questions', methods=['GET'])
def get_questions():
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()

        # Créer une liste de dictionnaires pour retourner les questions et leurs IDs
        questions_list = [{'id': row[0],'text': row[1]} for row in questions]

        return jsonify(questions_list)  # Retourne les questions sous forme de liste de dictionnaires

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


# Endpoint pour enregistrer la réponse
@app.route('/save_response', methods=['POST'])
def save_response():
    try:
        data = request.get_json()
        print("Received data:", data)  # DEBUG: Afficher les données reçues

        question_id = data.get('question_id')
        response_text = data.get('response')
        username = data.get('username')
        qr_code = data.get('qr_code')

        if not question_id or not response_text or not username or not qr_code:
            return jsonify({'status': 'error', 'message': "Missing data."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # DEBUG : Afficher la requête et les valeurs
        print(f"Inserting: {question_id}, {response_text}, {username}, {qr_code}")

        cursor.execute(
            "INSERT INTO responses (question_id, response, username, qr_code) VALUES (%s, %s, %s, %s)",
            (question_id, response_text, username, qr_code)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': "Response saved."}), 200

    except Exception as e:
        print("Error:", e)  # Affiche l'erreur complète dans la console
        return jsonify({'status': 'error', 'message': f'Erreur : {str(e)}'}), 500

    
@app.route('/send_ask', methods=['POST'])
def send_ask():
    try:
        data = request.get_json()
        print("Received data in send_ask:", data)

        username = data.get('username')
        date_str = data.get('date')  # format attendu: "Tuesday, 03 June 16:50"
        comment = data.get('comment')
        qr_code = data.get('qr_code')

        if not username or not date_str or not comment or not qr_code:
            return jsonify({'status': 'error', 'message': 'Missing data'}), 400

        try:
            # Extrait la partie utile
            parts = date_str.split(', ')
            if len(parts) != 2:
                raise ValueError("Expected format: 'DayName, dd MMMM HH:mm'")

            date_time_str = parts[1]  # '03 June 16:50'
            current_year = datetime.now().year
            full_datetime_str = f"{date_time_str} {current_year}"  # '03 June 16:50 2025'

            appointment_datetime = datetime.strptime(full_datetime_str, "%d %B %H:%M %Y")

        except Exception as parse_err:
            print("Error parsing date:", parse_err)
            return jsonify({'status': 'error', 'message': 'Invalid date format. Expected: dd MMMM HH:mm'}), 400

        # Séparer date et heure
        date_only = appointment_datetime.date()     # 2025-06-03
        time_only = appointment_datetime.time()     # 16:50:00

        print(f"Inserting into ask_repair: username={username}, date={date_only}, hour_slot={time_only}, comment={comment}, qr_code={qr_code}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ask_repair (username, date, hour_slot, comment, qr_code) VALUES (%s, %s, %s, %s, %s)",
            (username, date_only, time_only, comment, qr_code)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Ask repair saved'}), 200

    except Exception as e:
        print("Error in send_ask:", e)
        return jsonify({'status': 'error', 'message': f'Erreur : {str(e)}'}), 500
    

@app.route('/change-password', methods=['POST'])
def change_password_forget():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not email or not new_password or not confirm_password:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
    
    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Passwords do not match.'}), 400
    
    if not is_valid_password(new_password):
        return jsonify({
            'status': 'error', 'message': 'Password must be at least 8 characters, include an uppercase letter, a number, and a special character.'
        }), 400

    hashed_password = hash_password(new_password)

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, email))
        user = cursor.fetchone()

        if user:
            cursor.execute("""
                UPDATE users SET password_hash = %s WHERE email = %s OR username = %s
            """, (hashed_password, email, email))
            conn.commit()
            return jsonify({'message': 'Password updated successfully!'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Email not found.'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        cursor.close()
        conn.close()


@app.route('/change_username', methods=['POST'])
def change_username():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400
    new_username = data.get('new_username')
    username = data.get('username')
    password = data.get('password')
    if not username or not password or not new_username:
        return jsonify({'status': 'error', 'message': 'All champs requis'}), 400
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s ", (username,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

    if not user:
        return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 404
    # Récupération du mot de passe haché
    try:
        hashed_password = user[2].encode('utf-8') if isinstance(user[2], str) else user[2]
        if verify_password(password, hashed_password):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET username = %s WHERE username = %s
            """, (new_username, username))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Username changed!'}), 200
        else:
            return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 300
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Processing error.: {str(e)}'}), 500


@app.route('/change_email', methods=['POST'])
def change_email():
    data = request.get_json()
    print("Payload reçu:", data)  # Pour debug

    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400
    
    new_email = data.get('new_email')
    email = data.get('email')
    password = data.get('password')

    if not email or not password or not new_email:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email) or not re.match(email_regex, new_email):
        return jsonify({'status': 'error', 'message': 'The email format is invalid.'}), 400

    if email == new_email:
        return jsonify({'status': 'error', 'message': "New email cannot be the same as current email."}), 400

    if is_email_taken(new_email):
        return jsonify({'status': 'error', 'message': 'This email is already in use.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404

        hashed_password = user[0]
        hashed_password = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password

        if not verify_password(password, hashed_password):
            return jsonify({'status': 'error', 'message': 'Incorrect password.'}), 401

        otp = str(random.randint(1000, 9999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Stockage sécurisé côté serveur du OTP + new_email + expiration + tentative
        otp_storage[email] = {
            'otp': otp,
            'new_email': new_email,
            'expires_at': expires_at,
            'attempts': 0
        }

        send_otp_email(new_email, otp)

        return jsonify({'status': 'success', 'message': 'OTP sent to new email.'}), 200

    except mysql.connector.Error as err:
        print(f"Erreur base de données : {err}")
        return jsonify({'status': 'error', 'message': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/verify_change_email', methods=['POST'])
def verify_change_email():
    data = request.get_json()
    otp = data.get('otp')
    email = data.get('email')
    MAX_ATTEMPTS = 5
    conn = None
    cursor = None

    if not email or not otp:
        return jsonify({'status': 'error', 'message': 'Missing fields.'}), 400

    record = otp_storage.get(email)
    if not record:
        return jsonify({'status': 'error', 'message': 'No OTP found for this user.'}), 404


    if record['attempts'] >= MAX_ATTEMPTS:
        del otp_storage[email]
        return jsonify({'status': 'error', 'message': 'Too many attempts. OTP blocked.'}), 429

    if datetime.utcnow() > record['expires_at']:
        del otp_storage[email]
        return jsonify({'status': 'error', 'message': 'OTP expired.'}), 400

    if record['otp'] != otp:
        record['attempts'] += 1
        return jsonify({'status': 'error', 'message': 'Incorrect OTP.'}), 400


    try:
        new_email = record['new_email']
        print(f"Changing email from {email} to {new_email}")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = %s WHERE email = %s", (new_email, email))
        conn.commit()

        del otp_storage[email]

        return jsonify({'status': 'success', 'message': 'Email changed successfully.'}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {err}'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/change_number', methods=['POST'])
def change_number():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400
    new_phone = data.get('new_phone')
    phone = data.get('phone')
    code = data.get('code')
    new_code = data.get('new_code')
    password = data.get('password')
    if not phone or not password or not new_phone or not code or not new_code:
        return jsonify({'status': 'error', 'message': 'All champs requis'}), 400
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone_number=%s AND indicatif_telephonique=%s ", (phone, code))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

    if not user:
        return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 404
    # Récupération du mot de passe haché
    try:
        hashed_password = user[2].encode('utf-8') if isinstance(user[2], str) else user[2]
        if verify_password(password, hashed_password):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE users 
            SET phone_number = %s, indicatif_telephonique = %s 
            WHERE phone_number = %s AND indicatif_telephonique = %s;

            """, (new_phone, new_code, phone, code))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'number changed!'}), 200
        else:
            return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Processing error.: {str(e)}'}), 500


@app.route('/change_password', methods=['POST'])
def change_password():
    """
    Endpoint pour changer le mot de passe d'un utilisateur.
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    # Extraction des champs
    email = data.get('email')
    password = data.get('password')
    new_password = data.get('new_password')
    confirm_new_password = data.get('confirm_new_password')

    # Validation des champs
    if not email or not password or not new_password:
        return jsonify({'status': 'error', 'message': "All fields are required."}), 400
    # Email format validation
    email = data.get("email", "").strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    # if email and not re.match(email_regex, email):
    #     return jsonify({
    #         'status': 'error',
    #         'message': 'Invalid email format.'
    #     }), 400 
    if confirm_new_password != new_password:
       return jsonify({
            'status': 'error',
            'message': "Passwords do not match."
        }), 400 
    if not is_valid_password(new_password):
        return jsonify({
            'status': 'error',
            'message': "The password must be at least 8 characters long and include an uppercase letter, a number, and a special character."
        }), 400

    # Hachage du mot de passe avant de le stocker
    hashed_new_password = hash_password(new_password)
    # Mise à jour de la base de données MySQL
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s ", (email,email))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': "Incorrect username or password."}), 404
        try:
            hashed_password = user[2].encode('utf-8') if isinstance(user[2], str) else user[2]
            if verify_password(password, hashed_password):
                # Mise à jour du mot de passe dans la base de données
                cursor.execute("""
                    UPDATE users SET password_hash = %s WHERE email = %s OR username = %s
                """, (hashed_new_password, email, email))
                conn.commit()
                return jsonify({'message': 'Password updated successfully!'}), 200
            else:
                return jsonify({'status': 'error', 'message': "Incorrect username or password."}), 401
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Processing error: {str(e)}'}), 500
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Unexpected error. : {str(e)}'}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/delete_account', methods=['POST'])
def delete_account():
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

    # Vérification format email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        return jsonify({'status': 'error', 'message': 'Invalid email format.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'status': 'error', 'message': "User not found."}), 404

        hashed_password = user[2]  # Assurez-vous que c'est bien le champ du mot de passe
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')

        if not verify_password(password, hashed_password):
            return jsonify({'status': 'error', 'message': "Incorrect password."}), 401

        # Génération OTP
        otp = str(random.randint(1000, 9999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        otp_storage[email] = {
            "email": email,
            "otp": otp,
            "expires_at": expires_at,
            "attempts": 0
        }

        send_otp_email(email, otp)
        return jsonify({"status": "success", "message": "OTP sent to your email.", "email": email}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/verify_delete_account', methods=['POST'])
def verify_delete_account():
    data = request.get_json()
    otp = data.get('otp')
    email = data.get('email')

    if not data or not otp or not email:
        return jsonify({'status': 'error', 'message': 'OTP and email are required.'}), 400

    record = otp_storage.get(email)
    MAX_ATTEMPTS = 5

    if not record:
        return jsonify({'status': 'error', 'message': 'No OTP found for this user.'}), 404

    if record['attempts'] >= MAX_ATTEMPTS:
        del otp_storage[email]
        return jsonify({'status': 'error', 'message': 'Too many attempts. OTP blocked.'}), 429

    if datetime.utcnow() > record['expires_at']:
        del otp_storage[email]
        return jsonify({'status': 'error', 'message': 'OTP expired.'}), 400

    if record['otp'] != otp:
        record['attempts'] += 1
        return jsonify({'status': 'error', 'message': 'Incorrect OTP.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'status': 'error', 'message': "User not found."}), 404

        cursor.execute("DELETE FROM users WHERE email=%s", (email,))
        conn.commit()
        del otp_storage[email]

        return jsonify({'status': 'success', 'message': 'Account successfully deleted.'}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/add_qr', methods=['POST'])
def add_qr():
    data = request.json
    username = data.get('username')
    location = data.get('location')
    qr_code = data.get('qr_code')

    if not username or not location or not qr_code:
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertion avec is_active = TRUE
        cursor.execute("""
            UPDATE qr_codes
            SET user = %s, locations = %s, is_active = TRUE
            WHERE qr_code = %s
        """, (username, location, qr_code))

        conn.commit()
        return jsonify({'status': 'success', "message": "QR code successfully added and activated."}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/exist_qr', methods=['POST'])
def exist_qr():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': "No data received."}), 400

    qr_code = data.get('qr_code')
    if not qr_code:
        return jsonify({'status': 'error', 'message': 'QR code is required.'}), 400

    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérifie si le QR code existe
        cursor.execute("SELECT is_active FROM qr_codes WHERE qr_code = %s", (qr_code,))
        result = cursor.fetchone()

        if result:
            is_active = result[0]
            if is_active == True:
                return jsonify({'status': 'success', 'message': 'QR code is active', 'is_active': True}), 200
            else:
                return jsonify({'status': 'success', 'message': 'QR code is not active', 'is_active': False}), 200
        else:
            # Insertion du QR code si inexistant
            # cursor.execute("INSERT INTO qr_codes (qr_code) VALUES (%s)", (qr_code,))
            # conn.commit()
            # QR code non trouvé
            return jsonify({'status': 'success', 'message': 'QR code does not exist'}), 404

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()




from datetime import datetime
@app.route('/ask_repair', methods=['GET'])
def ask_repair():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, date, comment, qr_code, hour_slot, status FROM ask_repair")
        asks = cursor.fetchall()

        asks_list = [{
            'id': row[0],
            'username': row[1],
            'date': row[2].strftime("%A, %d %b %Y") if row[2] else None,
            'comment': row[3],
            'qr_code': row[4],
            'hour_slot': (
                f"{row[5].seconds // 3600:02}:{(row[5].seconds % 3600) // 60:02}:{row[5].seconds % 60:02}"
                if row[5] else None
            ),
            'status': row[6]
        } for row in asks]

        return jsonify(asks_list), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/add_question', methods=['POST'])
def add_question():
    try:
        data = request.get_json()  # Récupère les données envoyées dans le body de la requête
        question_text = data.get('text')

        if not question_text:
            return jsonify({'status': 'error', 'message': 'Question text is required'}), 400
        
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insérer la nouvelle question dans la base de données
        cursor.execute("INSERT INTO questions (text) VALUES (%s)", (question_text,))
        conn.commit()

        # Retourner une réponse de succès
        return jsonify({'status': 'success', 'message': 'Question successfully added'}), 201

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/delete_question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()

        return jsonify({"status": "success", "message": "Question successfully deleted"}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/users', methods=['GET'])
def get_users():
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registred_users")
        users = cursor.fetchall()

        # Créer une liste de dictionnaires pour retourner les users et leurs IDs
        users_list = [{'id': row[0], 'username': row[1], 'email': row[2], 'role': row[3]} for row in users]

        return jsonify(users_list), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/add_user', methods=['POST'])
def add_user():
    conn = None
    cursor = None
    try:
        data = request.get_json()  # Récupération des données envoyées en JSON
        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON data'}), 400

        user = data.get('username', '').strip()
        email = data.get('email', '').strip()
        role = data.get('role', '').strip()
        if not user or not email or not role:
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if email and not re.match(email_regex, email):
            return jsonify({'status': 'error', 'message': 'Invalid email format.'}), 400
        # Connexion à la base de données
        conn = get_db_connection()
        cursor = conn.cursor()

        # Vérification si l'utilisateur existe déjà
        cursor.execute("SELECT * FROM registred_users WHERE email = %s OR username = %s", (email, user))
        user_registred = cursor.fetchone()

        if user_registred:
            return jsonify({'status': 'error', 'message': "Username or email already exists."}), 400

        # Insertion de l'utilisateur
        cursor.execute("INSERT INTO registred_users (username, email, role) VALUES (%s, %s, %s)", (user, email, role))
        conn.commit()

        return jsonify({'status': 'success', 'message': 'User successfully added'}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registred_users WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify({"status": "success", "message": "User successfully deleted"}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/techniciens', methods=['GET'])
def get_techniciens():
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM techniciens")
        techniciens = cursor.fetchall()

        # Créer une liste de dictionnaires pour retourner les techniciens et leurs IDs
        techniciens_list = [{'id': row[0], 'name': row[1], 'ville': row[2]} for row in techniciens]

        return jsonify(techniciens_list), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/email', methods=['POST'])
def get_email():
    data = request.get_json()  # Récupère les données envoyées dans le corps de la requête POST
    
    if not data or 'username' not in data:
        return jsonify({'status': 'error', 'message': "No username provided."}), 400

    username = data['username']  # Récupère le username à partir du corps de la requête

    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()

        # Requête pour récupérer l'email de l'utilisateur
        cursor.execute("SELECT email FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            # Si un email est trouvé, renvoyer l'email
            return jsonify({'status': 'success', 'email': result[0]}), 200
        else:
            # Si l'utilisateur n'est pas trouvé, renvoyer une erreur
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500

    finally:
        # Assurez-vous de fermer la connexion à la base de données
        if conn:
            cursor.close()
            conn.close()


@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        data = request.get_json(force=True)
        logging.info(f"Received data from client: {data}")

        to_email = data.get('to_email')
        message_text = data.get('message')

        if not to_email or not message_text:
            return jsonify({"error": "Missing 'to_email' or 'message' parameter"}), 400

        sender_email = "hseinghannoum@gmail.com"
        sender_password = "ehybppmrmbueakgo"  # Attention : stocker en variables d’environnement en prod

        # Compose email message
        email_subject = "Votre demande de maintenance"
        email_body = f"Subject: {email_subject}\n\nVotre code OTP est : {message_text}"

        # Connexion SMTP et envoi de l'email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, email_body)

        logging.info(f"Email sent successfully to {to_email}")
        return jsonify({"status": "success", "message": f"Email envoyé à {to_email}"}), 200

    except smtplib.SMTPException as smtp_err:
        logging.error(f"SMTP error: {smtp_err}")
        return jsonify({"error": "Erreur lors de l’envoi de l’email"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500





# data_store = {"qr_data": ""}
# @app.route('/receive_qr', methods=['POST'])
# def receive_qr():
#     data = request.json
#     if "qr_data" in data:
#         data_store["qr_data"] = data["qr_data"]
#         return jsonify({"message": "Data received successfully"}), 200
#     return jsonify({'status':'error',"message": "Invalid data"}), 400



#   @app.route('/get_qr', methods=['GET'])
#   def get_qr():
#     try:
#         # Connexion à la base de données MySQL
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM qr_codes")
#         qr_codes = cursor.fetchall()
#         if qr_codes :
#             return jsonify ({'status': 'success', 'message': 'Qrcode exist'}), 200
#         else:
#             return jsonify({'status': 'error', 'message': 'Qrcode not exist'}), 400
#     except mysql.connector.Error as err:
#         return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
#     finally:
#         if conn:
#             cursor.close()
#             conn.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
