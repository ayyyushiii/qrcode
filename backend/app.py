from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import fetch_latest_email, generate_reply, send_email

app = Flask(__name__)

CORS(app, origins=["http://localhost:3000"])

@app.route("/fetch-latest", methods=["GET"])
def fetch_latest():
    email = fetch_latest_email()
    return jsonify(email)

@app.route("/generate-reply", methods=["POST"])
def generate_reply_route():
    data = request.get_json()
    reply = generate_reply(data['subject'], data['body'])
    return jsonify({"reply": reply})

@app.route("/send-email", methods=["POST"])
def send_email_route():
    data = request.get_json()
    success = send_email(data['to'], data['subject'], data['content'])
    return jsonify({"success": success})
