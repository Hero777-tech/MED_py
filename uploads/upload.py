from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

# Initialize the database
def init_db():
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            replication1 TEXT,
            replication2 TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files')
    files = cursor.fetchall()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Replicate file to other servers
        replication_statuses = replicate_to_servers(filepath)
        
        # Generate a single timestamp if Replication 1 is successful
        if replication_statuses[0] == "Success":
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp = "Failed"
        
        # Assign the same timestamp to Replication 2 if Replication 1 is successful
        replication1_status = timestamp if timestamp != "Failed" else "Failed"
        replication2_status = timestamp if replication_statuses[1] == "Success" else "Failed"
        
        # Store file metadata in the database
        conn = sqlite3.connect('database/files.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filename, replication1, replication2, timestamp) 
            VALUES (?, ?, ?, ?)
        ''', (file.filename, replication1_status, replication2_status, timestamp))
        conn.commit()
        conn.close()
        
        flash('File successfully uploaded and replicated')
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
