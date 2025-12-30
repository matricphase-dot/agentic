from flask import Flask, request
app = Flask(__name__)
emails = []
workflows = [{"name": "Content Pipeline", "status": "Running", "success": "98%"}, {"name": "Lead Gen", "status": "Active", "success": "94%"}]

@app.route('/')
def dashboard():
    html = '''
<!DOCTYPE html>
<html>
<head><title>Agentic Core Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-900 text-white min-h-screen">
'''
    html += '''
<nav class="bg-gray-800 p-6">
<div class="max-w-7xl mx-auto flex justify-between">
<h1 class="text-2xl font-bold flex items-center">
<i class="fas fa-brain mr-3 text-blue-400"></i>Agentic Core
<span class="ml-4 bg-green-500 px-3 py-1 rounded-full text-sm font-bold">Production Ready</span>
</h1>
<a href="/waitlist" class="bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-2 rounded-xl font-semibold hover:from-emerald-600 hover:to-teal-700">+ Join Waitlist</a>
</div>
</nav>
'''
    html += '''
<div class="max-w-7xl mx-auto p-8">
<div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
<div class="bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-8 rounded-2xl border border-blue-500/30 text-center">
<div class="text-4xl font-bold text-blue-400">''' + str(len(workflows)) + '''</div>
<div class="text-sm opacity-75 mt-2">Active Workflows</div>
</div>
<div class="bg-gradient-to-br from-green-500/20 to-teal-500/20 p-8 rounded-2xl border border-green-500/30 text-center">
<div class="text-4xl font-bold text-green-400">92.5%</div>
<div class="text-sm opacity-75 mt-2">Intelligence</div>
</div>
<div class="bg-gradient-to-br from-orange-500/20 to-red-500/20 p-8 rounded-2xl border border-orange-500/30 text-center">
<div class="text-4xl font-bold text-orange-400">$18K</div>
<div class="text-sm opacity-75 mt-2">MRR Sim</div>
</div>
<div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-8 rounded-2xl border border-purple-500/30 text-center">
<div class="text-4xl font-bold text-purple-400">12/12</div>
<div class="text-sm opacity-75 mt-2">Modules Live</div>
</div>
</div>
'''
    html += '''
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
'''
    for wf in workflows:
        html += f'''
<div class="bg-gray-800/50 p-8 rounded-2xl border border-gray-600 hover:border-blue-500/50 transition-all backdrop-blur-sm">
<div class="flex justify-between items-start mb-6">
<h3 class="font-bold text-2xl flex-1 mr-4">{wf["name"]}</h3>
<span class="px-4 py-2 bg-green-500/20 text-green-400 rounded-full text-sm font-bold">{wf["status"]}</span>
</div>
<div class="text-4xl font-black text-green-400 mb-2">{wf["success"]}</div>
<div class="text-lg opacity-75">Success Rate</div>
</div>
'''
    html += '''
</div>
<div class="text-center py-16 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-3xl border border-emerald-500/30">
<h2 class="text-4xl font-black mb-6">Production Ready → Scale Now</h2>
<a href="/waitlist" class="inline-flex items-center bg-gradient-to-r from-emerald-500 to-teal-600 px-12 py-6 rounded-2xl font-bold text-xl hover:from-emerald-600 hover:to-teal-700 shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all">
<i class="fas fa-rocket mr-3"></i>Launch Enterprise Trial
</a>
<p class="mt-6 opacity-75">Trusted by teams automating $18K+ MRR</p>
</div>
</div>
</body>
</html>
'''
    return html

@app.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    global emails
    if request.method == 'POST':
        email = request.form.get('email', '')
        if '@' in email and email not in emails:
            emails.append(email)
        return f'<script>alert("✅ {email} joined! #{len(emails)} on waitlist");window.location="/";</script>'
    return '''
<!DOCTYPE html>
<html>
<head><title>Agentic Core Waitlist</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-slate-900 to-indigo-900 text-white min-h-screen flex items-center justify-center p-8">
<div class="max-w-md w-full bg-white/10 backdrop-blur-xl rounded-3xl p-12 border border-white/20 shadow-2xl">
<h1 class="text-4xl font-bold mb-8 text-center">Agentic Core Waitlist</h1>
<form method="POST" class="space-y-6">
<input name="email" type="email" placeholder="your@company.com" required class="w-full p-6 text-xl bg-white/20 border border-white/30 rounded-2xl backdrop-blur-sm focus:border-emerald-400 focus:outline-none text-white placeholder-white/60">
<button type="submit" class="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 p-6 text-xl font-bold rounded-2xl shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all">Get Early Access</button>
</form>
<p class="text-center mt-8 opacity-75 text-sm">''' + str(len(emails)) + ''' builders already joined</p>
<a href="/" class="block text-center mt-6 opacity-75 hover:opacity-100 transition-opacity">← Dashboard</a>
</div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
