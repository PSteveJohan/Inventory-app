import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"  # Required for session management

# Initialize Firebase using Render's Environment Variable
if not firebase_admin._apps:
    firebase_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if firebase_json:
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback for local testing if you have a local json file
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple check (You can replace this with your Firestore user verification logic)
    if username == "admin" and password == "password":
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password. <='/'><a href='/'>Go back</a>", 401

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)