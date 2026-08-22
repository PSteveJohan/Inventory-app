import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Firebase setup via Render Environment Variable
firebase_creds_json = os.environ.get('FIREBASE_CREDENTIALS_JSON')

if firebase_creds_json:
    cred_dict = json.loads(firebase_creds_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Connected to Firebase Firestore successfully!")
else:
    print("WARNING: FIREBASE_CREDENTIALS_JSON environment variable not found.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    search_query = request.args.get('search', '').lower()
    try:
        docs = db.collection('medicines').stream()
        medicines = []
        for doc in docs:
            item = doc.to_dict()
            item['id'] = doc.id
            if search_query:
                name = str(item.get('name', '')).lower()
                batch = str(item.get('batch', '')).lower()
                if search_query in name or search_query in batch:
                    medicines.append(item)
            else:
                medicines.append(item)
        return jsonify(medicines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medicine/<id>', methods=['GET'])
def get_medicine(id):
    try:
        doc_ref = db.collection('medicines').document(id)
        doc = doc_ref.get()
        if doc.exists:
            item = doc.to_dict()
            item['id'] = doc.id
            return jsonify(item)
        return jsonify({"error": "Not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add', methods=['POST'])
def add_medicine():
    try:
        data = request.json
        new_doc_ref = db.collection('medicines').document()
        new_doc_ref.set({
            'name': data.get('name'),
            'form': data.get('form'),
            'strength': data.get('strength'),
            'batch': data.get('batch'),
            'quantity': int(data.get('quantity', 0)),
            'expiry': data.get('expiry'),
            'cost': float(data.get('cost', 0)),
            'price': float(data.get('price', 0))
        })
        return jsonify({"success": True, "id": new_doc_ref.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update', methods=['POST'])
def update_medicine():
    try:
        data = request.json
        doc_id = str(data.get('id'))
        doc_ref = db.collection('medicines').document(doc_id)
        doc_ref.update({
            'name': data.get('name'),
            'form': data.get('form'),
            'strength': data.get('strength'),
            'batch': data.get('batch'),
            'quantity': int(data.get('quantity', 0)),
            'expiry': data.get('expiry'),
            'cost': float(data.get('cost', 0)),
            'price': float(data.get('price', 0))
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_medicine():
    try:
        data = request.json
        doc_id = str(data.get('id'))
        db.collection('medicines').document(doc_id).delete()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)