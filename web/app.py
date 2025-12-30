from flask import Flask, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.secret_key = 'super-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
@app.route('/')
def home():
    return '<h1>?? Agentic Core Dashboard</h1><p><a href="/waitlist">Join Waitlist</a></p>'
@app.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    messages = []
    if request.method == 'POST':
        email = request.form.get('email')
        if email:
            if Waitlist.query.filter_by(email=email).first():
                messages.append('Already on waitlist!')
            else:
                wl = Waitlist(email=email)
                db.session.add(wl)
                db.session.commit()
                messages.append('Joined waitlist! ??')
    html = '''
<!DOCTYPE html>
<html><head><title>Waitlist</title></head>
<body style="font-family:Arial;padding:50px;text-align:center;">
<h1>?? Agentic Core Waitlist</h1>
<form method="POST">
  <input name="email" type="email" placeholder="your@email.com" style="padding:15px;width:300px;" required>
  <button style="padding:15px 30px;background:blue;color:white;">Join</button>
</form>
'''
    for msg in messages:
        html += f'<p style="color:green;">{msg}</p>'
    html += '</body></html>'
    return html
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
