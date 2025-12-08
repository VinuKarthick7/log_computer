"""
College Lab Registration System
Flask Backend - Professional Edition
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import uuid
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = 'lab_registration_secure_key_2025'

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            register_no TEXT NOT NULL,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            system_no TEXT NOT NULL,
            in_time TEXT NOT NULL,
            in_date TEXT NOT NULL,
            out_time TEXT,
            out_date TEXT,
            status TEXT DEFAULT 'active'
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    """Redirect to registration page."""
    return redirect(url_for('register'))

@app.route('/register', methods=['GET'])
def register():
    """Display the registration form."""
    # Get current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')
    
    return render_template('register.html', 
                         current_date=current_date,
                         current_time=current_time)

@app.route('/api/register', methods=['POST'])
def api_register():
    """Handle registration form submission."""
    try:
        data = request.get_json()
        
        # Extract and validate data
        register_no = data.get('register_no', '').strip().upper()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        system_no = data.get('system_no', '').strip()
        in_time = data.get('in_time', '').strip()
        in_date = data.get('in_date', '').strip()
        
        # Validation
        if not re.match(r'^[A-Z0-9]{12}$', register_no):
            return jsonify({
                'success': False, 
                'error': 'Register number must be exactly 12 alphanumeric characters.'
            }), 400
        
        if not name or len(name) < 2:
            return jsonify({
                'success': False, 
                'error': 'Please enter a valid name.'
            }), 400
        
        if not department:
            return jsonify({
                'success': False, 
                'error': 'Please select a department.'
            }), 400
        
        if not system_no or len(system_no) < 1:
            return jsonify({
                'success': False, 
                'error': 'System number is required.'
            }), 400
        
        # Check if student is already logged in (active session)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM logs 
            WHERE register_no = ? AND status = 'active'
        ''', (register_no,))
        active_session = cursor.fetchone()
        
        if active_session:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'You are already logged in. Please log out first.'
            }), 400
        
        # Generate session ID and insert into database
        session_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO logs (
                session_id, register_no, name, department, 
                system_no, in_time, in_date, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active')
        ''', (session_id, register_no, name, department, 
              system_no, in_time, in_date))
        
        conn.commit()
        conn.close()
        
        # Write session info to file for tracking
        with open('current_session.txt', 'w') as f:
            f.write(f"{session_id}|{register_no}|{name}")
        
        return jsonify({
            'success': True,
            'message': 'Registration successful!',
            'session_id': session_id,
            'name': name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle logout (update out_time)."""
    try:
        data = request.get_json()
        session_id = data.get('session_id', '').strip()
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID is required.'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if session exists and is active
        cursor.execute('''
            SELECT * FROM logs 
            WHERE session_id = ? AND status = 'active'
        ''', (session_id,))
        session = cursor.fetchone()
        
        if not session:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Invalid session or already logged out.'
            }), 400
        
        # Update out_time and status
        out_time = datetime.now().strftime('%H:%M:%S')
        out_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            UPDATE logs 
            SET out_time = ?, out_date = ?, status = 'completed'
            WHERE session_id = ?
        ''', (out_time, out_date, session_id))
        
        conn.commit()
        conn.close()
        
        # Clear session file
        if os.path.exists('current_session.txt'):
            os.remove('current_session.txt')
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/admin')
def admin():
    """Display admin dashboard with all logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs ORDER BY id DESC')
    logs = cursor.fetchall()
    conn.close()
    
    # Get current date for today's sessions calculation
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('admin.html', logs=logs, current_date=current_date)

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    print("=" * 60)
    print("🖥️  College Lab Registration System")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("Registration page: http://localhost:5000/register")
    print("Admin dashboard: http://localhost:5000/admin")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
