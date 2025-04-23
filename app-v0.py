from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Fungsi untuk koneksi ke database Railway
def get_db_connection():
    return mysql.connector.connect(
        host="shuttle.proxy.rlwy.net",
        port=14810,  # Sesuaikan dengan Railway
        user="root",
        password="uwJUEiosnJUeLOCkkhBgOgfZAqalBUGx",
        database="railway"
    )

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", users=users)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    email = request.form["email"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect("/")

# ✅ API ENDPOINT JSON untuk Android
@app.route("/api/users", methods=["GET"])
def api_get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

@app.route("/api/users", methods=["POST"])
def api_add_user():
    data = request.get_json()
    id = data["id"]
    name = data["name"]
    email = data["email"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (id, name, email) VALUES (%s, %s, %s)", (id, name, email))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User added"}), 201

@app.route("/api/users/<int:id>", methods=["PUT"])
def api_update_user(id):
    data = request.get_json()
    name = data["name"]
    email = data["email"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User updated"}), 200

@app.route("/api/users/<int:id>", methods=["DELETE"])
def api_delete_user(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "User deleted"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
