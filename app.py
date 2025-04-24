from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)
CORS(app)

# 🔌 Koneksi ke MongoDB Railway
# client = MongoClient("mongodb://mongo:efjIOPvBPZPKeHRQeFGcgGUQnjauiuWF@gondola.proxy.rlwy.net:47608")
client = MongoClient("mongodb://mongo:efjIOPvBPZPKeHRQeFGcgGUQnjauiuWF@mongodb.railway.internal:27017")

db = client["MongoRail"]  # Ganti jika nama databasenya berbeda
users_collection = db["users"]

# 🔧 Helper untuk ubah ObjectId ke string
def serialize_user(user):
    # Mengubah data MongoDB agar sesuai dengan format template HTML
    return [
        str(user["_id"]),  # user[0] adalah id
        user["name"],      # user[1] adalah name
        user["email"]      # user[2] adalah email
    ]

# 🌐 Web Routes
@app.route("/")
def index():
    users = list(users_collection.find())
    # Menyesuaikan format data sebelum dikirim ke template HTML
    serialized_users = [serialize_user(user) for user in users]
    return render_template("index.html", users=serialized_users)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    email = request.form["email"]
    users_collection.insert_one({"name": name, "email": email})
    return redirect("/")

@app.route("/delete/<string:id>")
def delete(id):
    try:
        users_collection.delete_one({"_id": ObjectId(id)})
    except (InvalidId, TypeError):
        users_collection.delete_one({"_id": id})  # Untuk UUID string
    return redirect("/")

# 📱 API Routes (Tetap bisa diakses, jika diperlukan)
@app.route("/api/users", methods=["GET"])
def api_get_users():
    users = list(users_collection.find())
    return jsonify([serialize_user(user) for user in users]), 200

@app.route("/api/users", methods=["POST"])
def api_add_user():
    data = request.get_json()
    # Gunakan ID yang dikirimkan dari Android (jika ada)
    user_id = data.get("id", None)  # Jika tidak ada ID, MongoDB akan generate
    user = {
        "_id": user_id or None,  # Jika user_id ada, gunakan itu
        "name": data["name"],
        "email": data["email"]
    }
    result = users_collection.insert_one(user)
    return jsonify({"message": "User added", "id": str(result.inserted_id)}), 201

from bson.errors import InvalidId

@app.route("/api/users/<string:id>", methods=["PUT"])
def api_update_user(id):
    data = request.get_json()
    try:
        # Coba convert ke ObjectId, kalau gagal berarti UUID biasa
        users_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"name": data["name"], "email": data["email"]}}
        )
    except (InvalidId, TypeError):
        users_collection.update_one(
            {"_id": id},  # UUID string
            {"$set": {"name": data["name"], "email": data["email"]}}
        )
    return jsonify({"message": "User updated"}), 200

@app.route("/api/users/<string:id>", methods=["DELETE"])
def api_delete_user(id):
    try:
        users_collection.delete_one({"_id": ObjectId(id)})
    except (InvalidId, TypeError):
        users_collection.delete_one({"_id": id})
    return jsonify({"message": "User deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
