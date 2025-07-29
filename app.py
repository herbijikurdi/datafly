import os
import uuid
import json
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
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        password = request.form.get('password')
        if uploaded_file.filename != '':
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}_{uploaded_file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)

            if password:
                passwords = load_passwords()
                passwords[filename] = password
                save_passwords(passwords)

            download_link = url_for('download_file', filename=filename, _external=True)
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
    app.run(debug=True)