from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from dotenv import load_dotenv
import requests
import os
import logging

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv('API_URL')

# Predefined responses
responses = {
    "hi": "Hello! How can I help you today?",
    "bye": "Goodbye! Have a nice day!",
    "how are you": "I'm just a bunch of code, but thanks for asking!"
}



def check_authentication():
    access_token = session.get('access_token')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        try:
            response = requests.get(f"{API_URL}/user_history", headers=headers)
            if response.status_code == 200:
                return True
            else:
                logger.error(f"Authentication check failed: {response.text}")
                session.pop('access_token', None)
                flash('Session expired, please login again', 'danger')
                return False
        except requests.RequestException as e:
            logger.error(f"Error during authentication check: {e}")
            flash('Error during authentication check. Please login again.', 'danger')
            session.pop('access_token', None)
            return False
    else:
        flash('You need to login first', 'danger')
        return False


@app.before_request
def before_request():
    if request.endpoint not in ('login', 'register', 'static'):
        if not check_authentication():
            return redirect(url_for('login'))



@app.route('/')
def index():
    packs = []
    if 'access_token' in session:
        token = session.get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        try:
            response = requests.get(f"{API_URL}/packman/list_packs", headers=headers)
            if response.status_code == 200:
                packs = response.json()
            else:
                logger.error(f"Failed to fetch packs: {response.text}")
                flash('Failed to fetch packs', 'danger')
        except requests.RequestException as e:
            logger.error(f"Error fetching packs: {e}")
            flash('Error fetching packs', 'danger')
    return render_template('index.html', packs=packs)




@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "").lower()
    response_message = responses.get(user_message, "Sorry, I don't understand that.")
    return jsonify({"response": response_message})



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            response = requests.post(f"{API_URL}/login", json={
                'email': email,
                'password': password
            })

            if response.status_code == 200:
                access_token = response.json().get('access_token')
                session['access_token'] = access_token
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                message = response.json().get('message', 'Login failed')
                logger.error(f"Login failed: {message}")
                flash(message, 'danger')
        except requests.RequestException as e:
            logger.error(f"Error during login: {e}")
            flash('Error during login', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    return redirect("https://sourcebox-official-website-9f3f8ae82f0b.herokuapp.com/sign_up")




if __name__ == '__main__':
    app.run(debug=True)
