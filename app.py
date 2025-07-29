import os
import uuid
import json
import zipfile
from flask import Flask, request, send_from_directory, redirect, render_template, url_for, flash

UPLOAD_FOLDER = 'uploads'
PASSWORD_FILE = 'passwords.json'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'geheimes_ding'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_passwords():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_passwords(passwords):
    with open(PASSWORD_FILE, 'w') as f:
        json.dump(passwords, f)

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        password = request.form.get('password')
        
        if not uploaded_files or uploaded_files[0].filename == '':
            flash("Keine Dateien ausgewählt.")
            return redirect(request.url)

        unique_id = str(uuid.uuid4())
        zip_filename = f"{unique_id}.zip"
        zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in uploaded_files:
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                zipf.write(file_path, arcname=filename)
                os.remove(file_path)  # temporäre Datei löschen

        # Passwort speichern
        if password:
            passwords = load_passwords()
            passwords[zip_filename] = password
            save_passwords(passwords)

        download_link = url_for('download_file', filename=zip_filename, _external=True)
        return render_template("index.html", download_link=download_link)

    return render_template("index.html", download_link=None)

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    passwords = load_passwords()
    if filename in passwords:
        if request.method == 'POST':
            entered_password = request.form.get('password')
            if entered_password == passwords[filename]:
                return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
            else:
                flash("Falsches Passwort.")
        return render_template('download.html', password_required=True, filename=filename)
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
