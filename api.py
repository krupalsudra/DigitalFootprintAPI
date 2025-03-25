from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import os
import time

app = Flask(__name__)
CORS(app)

# Fetch API keys from environment variables (corrected)
LEAKCHECK_API_KEY = os.getenv("1aa966cec1397b3b48af57b9113cd1a43844e75f")
GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("AIzaSyDMb0G6Oc-msfdigMLBI76PE_oAb-Mbk0M")

def block_fake_entity(entity_type, value):
    """Simulates blocking a fake entity (email, phone, website)."""
    time.sleep(3)  # Simulate blocking delay
    return f"🚨 {entity_type} {value} has been BLOCKED!"

@app.route('/check_email', methods=['POST'])
def check_email():
    """Checks if an email is fake using LeakCheck API."""
    data = request.json
    email = data.get('email', '').strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email is required!"}), 400

    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({"status": "alert", "message": "❌ Invalid Email Format!"}), 400

    if not LEAKCHECK_API_KEY:
        return jsonify({"status": "error", "message": "API Key Missing!"}), 500

    # Call LeakCheck API
    try:
        response = requests.get(f"https://leakcheck.io/api/public?key={LEAKCHECK_API_KEY}&check={email}", timeout=5)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status") == "found":
            block_message = block_fake_entity("Email", email)
            return jsonify({"status": "alert", "message": "⚠️ This Email is FAKE!", "action": block_message})

        return jsonify({"status": "safe", "message": "✅ Email is SAFE!"})

    except requests.RequestException:
        return jsonify({"status": "error", "message": "Failed to check email. Try again later."}), 500

@app.route('/check_website', methods=['POST'])
def check_website():
    """Checks if a website is suspicious."""
    data = request.json
    url = data.get('url', '')

    if not url:
        return jsonify({"status": "error", "message": "URL is required!"}), 400

    # Validate URL format
    url_pattern = r'^(https?:\/\/)?(www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    if not re.match(url_pattern, url):
        return jsonify({"status": "alert", "message": "❌ Invalid URL format!"}), 400

    # Block websites with "http://" (non-secure)
    if url.startswith("http://"):
        block_message = block_fake_entity("Website", url)
        return jsonify({"status": "alert", "message": "🚨 Fake Website Detected!", "action": block_message})

    return jsonify({"status": "safe", "message": "✅ Website is SAFE!"})

@app.route('/check_phone', methods=['POST'])
def check_phone():
    """Checks if a phone number is suspicious."""
    data = request.json
    phone = data.get('phone', '')

    if not phone:
        return jsonify({"status": "error", "message": "Phone number is required!"}), 400

    # Ensure phone is a 10-digit number
    if not phone.isdigit() or len(phone) != 10:
        block_message = block_fake_entity("Phone", phone)
        return jsonify({"status": "alert", "message": "❌ Fake Call Detected!", "action": block_message}), 400

    return jsonify({"status": "safe", "message": "✅ Phone Number is SAFE!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
