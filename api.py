from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os
import time

app = Flask(__name__)
CORS(app)

# API Keys (Replace with valid ones)
LEAKCHECK_API_KEY = os.getenv("1aa966cec1397b3b48af57b9113cd1a43844e75f", "your_leakcheck_api_key")
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("AIzaSyDMb0G6Oc-msfdigMLBI76PE_oAb-Mbk0M", "your_google_api_key")

# ✅ Function to Simulate Blocking (Wait 3 Seconds & Block)
def block_fake_entity(entity_type, value):
    time.sleep(3)  # Wait for 3 seconds before blocking
    return f"🚨 {entity_type} {value} has been BLOCKED!"

# ✅ Check Fake Emails
@app.route('/check_email', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email is required!"}), 400

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"status": "alert", "message": "❌ Invalid Email Format!"}), 400

    response = requests.get(f"https://leakcheck.io/api/public?key={LEAKCHECK_API_KEY}&check={email}", timeout=5)
    
    if response.status_code == 200 and response.json().get("status") == "found":
        block_message = block_fake_entity("Email", email)  # Simulate blocking
        return jsonify({"status": "alert", "message": "⚠️ This Email is FAKE!", "action": block_message})

    return jsonify({"status": "safe", "message": "✅ Email is SAFE!"})

# ✅ Check Fake Websites
@app.route('/check_website', methods=['POST'])
def check_website():
    data = request.json
    url = data.get('url', '')

    if not url:
        return jsonify({"status": "error", "message": "URL is required!"}), 400

    if url.startswith("http://"):
        block_message = block_fake_entity("Website", url)
        return jsonify({"status": "alert", "message": "🚨 Fake Website Detected!", "action": block_message})

    return jsonify({"status": "safe", "message": "✅ Website is SAFE!"})

# ✅ Check Fake Calls
@app.route('/check_phone', methods=['POST'])
def check_phone():
    data = request.json
    phone = data.get('phone', '')

    if not phone:
        return jsonify({"status": "error", "message": "Phone number is required!"}), 400

    if not phone.isdigit() or len(phone) != 10:
        block_message = block_fake_entity("Phone", phone)
        return jsonify({"status": "alert", "message": "❌ Fake Call Detected!", "action": block_message}), 400

    return jsonify({"status": "safe", "message": "✅ Phone Number is SAFE!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)  # Running on Port 8000
