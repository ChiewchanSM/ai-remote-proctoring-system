from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import database

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "data")

# --- 1. THE CLASSROOM HOME PAGE ---
@app.route('/')
def dashboard():
    students = database.get_student_summary()
    return render_template('index.html', students=students)

# --- 2. THE STUDENT DETAIL PAGE ---
@app.route('/student/<student_id>')
def student_detail(student_id):
    logs = database.get_logs_by_student(student_id)
    return render_template('student_detail.html', logs=logs, student_id=student_id)

# --- 3. THE EVIDENCE FOLDER ---
@app.route('/evidence/<filename>')
def serve_image(filename):
    return send_from_directory(LOG_DIR, filename)

# --- 4. THE API MAILBOX ---
@app.route('/api/upload', methods=['POST'])
def receive_evidence():
    student_id = request.form.get('student_id')
    violation_type = request.form.get('violation_type')
    timestamp = request.form.get('timestamp')
    photo = request.files.get('photo')

    if photo:
        photo_path = os.path.join(LOG_DIR, photo.filename)
        photo.save(photo_path)
        database.add_log(timestamp, student_id, violation_type, photo.filename)
        return jsonify({'message': 'Evidence logged!'}), 200
        
    return jsonify({'error': 'No photo attached'}), 400

if __name__ == '__main__':
    print("\n🌐 STARTING TEACHER DASHBOARD...")
    print("👉 Open: http://127.0.0.1:5000\n")
    
    database.init_db() 
    
    app.run(host='0.0.0.0', port=5000, debug=True)