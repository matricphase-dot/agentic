from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
@app.route('/')
def home():
    return '<h1>?? Agentic Core Dashboard - BACK ONLINE!</h1><br><a href="/waitlist">Join Waitlist</a>'
@app.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    if request.method == 'POST':
        email = request.form['email']
        if Waitlist.query.filter_by(email=email).first():
            flash('Already on waitlist!', 'warning')
        else:
            wl = Waitlist(email=email)
            db.session.add(wl)
            db.session.commit()
            flash('Joined waitlist! ??', 'success')
        return redirect('/waitlist')
    return '''
<!DOCTYPE html>
<html>
<head><title>Agentic Core Waitlist</title></head>
<body style="font-family:Arial;padding:50px;">
<h1>?? Agentic Core Waitlist</h1>
<p>Be first to access AI-powered workflows</p>
<form method="POST">
  <input name="email" type="email" placeholder="your@email.com" style="padding:15px;width:300px;font-size:16px;" required>
  <button type="submit" style="padding:15px 30px;font-size:16px;background:#007bff;color:white;border:none;cursor:pointer;">Join Waitlist</button>
</form>
<br>
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <p style="color:{{ 'green' if category == 'success' else 'orange' }};">{{ message }}</p>
    {% endfor %}
  {% endif %}
{% endwith %}
</body>
</html>
'''
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
