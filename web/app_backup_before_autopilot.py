import os
import json
import sqlite3
import random
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, date, timezone

from flask import Flask, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import gspread


# ---------------- Paths ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
DB_URI = "sqlite:///" + DB_PATH.replace("\\", "/")


# ---------------- Flask app ----------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_ME_FOR_REAL_USE")

app.config["SQLALCHEMY_DATABASE_URI"] = DB_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

scheduler = BackgroundScheduler(daemon=True)


# ---------------- Google Sheets config ----------------
DEFAULT_SPREADSHEET_ID = "1CmNDVr2t4JWwmnZkRymxMw-ybgZ7gNiICIiR3yuMX1I"
SERVICE_ACCOUNT_FILE = os.environ.get("GSHEETS_SERVICE_ACCOUNT_FILE", os.path.join(BASE_DIR, "service_account.json"))
GSHEETS_SPREADSHEET_ID = (os.environ.get("GSHEETS_SPREADSHEET_ID") or DEFAULT_SPREADSHEET_ID).strip()
GSHEETS_WORKSHEET = (os.environ.get("GSHEETS_WORKSHEET") or "Sheet1").strip()

_gs_client = None


# ---------------- Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Automation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)  # "leads_sheet" (demo) or others
    config_json = db.Column(db.Text, nullable=True)

    run_daily_at = db.Column(db.String(5), nullable=True)  # HH:MM UTC
    enabled = db.Column(db.Boolean, default=True, nullable=False)

    last_run_at = db.Column(db.DateTime, nullable=True)
    last_status = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="automations")


class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    automation_id = db.Column(db.Integer, db.ForeignKey("automation.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    raw_response_json = db.Column(db.Text, nullable=True)

    automation = db.relationship("Automation", backref="runs")


# ---------------- Dev schema reset (optional helper) ----------------
def sqlite_table_columns(db_file: str, table: str):
    if not os.path.exists(db_file):
        return []
    con = sqlite3.connect(db_file)
    try:
        cur = con.cursor()
        cur.execute(f"PRAGMA table_info({table});")
        rows = cur.fetchall()
        return [r[1] for r in rows]
    finally:
        con.close()


def dev_reset_db_if_schema_old():
    if not os.path.exists(DB_PATH):
        return
    auto_cols = sqlite_table_columns(DB_PATH, "automation")
    required = {"run_daily_at", "last_run_at", "last_status", "enabled"}
    if auto_cols and not required.issubset(set(auto_cols)):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass


# ---------------- Helpers ----------------
def now_utc():
    return datetime.now(timezone.utc)


def utc_hhmm_now():
    n = now_utc()
    return f"{n.hour:02d}:{n.minute:02d}"


def has_run_today(dt: datetime | None):
    if not dt:
        return False
    return dt.date() == date.today()


def validate_hhmm(s: str | None):
    if not s:
        return None
    s = s.strip()
    if len(s) != 5 or s[2] != ":":
        return None
    hh, mm = s.split(":")
    if not (hh.isdigit() and mm.isdigit()):
        return None
    h = int(hh)
    m = int(mm)
    if h < 0 or h > 23 or m < 0 or m > 59:
        return None
    return f"{h:02d}:{m:02d}"


def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)


def format_dt(dt):
    if not dt:
        return "-"
    # show as UTC string
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if dt.tzinfo else dt.strftime("%Y-%m-%d %H:%M:%S")


# ---------------- SMTP (runtime config; no caching) ----------------
def get_smtp_config():
    host = (os.environ.get("SMTP_HOST") or "").strip()
    port_raw = (os.environ.get("SMTP_PORT") or "587").strip()
    user = (os.environ.get("SMTP_USER") or "").strip()
    password = (os.environ.get("SMTP_PASS") or "").strip()
    alert_to = (os.environ.get("ALERT_TO_EMAIL") or "").strip()
    debug = ((os.environ.get("SMTP_DEBUG") or "1").strip() == "1")

    try:
        port = int(port_raw)
    except Exception:
        port = 587

    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "alert_to": alert_to,
        "debug": debug,
    }


