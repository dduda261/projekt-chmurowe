from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])
matches = []

@app.route("/match", methods=["POST"])
def create_match():
    data = request.json
    pet_name = data.get("pet_name")
    username = data.get("username")
    if not pet_name or not username:
        return jsonify({"error": "Missing data"}), 400
    matches.append({"pet_name": pet_name, "username": username})
    return jsonify({"message": "Match submitted"}), 201

@app.route("/matches", methods=["GET"])
def list_matches():
    return jsonify(matches), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
