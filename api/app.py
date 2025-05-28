from kivy.uix.filechooser import error
import jwt
import datetime
from flask import Flask, request, jsonify
import mysql.connector
import random
import smtplib
import bcrypt
import re  # Pour valider le format des emails
from flask_cors import CORS  # Importation de CORS

# Initialisation de l'application Flask
app = Flask(__name__)
# Appliquer CORS à toute l'application
CORS(app)
# Clé secrète pour l'encodage et le décodage du JWT
SECRET_KEY = "SEZAIA2022"

# Configuration de la connexion à la base de données MySQL
db_config = {
    'user': 'root',        # Nom d'utilisateur MySQL
    'password': 'root',    # Mot de passe MySQL
    'host': '127.168.100.229',   # Hôte MySQL
    'database': 'projet_sezaia'  # Nom de la base de données
}

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
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    required_fields = ["username", "email", "password", "confirm_password", "number", "address", "country_code", "city", "postal_code"]
    errors = []

    # Checking for required fields
    for field in required_fields:
        if not data.get(field):
            errors.append({'field': field, 'message': f"The field '{field.replace('_', ' ').capitalize()}' is required."})

    # Email format validation
    email = data.get("email", "").strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if email and not re.match(email_regex, email):
        errors.append({'field': 'email', 'message': 'Invalid email format.'})

    # Password validation
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    if not is_valid_password(password):
        errors.append({'field': 'password', 'message': "Password must be at least 8 characters long, include an uppercase letter, a number, and a special character."})
    elif password != confirm_password:
        errors.append({'field': 'confirm_password', 'message': "Passwords do not match."})

    # if errors:
    #     return jsonify({'status': 'error', 'message': 'Validation errors.', 'errors': errors}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the username or email exists in the 'users' table
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (data["username"], data["email"]))
        existing_user = cursor.fetchone()

        if existing_user:
            # return jsonify({'status': 'error', 'message': "Username or email already exists."}), 400
            errors.append({'field': ['username', 'email'], 'message': "Username or email already exists."})
        
        # Check if the user is in 'registred_users'
        cursor.execute("SELECT * FROM registred_users WHERE username = %s OR email = %s", (data["username"], data["email"]))
        user_registred = cursor.fetchone()
        role = user_registred[3]

        if not user_registred:
            # return jsonify({'status': 'error', 'message': "Username or email can't be used."}), 400
            errors.append({'field': ['username', 'email'], 'message': "Username or email can't be used."})
        
        if errors:
            return jsonify({'status': 'error', 'message': 'Validation errors.', 'errors': errors}), 400
        # Generate OTP
        otp = str(random.randint(1000, 9999))

        # Create JWT payload
        payload = {
            "username": data['username'],
            "email": data['email'],
            "password": hash_password(password).decode("utf-8") if isinstance(hash_password(password), bytes) else hash_password(password),
            "number": data['number'],
            "address": data['address'],
            "postal_code": data['postal_code'],
            "city": data['city'],
            "country_code": data['country_code'],
            "role": role,
            "otp_code": otp,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        }


        # Generate JWT token
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Send OTP by email
        send_otp_email(data['email'], otp)

        return jsonify({"message": "OTP sent to your email.", "token": token}), 200

    except Exception as e:
        return jsonify({'status': 'error', "message": f"Server error: {str(e)}"}), 500

    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/verify_register', methods=['POST'])
