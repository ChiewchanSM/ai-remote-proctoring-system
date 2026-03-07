import sqlite3
import os

# The database file will be saved right next to your photos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(LOG_DIR, "proctor_database.db")

def init_db():
    """Creates the database and table if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create the structure for our evidence table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evidence_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            student_id TEXT,
            violation_type TEXT,
            photo_filename TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_log(timestamp, student_id, violation_type, photo_filename):
    """Inserts a new violation alert into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO evidence_logs (timestamp, student_id, violation_type, photo_filename)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, student_id, violation_type, photo_filename))
    conn.commit()
    conn.close()

def get_all_logs():
    """Fetches all logs from the database, newest first."""
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Order by ID descending so the newest alerts are automatically at the top
    cursor.execute('SELECT timestamp, student_id, violation_type, photo_filename FROM evidence_logs ORDER BY id DESC')
    logs = cursor.fetchall()
    conn.close()
    return logs

def get_student_summary():
    """Groups alerts by student to show a summary on the Home Page."""
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # This SQL gets each student, counts their violations, and finds their latest alert
    cursor.execute('''
        SELECT student_id, COUNT(*) as total_violations, MAX(timestamp) as latest_alert
        FROM evidence_logs 
        GROUP BY student_id 
        ORDER BY latest_alert DESC
    ''')
    summary = cursor.fetchall()
    conn.close()
    return summary

def get_logs_by_student(student_id):
    """Fetches the detailed evidence photos for just one specific student."""
    if not os.path.exists(DB_PATH):
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, student_id, violation_type, photo_filename 
        FROM evidence_logs 
        WHERE student_id = ? 
        ORDER BY id DESC
    ''', (student_id,))
    logs = cursor.fetchall()
    conn.close()
    return logs