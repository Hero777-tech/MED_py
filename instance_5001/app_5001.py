from flask import Flask, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Initialize the database
def init_db():
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            replication1 TEXT,
            replication2 TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check if the columns replication1 and replication2 exist, if not, add them
    cursor.execute("PRAGMA table_info(files)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'replication1' not in columns:
        cursor.execute("ALTER TABLE files ADD COLUMN replication1 TEXT")
    if 'replication2' not in columns:
        cursor.execute("ALTER TABLE files ADD COLUMN replication2 TEXT")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return "Replication Server 5001 is running."

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Store file metadata in the database
        conn = sqlite3.connect('database/files.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO files (filename) VALUES (?)', (file.filename,))
        conn.commit()
        conn.close()
        return "File successfully uploaded and stored", 200

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(port=5001, debug=True)
