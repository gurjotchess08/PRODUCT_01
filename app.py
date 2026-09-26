import os
from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)


def get_db():
    # Vercel injects DATABASE_URL automatically once you add Postgres storage
    return psycopg2.connect(os.environ["DATABASE_URL"])


# GET: read all records
@app.route('/api/records', methods=['GET'])
def get_records():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM records ORDER BY id DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)


# POST: insert a new record
@app.route('/api/records', methods=['POST'])
def add_record():
    data = request.get_json()
    name = (data or {}).get('name', '').strip()
    email = (data or {}).get('email', '').strip()
    age = (data or {}).get('age')

    if not name or not email or not age:
        return jsonify({"error": "name, email and age are all required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (name, email, age) VALUES (%s, %s, %s) RETURNING id",
        (name, email, age)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": new_id, "name": name, "email": email, "age": age}), 201


# DELETE: remove a record by id
@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id = %s", (record_id,))
    conn.commit()
    cur.close()
    conn.close()
    return '', 204
