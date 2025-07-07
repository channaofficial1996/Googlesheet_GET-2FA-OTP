import os
from otp_fetcher import fetch_otp_from_email
from flask import Flask, request, jsonify
from waitress import serve

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "✅ API is running"

@app.route("/get-otp", methods=["POST"])
def get_otp():
    try:
        data = request.get_json()
        email = data["email"]
        password = data["password"]
        result = fetch_otp_from_email(email, password)
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    serve(app, host="0.0.0.0", port=port)
