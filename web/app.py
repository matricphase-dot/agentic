from flask import Flask, request, render_template_string
app = Flask(__name__)
emails = []
workflows = [{"name": "Content Pipeline", "status": "Running", "success": "98%"}, {"name": "Lead Gen", "status": "Active", "success": "94%"}]

@app.route('/')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
<title>Agentic Core - Production Dashboard</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-900 text-white min-h-screen">
<nav class="bg-gray-800 p-6">
<div class="max-w-7xl mx-auto flex justify-between">
<h1 class="text-2xl font-bold flex items-center">
<i class="fas fa-brain mr-3 text-blue-400"></i>Agentic Core
</h1>
<a href="/waitlist" class="bg-gradient-to-r from-emerald-500 to-teal-600 px-6 py-2 rounded-xl font-semibold">+ Join Waitlist</a>
</div>
</nav>

<div class="max-w-7xl mx-auto p-6">
<!-- METRICS -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
<div class="bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-8 rounded-2xl border border-blue-500/30">
<div class="text-3xl font-bold text-blue-400">{{ len(workflows) }}</div>
<div class="text-sm opacity-75">Active Workflows</div>
</div>
<div class="bg-gradient-to-br from-green-500/20 to-teal-500/20 p-8 rounded-2xl border border-green-500/30">
<div class="text-3xl font-bold text-green-400">92.5%</div>
<div class="text-sm opacity-75">Intelligence</div>
</div>
<div class="bg-gradient-to-br from-orange-500/20 to-red-500/20 p-8 rounded-2xl border border-orange-500/30">
<div class="text-3xl font-bold text-orange-400">$18K</div>
<div class="text-sm opacity-75">MRR Sim</div>
</div>
<div class="bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-8 rounded-2xl border border-purple-500/30">
<div class="text-3xl font-bold text-purple-400">12/12</div>
<div class="text-sm opacity-75">Modules</div>
</div>
</div>

<!-- WORKFLOWS -->
<div class="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 mb-12">
<h2 class="text-3xl font-bold mb-8 flex items-center">
<i class="fas fa-cogs mr-3 text-yellow-400"></i>Active Workflows
</h2>
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
{% for workflow in workflows %}
<div class="bg-gray-700/50 p-6 rounded-xl border border-gray-600 hover:border-blue-500/50 transition-all">
<div class="flex justify-between items-start mb-4">
<h3 class="font-bold text-xl flex-1 mr-4">{{ workflow.name }}</h3>
<span class="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold">{{ workflow.status }}</span>
</div>
<div class="text-2xl font-bold text-green-400 mb-2">{{ workflow.success }}</div>
<div class="text-sm opacity-75">Success Rate</div>
</div>
{% endfor %}
</div>
</div>

<!-- AGENTS STATUS -->
<div class="grid md:grid-cols-3 gap-6">
<div class="bg-gradient-to-br from-indigo-500/20 p-8 rounded-2xl border border-indigo-500/30">
<h3 class="text-xl font-bold mb-4 flex items-center"><i class="fas fa-robot mr-2"></i>6 Agents</h3>
<div class="space-y-2 text-sm">
<span class="block">✅ Planner</span>
<span class="block">✅ Researcher</span>
<span class="block">✅ Coder</span>
<span class="block">✅ QA</span>
<span class="block">✅ Executor</span>
<span class="block">✅ Teacher</span>
</div>
</div>
<div class="bg-gradient-to-br from-emerald-500/20 p-8 rounded-2xl border border-emerald-500/30">
<h3 class="text-xl font-bold mb-4 flex items-center"><i class="fas fa-chart-line mr-2"></i>Optimization</h3>
<div class="text-2xl font-bold text-emerald-400 mb-4">125% Gain</div>
<p class="text-sm opacity-75">Cumulative improvement</p>
</div>
<div class="bg-gradient-to-br from-purple-500/20 p-8 rounded-2xl border border-purple-500/30">
<h3 class="text-xl font-bold mb-4 flex items-center"><i class="fas fa-trophy mr-2"></i>Market Share</h3>
<div class="text-2xl font-bold text-purple-400 mb-4">18.9%</div>
<p class="text-sm opacity-75">+4.2% MoM growth</p>
</div>
</div>
</div>

<!-- WAITLIST CTA -->
<div class="mt-20 p-12 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-3xl border border-emerald-500/30 text-center">
<h2 class="text-4xl font-bold mb-6">Production Ready → Scale Now</h2>
<a href="/waitlist" class="inline-flex items-center bg-gradient-to-r from-emerald-500 to-teal-600 px-12 py-6 rounded-2xl font-bold text-xl hover:from-emerald-600 hover:to-teal-700 shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all">
<i class="fas fa-rocket mr-3"></i>Launch Enterprise
</a>
</div>
</body>
</html>
    ''', workflows=workflows)

@app.route('/waitlist', methods=['GET', 'POST'])
def waitlist():
    global emails
    if request.method == 'POST':
        email = request.form['email']
        if email not in emails:
            emails.append(email)
        return f'<script>alert("✅ {email} joined! #{len(emails)}"); window.location="/";</script>'
    return '''
<!DOCTYPE html>
<html>
<head><title>Waitlist - Agentic Core</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gradient-to-br from-slate-900 to-indigo-900 text-white min-h-screen flex items-center justify-center p-6">
<div class="max-w-md w-full bg-white/5 backdrop-blur-xl rounded-3xl p-12 border border-white/20 shadow-2xl">
<h1 class="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">Agentic Core Waitlist</h1>
<form method="POST" class="space-y-6">
<input name="email
