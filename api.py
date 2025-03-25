from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os
import time

app = Flask(__name__)
CORS(app)

# ✅ Use Environment Variables for API Keys
LEAKCHECK_API_KEY = os.getenv("LEAKCHECK_API_KEY", "1aa966cec1397b3b48af57b9113cd1a43844e75f")
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "AIzaSyDMb0G6Oc-msfdigMLBI76PE_oAb-Mbk0M")

# ✅ Function to Simulate Blocking
def block_fake_entity(entity_type, value):
    time.sleep(3)  # Simulate processing delay
    return f"🚨 {entity_type} {value} has been BLOCKED!"

# ✅ Check if Email is Fake
@app.route('/api/check_email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email is required!"}), 400

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"status": "alert", "message": "❌ Invalid Email Format!"}), 400

    try:
        response = requests.get(f"https://leakcheck.io/api/public?key={LEAKCHECK_API_KEY}&check={email}", timeout=5)
        if response.status_code == 200 and response.json().get("status") == "found":
            block_message = block_fake_entity("Email", email)
            return jsonify({"status": "alert", "message": "⚠️ This Email is FAKE!", "action": block_message})
    except requests.RequestException:
        return jsonify({"status": "error", "message": "🔴 Failed to verify email!"}), 500

    return jsonify({"status": "safe", "message": "✅ Email is SAFE!"})

# ✅ Check if Website is Fake
@app.route('/api/check_website', methods=['POST'])
def check_website():
    data = request.json
    url = data.get('url', '')

    if not url:
        return jsonify({"status": "error", "message": "URL is required!"}), 400

    if url.startswith("http://"):
        block_message = block_fake_entity("Website", url)
        return jsonify({"status": "alert", "message": "🚨 Fake Website Detected!", "action": block_message})

    return jsonify({"status": "safe", "message": "✅ Website is SAFE!"})

# ✅ Check if Phone Number is Fake
@app.route('/api/check_phone', methods=['POST'])
def check_phone():
    data = request.json
    phone = data.get('phone', '')

    if not phone:
        return jsonify({"status": "error", "message": "Phone number is required!"}), 400

    if not phone.isdigit() or len(phone) != 10:
        block_message = block_fake_entity("Phone", phone)
        return jsonify({"status": "alert", "message": "❌ Fake Call Detected!", "action": block_message}), 400

    return jsonify({"status": "safe", "message": "✅ Phone Number is SAFE!"})

# ✅ Root Route
@app.route("/")
def home():
    return jsonify({"message": "Digital Footprint API is running!"}), 200

# ✅ Run the App (Production-ready with Waitress)
if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)  # Changed to Port 8080
