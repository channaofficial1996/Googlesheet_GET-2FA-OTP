from flask import Flask, request, jsonify
from otp_fetcher import fetch_otp_from_email

app = Flask(__name__)

@app.route("/get-otp", methods=["POST"])
def get_otp():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"result": "❌ Email/password not provided"}), 400
        result = fetch_otp_from_email(email, password)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"result": f"❌ Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
