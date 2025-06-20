import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_cors import CORS
from auth_middleware import requires_auth
import uuid

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])
app.config["UPLOAD_FOLDER"] = "uploads"

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5001")

DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "localhost")  
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "petdopt")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

db = SQLAlchemy(app)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    species = db.Column(db.String(30))
    gender = db.Column(db.String(20))
    age = db.Column(db.String(20))
    location = db.Column(db.String(120))
    description = db.Column(db.Text)
    username = db.Column(db.String(80), nullable=False)
    image_filename = db.Column(db.String(120))

@app.route("/pets", methods=["GET"])
def list_pets():
    pets = Pet.query.all()
    return jsonify([
        {   
            "id": pet.id,
            "name": pet.name,
            "species": pet.species,
            "gender": pet.gender,
            "age": pet.age,
            "location": pet.location,
            "description": pet.description,
            "username": pet.username,
            "image_url": f"{BASE_URL}/uploads/{pet.image_filename}"
        } for pet in pets
    ])
import uuid

@app.route("/pets", methods=["POST"])
@requires_auth(allowed_roles=["user", "admin"])
def add_pet():
    if "image" not in request.files:
        return jsonify({"error": "Brak pliku ze zdjęciem"}), 400
    
    image = request.files["image"]
    filename = secure_filename(image.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    image.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))

    pet = Pet(
        name=request.form["name"],
        species=request.form["species"],
        gender=request.form["gender"],
        age=request.form["age"],
        location=request.form["location"],
        description=request.form["description"],
        username=request.form['username'],
        image_filename=unique_filename
    )
    db.session.add(pet)
    db.session.commit()
    return jsonify({"status": "ok"}), 201


@app.route('/pets/<int:pet_id>', methods=['DELETE'])
@requires_auth(allowed_roles=["user", "admin"])
def delete_pet(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet:
        return jsonify({"error": "Nie znaleziono zwierzaka"}), 404
    
    requesting_user = request.user.get("preferred_username")

    if not requesting_user:
        return jsonify({"error": "Brak informacji o użytkowniku"}), 400
    
    user_roles = request.user.get("realm_access", {}).get("roles", [])
    is_admin = "admin" in user_roles

    if pet.username != requesting_user and not is_admin:
        return jsonify({"error": "Brak uprawnień do usunięcia tego ogłoszenia"}), 403

    db.session.delete(pet)
    db.session.commit()
    return jsonify({"message": "Usunięto ogłoszenie"})

@app.route("/uploads/<filename>")
def get_image(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)


