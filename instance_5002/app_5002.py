from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Initialize the database
def init_db():
    conn = sqlite3.connect('database/files.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('upload.html')

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

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    init_db()
    app.run(port=5002,debug=True)