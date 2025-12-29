from flask import Blueprint, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from app import db
waitlist_bp = Blueprint('waitlist_page', __name__)  # Changed name
class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
@waitlist_bp.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    if request.method == 'POST':
        email = request.form['email']
        if Waitlist.query.filter_by(email=email).first():
            flash('Already on waitlist!', 'warning')
        else:
            new_entry = Waitlist(email=email)
            db.session.add(new_entry)
            db.session.commit()
            flash('Joined waitlist! ??', 'success')
        return redirect(url_for('waitlist_page.waitlist'))
    return render_template('waitlist.html')