def verify_register():
    data = request.json
    otp = data['otp']
    token = data['token']
    
    try:
        # Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # OTP verification
        if payload['otp_code'] == otp:
            # Connect to the database and insert user information
            conn = get_db_connection()
            cursor = conn.cursor()

            # SQL query to insert user information
            cursor.execute(""" 
                INSERT INTO users (username, email, password_hash, phone_number, address, role, ville, code_postal, indicatif_telephonique)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (payload['username'], payload['email'], payload['password'], payload['number'], payload['address'], payload['role'], payload['city'], payload['postal_code'], payload['country_code']))

            # Commit changes to the database
            conn.commit()

            return jsonify({'status': 'success', "message": "User successfully verified."}), 200
        else:
            return jsonify({'status': 'error', "message": "Incorrect OTP"}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', "message": "The token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'error', "message": "Invalid token."}), 401
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', "message": f"MySQL error: {err}"}), 500
    except Exception as e:
        return jsonify({'status': 'error', "message": str(e)}), 500


@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    data = request.json
    token = data.get('token')
    new_email = data.get('email')

    if not token:
        return jsonify({'status': 'error', "message": "Token missing."}), 400

    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Check if the token has expired
        exp_datetime = datetime.datetime.utcfromtimestamp(payload['exp']) if isinstance(payload['exp'], int) else payload['exp']
        if datetime.datetime.utcnow() > exp_datetime:
            return jsonify({'status': 'error', "message": "The token has expired."}), 401

        # Generate a new OTP
        new_otp = str(random.randint(1000, 9999))

        # Update the payload with the new OTP
        payload['otp_code'] = new_otp
        payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

        # Generate new token
        new_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Send the new OTP by email
        send_otp_email(new_email, new_otp)

        return jsonify({'status': 'success', "message": "New OTP sent.", "token": new_token}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', "message": "The token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'error', "message": "Invalid token."}), 401
    except Exception as e:
        return jsonify({'status': 'error', "message": f"Error while regenerating the OTP: {str(e)}"}), 500


data_store = {"qr_data": ""}
@app.route('/receive_qr', methods=['POST'])
def receive_qr():
    data = request.json
    if "qr_data" in data:
        data_store["qr_data"] = data["qr_data"]
        return jsonify({"message": "Data received successfully"}), 200
    return jsonify({'status':'error',"message": "Invalid data"}), 400


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
        data = request.get_json()  # Récupérer les données envoyées par le client
        question_id = data.get('question_id')
        response_text = data.get('response')
        username = data.get('username')
        qr_code = data.get('qr_code')
        # Vérification si les données sont présentes
        if not question_id or not response_text or not username or not qr_code:
            return jsonify({'status': 'error', 'message': "Missing data."}), 400
        
        # Insertion de la réponse dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO responses (question_id, response, username, qr_code) VALUES (%s, %s, %s,%s)", (question_id, response_text, username, qr_code))
        conn.commit()  # Confirmer l'insertion

        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': "Response saved."}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{err}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur : {str(e)}'}), 500
    

@app.route('/send_ask', methods=['POST'])
def send_ask():
    try:
        data = request.get_json()  # Récupérer les données envoyées par le client
        username = data.get('username')
        tech_name = data.get('tech_name')
        date = data.get("date")
        comment = data.get('comment')
        qr_code = data.get('qr_code')
        # Vérification si les données sont présentes
        if not username or not qr_code or not tech_name or not date or not comment:
            return jsonify({'status': 'error', 'message': "Missing data."}), 400
        
        # Insertion de la réponse dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ask_repair (username, technician_name, date, comments, qr_code) VALUES (%s,%s, %s, %s,%s)", (username, tech_name, date, comment, qr_code))
        conn.commit()  # Confirmer l'insertion

        cursor.close()
        conn.close()

        return jsonify({'status': 'success', 'message': "Response saved."}), 200

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{err}'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Erreur : {str(e)}'}), 500
  

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'status': 'error', 'message': "Email or username required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE (email = %s OR username = %s) ", (email, email))
        user = cursor.fetchone()

        if user:
            email = user[3]
            otp = str(random.randint(1000, 9999))
            
            payload = {
                "email": email,
                "otp_code": otp,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
            }

            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            try:
                send_otp_email(email, otp)
                return jsonify({'status': 'success', "message": "OTP sent to your email.", "token": token, "email": email})
            except Exception as e:
                return jsonify({'status': 'error', "message": str(e)}), 500
        else:
            return jsonify({'status': 'error', 'message': "User not found."}), 404

    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/verify_forget', methods=['POST'])
def verify_forget():
    data = request.json
    otp = data['otp']
    token = data['token']
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        
        if payload['otp_code'] == otp:
            return jsonify({"message": "User successfully verified.", "token": token}), 200
        else:
            return jsonify({'status': 'error', "message": "Incorrect OTP"}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', "message": "The token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'error', "message": "Invalid token."}), 401
    except Exception as e:
        return jsonify({'status': 'error', "message": str(e)}), 500


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
            print("Le mot de passe est correct!")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET username = %s WHERE username = %s
            """, (new_username, username))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Username changed!'}), 200
        else:
            return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Processing error.: {str(e)}'}), 500


@app.route('/change_email', methods=['POST'])
def change_email():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400
    
    new_email = data.get('new_email')
    email = data.get('email')
    password = data.get('password')

    if not email or not password or not new_email:
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email) or not re.match(email_regex, new_email):
            return jsonify({'status': 'error', 'message': 'The email format is invalid.'}), 400
        if email == new_email:
            return jsonify({'status': 'error', 'message': "Username or email already exists."}), 401
        cursor.execute("SELECT * FROM registred_users WHERE email = %s", (email,))
        user_registred = cursor.fetchone()
        if not user_registred:
            return jsonify({'status': 'error', 'message': "Username or email can't be used."}), 400
        if not user: 
            return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 401
        
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

    # Vérification du mot de passe
    try:
        hashed_password = user[2].encode('utf-8') if isinstance(user[2], str) else user[2]
        if verify_password(password, hashed_password):
            otp = str(random.randint(1000, 9999))
            payload = {
                "email": email,
                "new_email": new_email,
                "otp_code": otp,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)  # Expiration après 5 minutes
            }
            # Création du JWT
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            try:
                # Envoi du code OTP au nouvel email
                send_otp_email(new_email, otp)
                return jsonify({"message": "OTP sent to your email.", "token": token}), 200
            except Exception as e:
                return jsonify({'status': 'error', "message": f"Error while sending the OTP: {str(e)}"}), 500
        else:
            return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Processing error: {str(e)}'}), 500
    