def smtp_config_ok():
    c = get_smtp_config()
    return bool(c["host"] and c["port"] and c["user"] and c["password"] and c["alert_to"])


def send_email(subject: str, body_text: str, to_email: str):
    c = get_smtp_config()
    if not (c["host"] and c["user"] and c["password"] and to_email):
        raise RuntimeError("SMTP not configured (SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASS/ALERT_TO_EMAIL).")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = c["user"]
    msg["To"] = to_email
    msg.set_content(body_text)

    context = ssl.create_default_context()
    with smtplib.SMTP(c["host"], c["port"], timeout=30) as server:
        if c["debug"]:
            server.set_debuglevel(1)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(c["user"], c["password"])
        server.send_message(msg)


def send_lead_alert_email(lead: dict):
    c = get_smtp_config()
    subject = f"New lead: {lead.get('name') or 'Unknown'}"
    body = (
        f"New lead submitted\n\n"
        f"Time (UTC): {lead.get('timestamp_utc')}\n"
        f"Name: {lead.get('name')}\n"
        f"Email: {lead.get('email')}\n"
        f"Phone: {lead.get('phone')}\n"
        f"Message: {lead.get('message')}\n"
        f"Source: {lead.get('source')}\n"
    )
    send_email(subject, body, c["alert_to"])


# ---------------- Google Sheets ----------------
def get_gspread_client():
    global _gs_client
    if _gs_client is not None:
        return _gs_client
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise RuntimeError(f"Missing service account JSON: {SERVICE_ACCOUNT_FILE}")
    _gs_client = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    return _gs_client


