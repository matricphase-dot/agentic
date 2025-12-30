from flask import Flask, request, redirect
app = Flask(__name__)
app.secret_key = 'simple-key'
emails = []
@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head><title>Agentic Core</title>
<style>body{font-family:Arial;padding:50px;text-align:center;background:#f0f8ff;}</style>
</head>
<body>
<h1>?? Agentic Core Dashboard</h1>
<p>AI Agentic Workflows</p>
<a href="/waitlist" style="display:inline-block;padding:15px 30px;background:#007bff;color:white;text-decoration:none;border-radius:8px;font-size:18px;">Join Waitlist</a>
</body>
</html>
'''
@app.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email', '')
        if '@' in email and email not in emails:
            emails.append(email)
            message = '<p style="color:green;font-size:18px;">? Thanks ' + email + '! You're on the waitlist! ??</p>'
        elif email in emails:
            message = '<p style="color:orange;font-size:18px;">?? Already on waitlist!</p>'
        else:
            message = '<p style="color:red;">? Please enter valid email</p>'
    return '''
<!DOCTYPE html>
<html>
<head><title>Waitlist</title>
<style>body{font-family:Arial;padding:50px;text-align:center;}</style>
</head>
<body>
<h1>?? Agentic Core Waitlist</h1>
<p>Be first to access AI-powered agentic workflows</p>
''' + message + '''
<form method="POST" style="margin:50px 0;">
  <input name="email" type="email" placeholder="your@email.com" style="padding:20px;width:350px;font-size:18px;border:2px solid #ddd;border-radius:5px;" required>
  <button type="submit" style="padding:20px 40px;font-size:18px;background:#28a745;color:white;border:none;border-radius:5px;cursor:pointer;margin-left:10px;">Join Waitlist</button>
</form>
<p><small>''' + str(len(emails)) + ''' subscribers</small></p>
<a href="/"> Back to Dashboard</a>
</body>
</html>
'''
if __name__ == '__main__':
    app.run(debug=True)