@app.route('/verify_change_email', methods=['POST'])
def verify_change_email():
    data = request.json
    otp = data['otp']
    token = data['token']
    new_email = data['email']
    
    try:
        # Décodage du JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        
        # Vérification de l'OTP
        if payload['otp_code'] == otp:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET email = %s WHERE email = %s
            """, (new_email, payload["email"]))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'email changed!'}), 200
            
        else:
            return jsonify({'status':'error',"message": "OTP incorrect"}), 400
    except jwt.ExpiredSignatureError:
        return jsonify({'status':'error',"message": "The token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status':'error',"message": "Invalid token."}), 401
    except Exception as e:
        return jsonify({'status':'error',"message": str(e)}), 500


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
    if email and not re.match(email_regex, email):
        return jsonify({
            'status': 'error',
            'message': 'Invalid email format.'
        }), 400 
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
    hashed_password = hash_password(new_password)
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
                """, (hashed_password, email, email))
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


@app.route('/verify_delete_account', methods=['POST'])
def verify_delete_account():
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error: {str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

    if not user:
        return jsonify({'status': 'error', 'message': "User not found or incorrect password."}), 404

    try:
        hashed_password = user[2].encode('utf-8') if isinstance(user[2], str) else user[2]
        if verify_password(password, hashed_password):
            # Génération d'un code OTP
            otp = str(random.randint(1000, 9999))
            payload = {
                "email": email,
                "otp_code": otp,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)  # Expiration après 5 minutes
            }
            # Création du JWT
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            try:
                # Envoi du code OTP à l'email de l'utilisateur
                send_otp_email(email, otp)
                return jsonify({"message": "OTP sent to your email.", "token": token}), 200
            except Exception as e:
                return jsonify({'status': 'error', 'message': f"Error while sending the OTP: {str(e)}"}), 500
        else:
            return jsonify({'status': 'error', 'message': "Incorrect password."}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Processing error: {str(e)}'}), 500


@app.route('/delete_account', methods=['POST'])
def delete_account():
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No data received.'}), 400

    otp = data.get('otp')
    token = data.get('token')

    try:
        # Décodage du JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")

        # Vérification de l'OTP
        if payload['otp_code'] == otp:
            email = payload['email']

            # Connexion à la base de données MySQL
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()

            if not user:
                return jsonify({'status': 'error', 'message': "User not found."}), 404

            # Suppression du compte de l'utilisateur
            cursor.execute("DELETE FROM users WHERE email=%s", (email,))
            conn.commit()

            return jsonify({'status': 'success', 'message': 'Account successfully deleted.'}), 200
        else:
            return jsonify({'status': 'error', 'message': "OTP incorrect."}), 400

    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', 'message': "The token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({'status': 'error', 'message': "Invalid token."}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"Error: {str(e)}"}), 500


@app.route('/add_qr', methods=['POST'])
def add_qr():
    data = request.json
    username = data['username']
    location = data['location']
    qr_code = data['qr_code']
    if not username or not location or not qr_code:
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO qr_codes (user,locations,qr_code) VALUES (%s, %s,%s)",(username, location, qr_code))
        conn.commit()
        return jsonify({'status': 'success', "message": "Qr_code successfuly added."}), 200
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.route('/exist_qr', methods=['POST'])
def exist_qr():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': "No data received."}), 400
    
    qr_code = data.get('qr_code')
    if not qr_code:
        return jsonify({'status': 'error', 'message': 'Qr code is required.'}), 400

    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qr_codes where qr_code = %s", (qr_code,))
        qr_codes = cursor.fetchall()
        if qr_codes :
            return jsonify ({'status': 'success', 'message': 'Qrcode exist'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Qrcode not exist'}), 400
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
            cursor.close()
            conn.close()


# @app.route('/get_qr', methods=['GET'])
# def get_qr():
    try:
        # Connexion à la base de données MySQL
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qr_codes")
        qr_codes = cursor.fetchall()
        if qr_codes :
            return jsonify ({'status': 'success', 'message': 'Qrcode exist'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Qrcode not exist'}), 400
    except mysql.connector.Error as err:
        return jsonify({'status': 'error', 'message': f'Database error:{str(err)}'}), 500
    finally:
        if conn:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
