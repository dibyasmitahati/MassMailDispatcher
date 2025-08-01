import os
import pandas as pd
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from email_validator import validate_email, EmailNotValidError  # ✅ NEW

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    subject = request.form.get('subject')
    body = request.form.get('body')

    if not file or file.filename == '':
        return redirect('/')
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    valid_emails = []
    invalid_emails = []

    if 'Email' in df.columns:
        for email in df['Email']:
            if pd.isna(email):
                continue
            email = str(email).strip()
            if is_valid_email(email):
                valid_emails.append(email)
            else:
                invalid_emails.append(email)
    else:
        return "CSV must have a column named 'Email'"

    for email in valid_emails:
        send_email(email, subject, body)

    return render_template('result.html', valid=valid_emails, invalid=invalid_emails)

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)