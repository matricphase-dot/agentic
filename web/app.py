from flask import Flask, request
app = Flask(__name__)
emails = []

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head><title>Agentic Core</title>
<style>body{font-family:Arial;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:100px;text-align:center;}
h1{font-size:3em;} .btn{padding:15px 30px;background:#ff6b6b;color:white;text-decoration:none;border-radius:25px;font-size:1.2em;}</style>
</head>
<body>
<h1>🚀 Agentic Core</h1>
<p>AI Agentic Workflows</p>
<a href="/waitlist" class="btn">Join Waitlist</a>
</body>
</html>
'''

@app.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    message = ''
    count = len(emails)
    if request.method == 'POST':
        email = request.form.get('email', '')
        if '@' in email and email not in emails:
            emails.append(email)
            message = f'<div style="background:green;color:white;padding:15px;border-radius:10px;margin:20px;">Joined! #{count+1}</div>'
        else:
            message = '<div style="background:orange;color:white;padding:15px;border-radius:10px;margin:20px;">Already joined!</div>'
    return '''
<!DOCTYPE html>
<html>
<head><title>Waitlist</title>
<style>body{font-family:Arial;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;padding:50px;text-align:center;}
input{padding:15px;width:300px;font-size:16px;border-radius:5px;border:none;margin-right:10px;}
button{padding:15px 30px;font-size:16px;background:#10b981;color:white;border:none;border-radius:5px;cursor:pointer;}</style>
</head>
<body>
<h1>🚀 Agentic Core Waitlist</h1>
''' + message + f'''
<form method="POST">
<input name="email" type="email" placeholder="your@email.com" required>
<button>Join Waitlist</button>
</form>
<p><strong>{count}</strong> subscribers</p>
<a href="/" style="color:white;">← Dashboard</a>
</body>
</html>
'''
