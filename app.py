from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
from replication.replicate import replicate_to_servers


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.secret_key = 'your_secret_key'

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
        replicate_to_servers(filepath)
        
        # Assuming replicate_to_servers replicates to two servers in order, we can manually set the status
        replication1_status = "Success" if os.path.exists('http://127.0.0.1:5001/upload') else "Failed"
        replication2_status = "Success" if os.path.exists('http://127.0.0.1:5002/upload') else "Failed"
        
        # Store file metadata in the database
        conn = sqlite3.connect('database/files.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (filename, replication1, replication2) 
            VALUES (?, ?, ?)
        ''', (file.filename, replication1_status, replication2_status))
        conn.commit()
        conn.close()
        
        flash('File successfully uploaded and replicated')
        return redirect(url_for('index'))

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    cursor.execute('SELECT filename FROM files WHERE id = ?', (file_id,))
    file = cursor.fetchone()
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file[0])
        if os.path.exists(filepath):
            os.remove(filepath)
        cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
    
    conn.close()
    flash('File successfully deleted')
    return redirect(url_for('index'))

@app.route('/view/<int:file_id>')
def view_file(file_id):
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file = cursor.fetchone()
    conn.close()
    
    if file:
        return render_template('view.html', file=file)
    else:
        flash('File not found')
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