def service_account_email():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        return None
    with open(SERVICE_ACCOUNT_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("client_email")


def get_ws():
    if not GSHEETS_SPREADSHEET_ID:
        raise RuntimeError("GSHEETS_SPREADSHEET_ID is empty")
    gc = get_gspread_client()
    sh = gc.open_by_key(GSHEETS_SPREADSHEET_ID)
    return sh.worksheet(GSHEETS_WORKSHEET)


def ensure_leads_header(ws):
    existing = ws.get_all_values()
    if existing:
        return
    ws.append_row(
        ["timestamp_utc", "name", "email", "phone", "message", "source"],
        value_input_option="RAW",
    )


def append_lead_to_sheet(name, email, phone, message, source):
    ws = get_ws()
    ensure_leads_header(ws)

    ts = now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")
    row = [ts, name or "", email or "", phone or "", message or "", source]
    ws.append_row(row, value_input_option="RAW")
    return ts


# ---------------- Execution engine (demo) ----------------
def execute_automation(user: User, automation: Automation):
    if automation.type == "leads_sheet":
        ts = append_lead_to_sheet(
            name="Demo Lead",
            email=user.email,
            phone="",
            message=f"Triggered by {automation.name}",
            source="automation_run",
        )
        return "success", f"Appended a demo lead ({ts}) to '{GSHEETS_WORKSHEET}'."

    succeeded = random.random() > 0.1
    status = "success" if succeeded else "fail"
    message = "Executed successfully." if succeeded else "Simulated error while running."
    return status, message


def run_and_log(automation: Automation, source: str):
    user = db.session.get(User, automation.user_id)
    t = now_utc()

    try:
        status, message = execute_automation(user, automation)
    except Exception as e:
        status = "fail"
        message = f"Integration error: {type(e).__name__}: {str(e)}"

    automation.last_run_at = t
    automation.last_status = status

    r = Run(
        automation_id=automation.id,
        status=status,
        message=f"[{source}] {message}",
        created_at=t,
    )
    db.session.add(r)
    db.session.commit()


def scheduler_tick():
    with app.app_context():
        hhmm = utc_hhmm_now()
        autos = Automation.query.filter(
            Automation.enabled.is_(True),
            Automation.run_daily_at == hhmm
        ).all()

        for a in autos:
            if has_run_today(a.last_run_at):
                continue
            run_and_log(a, source="scheduler")


def start_scheduler_once():
    if scheduler.running:
        return
    scheduler.add_job(
        func=scheduler_tick,
        trigger=IntervalTrigger(seconds=60),
        id="scheduler_tick",
        replace_existing=True,
    )
    scheduler.start()


# ---------------- Auth pages ----------------
def auth_page_html(title, subtitle, action_path, submit_text, show_name, show_password, switch_text, switch_href, error=""):
    err_html = f"<div class='err'>{error}</div>" if error else ""
    name_html = "<input name='name' placeholder='Your name (optional)'>" if show_name else ""
    pass_html = "<input name='password' type='password' placeholder='Password' required>" if show_password else ""

    return f"""
    <!doctype html><html><head>
      <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
      <title>{title}</title>
      <style>
        body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fb;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}}
        .card {{background:#fff;padding:24px 20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.08);min-width:320px;}}
        h2 {{margin:0 0 8px 0;color:#667eea;font-size:20px;}}
        p {{font-size:13px;color:#555;margin:0 0 14px 0;}}
        input {{width:100%;padding:8px 10px;margin-bottom:10px;border-radius:6px;border:1px solid #ddd;font-size:13px;}}
        button {{width:100%;padding:9px 10px;border:none;border-radius:6px;background:#667eea;color:#fff;font-weight:600;font-size:14px;cursor:pointer;}}
        .switch {{margin-top:10px;font-size:12px;text-align:center;}}
        .switch a {{color:#667eea;text-decoration:none;}}
        .err {{background:#ffecec;color:#b32020;border:1px solid #ffcccc;padding:8px 10px;border-radius:8px;font-size:12px;margin-bottom:10px;}}
      </style>
    </head><body>
      <form class="card" method="post" action="{action_path}">
        <h2>{title}</h2><p>{subtitle}</p>{err_html}
        {name_html}
        <input name="email" type="email" placeholder="you@example.com" required>
        {pass_html}
        <button type="submit">{submit_text}</button>
        <div class="switch">{switch_text} <a href="{switch_href}">{switch_href}</a></div>
      </form>
    </body></html>
    """


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        name = (request.form.get("name") or "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return auth_page_html(
                "Sign up", "Create your workspace.", "/signup",
                "Create account →", True, True, "Already have an account? Go to", "/login",
                "Email and password are required."
            )

        existing = User.query.filter_by(email=email).first()
        if existing:
            return auth_page_html(
                "Sign up", "Create your workspace.", "/signup",
                "Create account →", True, True, "Already have an account? Go to", "/login",
                "Account already exists. Please log in instead."
            )

        u = User(email=email, name=name or (email.split("@")[0]), password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
        session["user_id"] = u.id
        return redirect(url_for("home"))

    return auth_page_html("Sign up", "Create your workspace.", "/signup",
                          "Create account →", True, True, "Already have an account? Go to", "/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        u = User.query.filter_by(email=email).first()
        if not u or not u.password_hash or not check_password_hash(u.password_hash, password):
            return auth_page_html(
                "Log in", "Welcome back.", "/login",
                "Log in →", False, True, "No account yet? Go to", "/signup",
                "Invalid email or password."
            )

        session["user_id"] = u.id
        return redirect(url_for("home"))

    return auth_page_html("Log in", "Welcome back.", "/login",
                          "Log in →", False, True, "No account yet? Go to", "/signup")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


# ---------------- Lead capture ----------------
@app.route("/lead", methods=["GET", "POST"])
def lead_capture():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        message = (request.form.get("message") or "").strip()

        sheet_ts = append_lead_to_sheet(name, email, phone, message, source="public_form")

        mail_ok = False
        mail_error = None

        if smtp_config_ok():
            try:
                send_lead_alert_email({
                    "timestamp_utc": sheet_ts,
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "message": message,
                    "source": "public_form",
                })
                mail_ok = True
            except Exception as e:
                mail_ok = False
                mail_error = f"{type(e).__name__}: {str(e)}"

        return f"""
        <h2>Thanks! Lead submitted.</h2>
        <p>Sheet timestamp (UTC): {sheet_ts}</p>
        <p>Email configured: {'YES' if smtp_config_ok() else 'NO'}</p>
        <p>Email sent: {'YES' if mail_ok else 'NO'}</p>
        <p>Email error: {mail_error or '-'}</p>
        <p><a href="/lead">Submit another</a></p>
        <p><a href="/">Back to dashboard</a></p>
        """

    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Lead Capture</title>
  <style>
    body {font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fb;margin:0;}
    .wrap {max-width:540px;margin:0 auto;padding:18px 12px;}
    .card {background:#fff;border-radius:12px;padding:16px 14px;box-shadow:0 2px 10px rgba(0,0,0,0.06);}
    h1 {margin:0 0 8px 0;color:#667eea;font-size:22px;}
    p {margin:0 0 12px 0;color:#555;font-size:13px;}
    label {display:block;font-size:12px;color:#444;margin-top:10px;margin-bottom:6px;}
    input, textarea {width:100%;padding:9px 10px;border-radius:8px;border:1px solid #ddd;font-size:13px;}
    textarea {min-height:90px;resize:vertical;}
    button {margin-top:12px;width:100%;padding:10px;border:none;border-radius:10px;background:#667eea;color:#fff;font-weight:700;cursor:pointer;}
    .small {margin-top:10px;font-size:12px;color:#777;}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Lead Capture</h1>
      <p>Submits to Google Sheet and sends an email alert (if SMTP vars are set).</p>

      <form method="post" action="/lead">
        <label>Name</label>
        <input name="name" placeholder="Full name" required>

        <label>Email</label>
        <input name="email" type="email" placeholder="name@example.com" required>

        <label>Phone</label>
        <input name="phone" type="tel" placeholder="Phone (optional)">

        <label>Message</label>
        <textarea name="message" placeholder="What does the lead need?"></textarea>

        <button type="submit">Submit lead</button>
      </form>

      <div class="small"><a href="/">Back to dashboard</a></div>
    </div>
  </div>
</body>
</html>
    """


# ---------------- Dashboard ----------------
@app.route("/", methods=["GET"])
def home():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    smtp_status = "ON" if smtp_config_ok() else "OFF"
    sa_email = service_account_email() or "-"

    autos = Automation.query.filter_by(user_id=u.id).order_by(Automation.created_at.desc()).all()

    autos_rows = ""
    for a in autos:
        autos_rows += f"""
          <tr>
            <td>{a.name}</td>
            <td>{a.type}</td>
            <td>{'YES' if a.enabled else 'NO'}</td>
            <td>{a.run_daily_at or '-'}</td>
            <td>{format_dt(a.last_run_at)}</td>
            <td>{a.last_status or '-'}</td>
            <td>
              <a href="/run/{a.id}">Run now</a>
              &nbsp;|&nbsp;
              <a href="/toggle/{a.id}">{'Disable' if a.enabled else 'Enable'}</a>
            </td>
          </tr>
        """

    if not autos_rows:
        autos_rows = "<tr><td colspan='7' style='color:#666;font-size:13px;'>No automations yet. Create one below.</td></tr>"

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Dashboard</title>
  <style>
    body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fb;margin:0;}}
    .container {{max-width:1100px;margin:0 auto;padding:14px 10px 30px;}}
    .top {{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#555;}}
    .top a {{color:#667eea;text-decoration:none;}}
    .card {{background:#fff;border-radius:12px;padding:14px 12px;margin-top:12px;box-shadow:0 2px 10px rgba(0,0,0,0.06);}}
    h1 {{margin:6px 0;color:#667eea;font-size:22px;}}
    table {{width:100%;border-collapse:collapse;margin-top:10px;}}
    th, td {{text-align:left;border-bottom:1px solid #eee;padding:10px 8px;font-size:13px;}}
    th {{font-size:12px;color:#666;}}
    input, select {{padding:8px 10px;border-radius:8px;border:1px solid #ddd;font-size:13px;}}
    button {{padding:9px 12px;border:none;border-radius:10px;background:#667eea;color:#fff;font-weight:700;cursor:pointer;}}
    .row {{display:flex;gap:10px;flex-wrap:wrap;align-items:center;}}
    .muted {{font-size:12px;color:#666;}}
  </style>
</head>
<body>
  <div class="container">
    <div class="top">
      <div>Signed in as {u.email}</div>
      <div style="display:flex;gap:12px;align-items:center;">
        <a href="/lead">Lead form</a>
        <a href="/health">Health</a>
        <a href="/logout">Log out</a>
      </div>
    </div>

    <div class="card">
      <h1>Autonomous Workflow Engine</h1>
      <div class="muted">
        Sheets service acct: <b>{sa_email}</b><br>
        Spreadsheet ID: <b>{GSHEETS_SPREADSHEET_ID}</b> • Worksheet: <b>{GSHEETS_WORKSHEET}</b><br>
        SMTP: <b>{smtp_status}</b>
      </div>
    </div>

    <div class="card">
      <h3 style="margin:0 0 10px 0;">Create automation</h3>
      <form method="post" action="/create">
        <div class="row">
          <input name="name" placeholder="Automation name" required>
          <select name="type">
            <option value="leads_sheet">leads_sheet (demo)</option>
            <option value="generic">generic (simulated)</option>
          </select>
          <input name="run_daily_at" placeholder="HH:MM UTC (optional)">
          <button type="submit">Create</button>
        </div>
        <div class="muted" style="margin-top:8px;">
          If you set HH:MM UTC, the scheduler checks every 60s and runs once per day at that time.
        </div>
      </form>
    </div>

    <div class="card">
      <h3 style="margin:0 0 6px 0;">Your automations</h3>
      <table>
        <thead>
          <tr>
            <th>Name</th><th>Type</th><th>Enabled</th><th>Daily (UTC)</th><th>Last run</th><th>Status</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {autos_rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


@app.route("/create", methods=["POST"])
def create_automation():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    name = (request.form.get("name") or "").strip()
    typ = (request.form.get("type") or "generic").strip()
    run_daily_at = validate_hhmm(request.form.get("run_daily_at"))

    if not name:
        return redirect(url_for("home"))

    a = Automation(
        user_id=u.id,
        name=name,
        type=typ,
        run_daily_at=run_daily_at,
        enabled=True,
        description="",
        config_json="{}",
    )
    db.session.add(a)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/toggle/<int:automation_id>")
def toggle_automation(automation_id):
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    a = Automation.query.filter_by(id=automation_id, user_id=u.id).first()
    if not a:
        return redirect(url_for("home"))

    a.enabled = not a.enabled
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/run/<int:automation_id>")
def run_now(automation_id):
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    a = Automation.query.filter_by(id=automation_id, user_id=u.id).first()
    if not a:
        return redirect(url_for("home"))

    run_and_log(a, source="manual")
    return redirect(url_for("home"))


# ---------------- Health ----------------
@app.route("/health")
def health():
    c = get_smtp_config()
    return jsonify({
        "status": "ok",
        "time_utc": now_utc().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "db_path": DB_PATH,
        "scheduler_running": scheduler.running,
        "utc_hhmm_now": utc_hhmm_now(),
        "sheets": {
            "service_account_email": service_account_email(),
            "spreadsheet_id": GSHEETS_SPREADSHEET_ID,
            "worksheet": GSHEETS_WORKSHEET,
        },
        "smtp": {
            "configured": smtp_config_ok(),
            "smtp_host": c["host"],
            "smtp_port": c["port"],
            "smtp_user": c["user"],
            "alert_to": c["alert_to"],
            "debug": c["debug"],
        }
    })


# ---------------- Main ----------------
if __name__ == "__main__":
    dev_reset_db_if_schema_old()
    with app.app_context():
        db.create_all()
    start_scheduler_once()

    print("Running at http://localhost:5000")
    print("Sheets service account:", service_account_email())
    print("SMTP configured:", smtp_config_ok())

    # Disable reloader to avoid config mismatch / double-process behavior. [web:842]
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
