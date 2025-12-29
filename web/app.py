from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
@app.route('/')
def home():
    return <h1>?? Agentic Core Dashboard - BACK ONLINE!</h1> + <br><a href="/waitlist">Join Waitlist</a>
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
<html><head><title>Waitlist</title></head>
<body><h1>?? Agentic Core Waitlist</h1>
<form method="POST"><input name="email" type="email" placeholder="your@email.com" required> <button>Join</button></form>
<p>{% with messages = get_flashed_messages() %}{% for message in messages %}{{ message }}{% endfor %}{% endwith %}</p>
</body></html>
'''
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
