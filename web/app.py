from flask import Flask
from web import create_app
from models import db

app = create_app()

@app.cli.command()
def init_db():
    db.create_all()
    print("✅ Database initialized with all tables")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
