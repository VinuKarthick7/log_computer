"""
College Lab Registration Web App
Flask Backend - Single file application
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
import uuid
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'lab_registration_secret_key_2025'

DATABASE = 'logs.db'

def get_db_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the logs table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            session_id TEXT PRIMARY KEY,
            register_no TEXT NOT NULL,
            name TEXT NOT NULL,
            purpose TEXT NOT NULL,
            in_time TEXT NOT NULL,
            out_time TEXT,
            computer_no TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle registration form display and submission."""
    if request.method == 'GET':
        computer_no = request.args.get('computer_no', 'Auto-Detected')
        in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return render_template('index.html', computer_no=computer_no, in_time=in_time)
    
    elif request.method == 'POST':
        # Get form data
        register_no = request.form.get('register_no', '').strip()
        name = request.form.get('name', '').strip()
        purpose = request.form.get('purpose', '').strip()
        computer_no = request.form.get('computer_no', '').strip()
        in_time = request.form.get('in_time', '').strip()
        
        # Validation
        import re
        if not re.match(r'^\d{8}$', register_no):
            return jsonify({'error': 'Register number must be exactly 8 digits.'}), 400
        
        if not name:
            return jsonify({'error': 'Name is required.'}), 400
        
        if not purpose:
            return jsonify({'error': 'Purpose is required.'}), 400
        
        # Generate session ID and insert into database
        session_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (session_id, register_no, name, purpose, in_time, out_time, computer_no)
            VALUES (?, ?, ?, ?, ?, NULL, ?)
        ''', (session_id, register_no, name, purpose, in_time, computer_no))
        conn.commit()
        conn.close()
        
        # Write session_id to file for tracking
        with open('current_session.txt', 'w') as f:
            f.write(session_id)
        
        session['complete'] = True
        
        return jsonify({'success': True, 'message': 'Logged!', 'session_id': session_id})

@app.route('/update-out', methods=['POST'])
def update_out():
    """Update the out_time for a session."""
    data = request.get_json()
    
    if not data or 'session_id' not in data:
        return jsonify({'error': 'session_id is required.'}), 400
    
    session_id = data['session_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if session exists and out_time is NULL
    cursor.execute('SELECT * FROM logs WHERE session_id = ? AND out_time IS NULL', (session_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'error': 'Session not found or already logged out.'}), 400
    
    # Update out_time
    out_time = datetime.now().isoformat()
    cursor.execute('UPDATE logs SET out_time = ? WHERE session_id = ?', (out_time, session_id))
    conn.commit()
    conn.close()
    
    # Delete current_session.txt if exists
    if os.path.exists('current_session.txt'):
        os.remove('current_session.txt')
    
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    print("=" * 50)
    print("College Lab Registration System")
    print("=" * 50)
    print("Server running at: http://localhost:5000")
    print("Access with computer_no: http://localhost:5000?computer_no=Lab1")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
