from flask import Flask, render_template, request, redirect, url_for
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
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM files')
    files = cursor.fetchall()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # Store file metadata in the database
        conn = sqlite3.connect('database/files.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO files (filename) VALUES (?)', (file.filename,))
        conn.commit()
        conn.close()
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
    return redirect(url_for('index'))


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(port=5002, debug=True)
