from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

@app.route('/beta/admin')
def beta_admin():
    try:
        conn = sqlite3.connect('beta_users.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM beta_users')
        total = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM beta_users WHERE status="approved"')
        approved = c.fetchone()[0]
        conn.close()
    except:
        total = 0
        approved = 0
    
    return f'''
    <html>
    <body>
        <h1>Beta Admin (Working)</h1>
        <p>Total: {total}</p>
        <p>Approved: {approved}</p>
        <a href="/">Back</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, port=5000)