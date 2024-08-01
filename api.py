import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('data.db')

@app.route('/get_code/<int:code>', methods=['GET'])
def get_code(code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT threshold FROM codes WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({'code': code, 'threshold': result[0]})
    else:
        return jsonify({'error': 'Code not found'}), 404

@app.route('/add_code', methods=['POST'])
def add_code():
    data = request.json
    code = data['code']
    threshold = data['threshold']
    umb = data['umb']
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO codes (code, threshold) VALUES (?, ?)', (code, threshold))
    cursor.execute('INSERT OR IGNORE INTO UMB (umb) VALUES (?)', (umb,))
    cursor.execute('INSERT OR REPLACE INTO umb_codes (umb, code) VALUES (?, ?)', (umb, code))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Code added successfully'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
