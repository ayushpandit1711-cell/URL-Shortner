import os
import random
import string
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, redirect
from flask_mysqldb import MySQL 

app = Flask(__name__)

app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'
app.config['MYSQL_PASSWORD'] = 'Ayush@841239'
app.config['MYSQL_DB']       = 'url_shortener'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def get_unique_short_code():
    while True:
        code = generate_short_code()
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM urls WHERE short_code = %s", (code,))
        if cur.fetchone() is None:
            cur.close()
            return code
        cur.close()


def format_url(row):
    return {
        "id":        str(row['id']),
        "url":       row['url'],
        "shortCode": row['short_code'],
        "createdAt": row['created_at'].isoformat() + 'Z',
        "updatedAt": row['updated_at'].isoformat() + 'Z',
    }

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<short_code>')
def redirect_short_url(short_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM urls WHERE short_code = %s", (short_code,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        return jsonify({"error": "Short URL not found"}), 404
    cur.execute("UPDATE urls SET access_count = access_count + 1 WHERE id = %s", (row['id'],))
    mysql.connection.commit()
    cur.close()
    return redirect(row['url'])

@app.route('/shorten', methods=['POST'])
def create_short_url():
    data = request.get_json()
    if not data or 'url' not in data or not data['url'].strip():
        return jsonify({"error": "A valid 'url' field is required"}), 400
    url = data['url'].strip()
    if not url.startswith(('http://', 'https://')):
        return jsonify({"error": "URL must start with http:// or https://"}), 400
    short_code = get_unique_short_code()
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO urls (url, short_code, created_at, updated_at) VALUES (%s, %s, %s, %s)",
        (url, short_code, now, now)
    )
    mysql.connection.commit()
    new_id = cur.lastrowid
    cur.execute("SELECT * FROM urls WHERE id = %s", (new_id,))
    row = cur.fetchone()
    cur.close()
    return jsonify(format_url(row)), 201

@app.route('/shorten/<short_code>', methods=['GET'])
def get_short_url(short_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM urls WHERE short_code = %s", (short_code,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return jsonify({"error": "Short URL not found"}), 404
    return jsonify(format_url(row)), 200


@app.route('/shorten/<short_code>', methods=['PUT'])
def update_short_url(short_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM urls WHERE short_code = %s", (short_code,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        return jsonify({"error": "Short URL not found"}), 404
    data = request.get_json()
    if not data or 'url' not in data or not data['url'].strip():
        cur.close()
        return jsonify({"error": "A valid 'url' field is required"}), 400
    new_url = data['url'].strip()
    if not new_url.startswith(('http://', 'https://')):
        cur.close()
        return jsonify({"error": "URL must start with http:// or https://"}), 400
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        "UPDATE urls SET url = %s, updated_at = %s WHERE short_code = %s",
        (new_url, now, short_code)
    )
    mysql.connection.commit()
    cur.execute("SELECT * FROM urls WHERE short_code = %s", (short_code,))
    updated = cur.fetchone()
    cur.close()
    return jsonify(format_url(updated)), 200

@app.route('/shorten/<short_code>', methods=['DELETE'])
def delete_short_url(short_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM urls WHERE short_code = %s", (short_code,))
    row = cur.fetchone()
    if row is None:
        cur.close()
        return jsonify({"error": "Short URL not found"}), 404
    cur.execute("DELETE FROM urls WHERE short_code = %s", (short_code,))
    mysql.connection.commit()
    cur.close()
    return '', 204


@app.route('/shorten/<short_code>/stats', methods=['GET'])
def get_stats(short_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM urls WHERE short_code = %s", (short_code,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        return jsonify({"error": "Short URL not found"}), 404
    result = format_url(row)
    result['accessCount'] = row['access_count']
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')