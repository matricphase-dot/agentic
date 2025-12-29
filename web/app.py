import os
import json
import sqlite3
import random
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime, date, timezone
from urllib.parse import urlencode

import gspread
from flask import Flask, jsonify, request, redirect, url_for, session, abort
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from templates_data import GALLERY_TEMPLATES

PH_MODE = os.environ.get("PH_MODE", "0") == "1"

# ---------------- Paths ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
DB_URI = "sqlite:///" + DB_PATH.replace("\\", "/")

# ---------------- Flask app ----------------
app = Flask(__name__)

secret = os.environ.get("SECRET_KEY")
if PH_MODE and not secret:
    raise RuntimeError("SECRET_KEY env var is required when PH_MODE=1")
app.secret_key = secret or "dev-not-secure-change-me"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI", DB_URI)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
scheduler = BackgroundScheduler(daemon=True)


@app.errorhandler(403)
def forbidden(e):
    return """
    <h1>Forbidden</h1>
    <p>Admins only.</p>
    <p><a href="/">Back to dashboard</a></p>
    """, 403
@app.after_request
def add_security_headers(resp):
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Strict baseline CSP (works because you use inline <style>; allows inline styles)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline';"
    return resp


# ---------------- Google Sheets config ----------------
DEFAULT_SPREADSHEET_ID = "1CmNDVr2t4JWwmnZkRymxMw-ybgZ7gNiICIiR3yuMX1I"
SERVICE_ACCOUNT_FILE = os.environ.get(
    "GSHEETS_SERVICE_ACCOUNT_FILE",
    os.path.join(BASE_DIR, "service_account.json"),
)
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

    # Power launch: v1 "Efficiency score"
    minutes_saved_per_run = db.Column(db.Integer, default=5, nullable=False)
    total_minutes_saved = db.Column(db.Integer, default=0, nullable=False)

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


def migrate_add_columns_if_missing():
    """
    Lightweight migration helper (SQLite).
    Adds new columns if they are missing, without deleting DB.
    """
    if not os.path.exists(DB_PATH):
        return

    cols = set(sqlite_table_columns(DB_PATH, "automation"))
    if not cols:
        return

    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()

        if "minutes_saved_per_run" not in cols:
            cur.execute("ALTER TABLE automation ADD COLUMN minutes_saved_per_run INTEGER NOT NULL DEFAULT 5;")

        if "total_minutes_saved" not in cols:
            cur.execute("ALTER TABLE automation ADD COLUMN total_minutes_saved INTEGER NOT NULL DEFAULT 0;")

        con.commit()
    finally:
        con.close()


# ---------------- Helpers ----------------
def now_utc():
    return datetime.now(timezone.utc)


def utc_hhmm_now():
    n = now_utc()
    return f"{n.hour:02d}:{n.minute:02d}"


def has_run_today(dt: datetime | None):
    if not dt:
        return False
    # compare in UTC (avoids timezone edge cases)
    return dt.astimezone(timezone.utc).date() == now_utc().date()


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
from functools import wraps
from flask import redirect, url_for, request

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return wrapper

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    return db.session.get(User, uid)

from functools import wraps
from flask import abort, request
import os

ADMIN_EMAILS = {
    "aadityamex3006@gmail.com",
}
ADMIN_EMAILS = {e.strip().lower() for e in ADMIN_EMAILS}
print("ADMIN_EMAILS =", sorted(ADMIN_EMAILS))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        u = current_user()
        if not u:
            abort(403)

        email = (getattr(u, "email", "") or "").strip().lower()
        print("ADMIN CHECK email =", email)
        print("ADMIN_EMAILS =", sorted([e.strip().lower() for e in ADMIN_EMAILS]))

        if email not in {e.strip().lower() for e in ADMIN_EMAILS}:
            abort(403)

        return f(*args, **kwargs)
    return wrapper


def format_dt(dt):
    if not dt:
        return "-"
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

    return {"host": host, "port": port, "user": user, "password": password, "alert_to": alert_to, "debug": debug}


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


def send_failure_email(automation: Automation, run_message: str):
    if not smtp_config_ok():
        return
    c = get_smtp_config()
    subject = f"Automation failed: {automation.name}"
    body = (
        f"Automation failure detected\n\n"
        f"Automation: {automation.name}\n"
        f"Type: {automation.type}\n"
        f"Time (UTC): {now_utc().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"Details:\n{run_message}\n"
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
    ws.append_row(["timestamp_utc", "name", "email", "phone", "message", "source"], value_input_option="RAW")


def append_lead_to_sheet(name, email, phone, message, source):
    ws = get_ws()
    ensure_leads_header(ws)

    ts = now_utc().strftime("%Y-%m-%d %H:%M:%S UTC")
    row = [ts, name or "", email or "", phone or "", message or "", source]
    ws.append_row(row, value_input_option="RAW")
    return ts


# ---------------- Execution engine (demo + v1 autopilot) ----------------
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

    # Generic simulation (safe v1 placeholder)
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

    if status == "success":
        try:
            automation.total_minutes_saved = int(automation.total_minutes_saved or 0) + int(automation.minutes_saved_per_run or 0)
        except Exception:
            pass

    r = Run(
        automation_id=automation.id,
        status=status,
        message=f"[{source}] {message}",
        created_at=t,
    )
    db.session.add(r)
    db.session.commit()

    if status != "success":
        try:
            send_failure_email(automation, r.message or "")
        except Exception:
            pass


def scheduler_tick():
    with app.app_context():
        hhmm = utc_hhmm_now()
        autos = Automation.query.filter(
            Automation.enabled.is_(True),
            Automation.run_daily_at == hhmm,
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
        coalesce=True,
        misfire_grace_time=300,  # allow 5 min late
        max_instances=1,
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
@app.route("/debug/whoami")
def debug_whoami():
    u = current_user()
    if not u:
        return "not logged in"
    email = (getattr(u, "email", "") or "")
    return f"raw={email} normalized={email.strip().lower()}"


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

    # Do NOT display sensitive IDs/emails on PH
    sheets_connected = "YES" if bool(service_account_email()) and bool(GSHEETS_SPREADSHEET_ID) and bool(GSHEETS_WORKSHEET) else "NO"

    autos = Automation.query.filter_by(user_id=u.id).order_by(Automation.created_at.desc()).all()

    # Onboarding checklist signals
    has_any = len(autos) > 0
    has_demo = any((a.name or "") == "Demo: Daily report → email (simulated)" for a in autos)
    has_schedule = any(bool(a.run_daily_at) for a in autos)
    done_count = sum([1 if has_demo else 0, 1 if has_any else 0, 1 if has_schedule else 0])

    checklist_html = f"""
    <div class="card">
      <h3 style="margin:0 0 10px 0;">Getting started ({done_count}/3)</h3>
      <div class="muted" style="margin-bottom:10px;">Complete these to unlock the “aha” moment.</div>
      <div style="display:grid;grid-template-columns:1fr;gap:8px;font-size:13px;">
        <div>{'✅' if has_demo else '⬜'} Run the demo automation (1 click)</div>
        <div>{'✅' if has_any else '⬜'} Create your first automation</div>
        <div>{'✅' if has_schedule else '⬜'} Set a daily schedule (HH:MM UTC)</div>
      </div>

      <div style="margin-top:12px; display:flex; gap:10px; flex-wrap:wrap;">
        <form method="post" action="/demo" style="margin:0;">
          <button type="submit" {'disabled' if has_demo else ''}>Run demo</button>
        </form>
        <a href="#create" style="align-self:center;color:#667eea;text-decoration:none;">Create an automation ↓</a>
      </div>
    </div>
    """

    total_minutes = sum(int(a.total_minutes_saved or 0) for a in autos)
    total_hours = total_minutes / 60.0

    failing = [a for a in autos if (a.last_status == "fail")]

    if not failing:
        health_html = """
        <div class="card">
          <h3 style="margin:0 0 10px 0;">Automation health</h3>
          <div class="muted">All automations running normally.</div>
        </div>
        """
    else:
        items = ""
        for a in failing[:8]:
            items += f"""
              <li>
                <b>{a.name}</b> —
                <a href="/runs/{a.id}">View runs</a>
                <form method="post" action="/fix/{a.id}" style="display:inline;margin-left:8px;">
                  <button type="submit" style="padding:6px 10px;border:none;border-radius:8px;background:#667eea;color:#fff;font-weight:700;cursor:pointer;">
                    Fix it (Beta)
                  </button>
                </form>
              </li>
            """

        health_html = f"""
        <div class="card">
          <h3 style="margin:0 0 10px 0;">Automation health</h3>
          <div class="muted" style="margin-bottom:8px;">Some automations need attention.</div>
          <ul style="margin:0;padding-left:18px;font-size:13px;color:#333;">
            {items}
          </ul>
        </div>
        """
    autos_rows = ""
    for a in autos:
        sched_badge = "Scheduled" if a.run_daily_at else "Manual"

        autos_rows += f"""
          <tr>
            <td>{a.name}</td>
            <td>{a.type}</td>
            <td>{'YES' if a.enabled else 'NO'}</td>
            <td>
              {a.run_daily_at or '-'}
              <span style="margin-left:8px;font-size:11px;padding:2px 8px;border-radius:999px;background:#f0f2ff;color:#334;">
                {sched_badge}
              </span>
            </td>
            <td>{format_dt(a.last_run_at)}</td>
            <td>{a.last_status or '-'}</td>
            <td>{int(a.minutes_saved_per_run or 0)} min</td>
            <td>
              <a href="/run/{a.id}">Run now</a>
              &nbsp;|&nbsp;
              <a href="/runs/{a.id}">Runs</a>
              &nbsp;|&nbsp;
              <a href="/toggle/{a.id}">{'Disable' if a.enabled else 'Enable'}</a>
              &nbsp;|&nbsp;
              <form method="post" action="/schedule/{a.id}/09:00" style="display:inline;">
                <button type="submit" style="padding:6px 10px;border:none;border-radius:8px;background:#111;color:#fff;font-weight:700;cursor:pointer;">
                  Schedule 09:00 UTC
                </button>
              </form>
            </td>
          </tr>
        """

    if not autos_rows:
        autos_rows = """
          <tr>
            <td colspan='8' style='color:#666;font-size:13px;'>
              No automations yet. Create one below — or run a demo to see how it works.
              <form method="post" action="/demo" style="display:inline;margin-left:10px;">
                <button type="submit">Run demo</button>
              </form>
            </td>
          </tr>
        """

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
    .badge {{display:inline-block;font-size:11px;padding:3px 8px;border-radius:999px;background:#111;color:#fff;margin-left:8px;}}
    .cols {{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}}
    @media (max-width: 900px) {{ .cols {{grid-template-columns:1fr;}} }}
    .mini {{border:1px solid #eee;border-radius:12px;padding:12px;}}
    .mini h4 {{margin:0 0 6px 0;}}
    .pill {{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;background:#f0f2ff;color:#334;}}
    .coming {{opacity:0.75;}}
  </style>
</head>
<body>
  <div class="container">
    <div class="top">
      <div>Signed in as {u.email}</div>
      <div style="display:flex;gap:12px;align-items:center;">
        <a href="/autopilot">Autopilot</a>
        <a href="/gallery">Gallery</a>
        <a href="/lead">Lead form</a>
        <a href="/health">Health</a>
        <a href="/logout">Log out</a>
      </div>
    </div>

    <div class="card">
      <h1>AUTO-PILOT <span class="badge">BETA</span></h1>
      <div class="muted">
        Connections — Sheets: <b>{sheets_connected}</b> &nbsp;•&nbsp; SMTP: <b>{smtp_status}</b><br>
        Hours given back: <b>{total_hours:.1f}h</b> (v1 estimate)
      </div>
      <div class="muted" style="margin-top:8px;">
        Beta note: Some features are experimental. Use “Runs” for logs and report issues during launch.
      </div>
    </div>

    <div class="card">
      <h3 style="margin:0 0 10px 0;">Roadmap (Live / Beta / Coming soon)</h3>
      <div class="cols">
        <div class="mini">
          <div class="pill">LIVE</div>
          <h4>Core automation control</h4>
          <ul style="margin:6px 0 0 18px;color:#333;font-size:13px;">
            <li>Create automation + schedule</li>
            <li>Run now + Run history</li>
            <li>Admin runs viewer</li>
          </ul>
        </div>

        <div class="mini">
          <div class="pill">BETA</div>
          <h4>AI + reliability</h4>
          <ul style="margin:6px 0 0 18px;color:#333;font-size:13px;">
            <li><a href="/autopilot">Autopilot: goal → automation</a></li>
            <li><a href="/gallery">Curated automation gallery</a></li>
            <li>Health “Fix it” (rerun + logs)</li>
          </ul>
        </div>

        <div class="mini coming">
          <div class="pill">COMING SOON</div>
          <h4>Watch you work</h4>
          <ul style="margin:6px 0 0 18px;color:#333;font-size:13px;">
            <li>Desktop “Automate this” recorder widget</li>
            <li>Community automation gallery</li>
            <li>Self-improving automations</li>
          </ul>

          <form method="post" action="/waitlist" style="margin-top:10px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
            <input name="email" value="{u.email}" placeholder="Email" style="min-width:220px;">
            <input type="hidden" name="feature_key" value="desktop_recorder">
            <button type="submit">Join waitlist</button>
            <div class="muted">Get early access.</div>
          </form>
        </div>
      </div>
    </div>

    {health_html}
    {checklist_html}

    <div class="card" id="create">
      <h3 style="margin:0 0 10px 0;">Create automation</h3>
      <form method="post" action="/create">
        <div class="row">
          <input name="name" placeholder="Automation name" required>
          <select name="type">
            <option value="leads_sheet">leads_sheet (demo)</option>
            <option value="generic">generic (simulated)</option>
          </select>
          <input name="run_daily_at" placeholder="HH:MM UTC (optional)">
          <input name="minutes_saved_per_run" placeholder="Minutes saved/run (optional)">
          <button type="submit">Create</button>
        </div>
        <div class="muted" style="margin-top:8px;">
          If you set HH:MM UTC, the scheduler checks every 60 seconds and runs once per day at that time.
        </div>
      </form>
    </div>

    <div class="card">
      <h3 style="margin:0 0 6px 0;">Your automations</h3>
      <table>
        <thead>
          <tr>
            <th>Name</th><th>Type</th><th>Enabled</th><th>Daily (UTC)</th><th>Last run</th><th>Status</th><th>Saves/run</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {autos_rows}
        </tbody>
      </table>
      <div class="muted" style="margin-top:8px;">
        Tip: Use “Runs” to see logs. For system-wide logs use <a href="/admin/runs">Admin runs</a>.
      </div>
    </div>
  </div>
</body>
</html>
"""


from urllib.parse import urlparse

@app.route("/schedule/<int:automation_id>/<hhmm>", methods=["POST"])
def quick_schedule(automation_id, hhmm):
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    a = Automation.query.filter_by(id=automation_id, user_id=u.id).first()
    if not a:
        return redirect(url_for("home"))

    hhmm = validate_hhmm(hhmm)
    if not hhmm:
        return redirect(url_for("home"))

    a.run_daily_at = hhmm
    a.enabled = True
    db.session.commit()

    # Redirect back to the page the user clicked from (dashboard usually).
    ref = request.headers.get("Referer") or ""
    try:
        p = urlparse(ref)
        if p.scheme in ("http", "https") and p.netloc:
            return redirect(ref)
    except Exception:
        pass

    return redirect(url_for("home"))



@app.route("/create", methods=["POST"])
def create_automation():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    name = (request.form.get("name") or "").strip()
    typ = (request.form.get("type") or "generic").strip()
    run_daily_at = validate_hhmm(request.form.get("run_daily_at"))
    mins_raw = (request.form.get("minutes_saved_per_run") or "").strip()

    minutes_saved_per_run = 5
    if mins_raw.isdigit():
        minutes_saved_per_run = max(0, min(240, int(mins_raw)))  # cap at 4h per run

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
        minutes_saved_per_run=minutes_saved_per_run,
        total_minutes_saved=0,
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


@app.route("/runs/<int:automation_id>")
def view_runs(automation_id):
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    a = Automation.query.filter_by(id=automation_id, user_id=u.id).first()
    if not a:
        return redirect(url_for("home"))

    runs = Run.query.filter_by(automation_id=a.id).order_by(Run.created_at.desc()).limit(50).all()

    rows = ""
    for r in runs:
        rows += f"""
          <tr>
            <td>{format_dt(r.created_at)}</td>
            <td>{r.status}</td>
            <td style="white-space:pre-wrap;">{(r.message or "-")}</td>
          </tr>
        """

    if not rows:
        rows = "<tr><td colspan='3' style='color:#666;font-size:13px;'>No runs yet.</td></tr>"

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Runs • {a.name}</title>
  <style>
    body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fb;margin:0;}}
    .container {{max-width:1100px;margin:0 auto;padding:14px 10px 30px;}}
    .card {{background:#fff;border-radius:12px;padding:14px 12px;margin-top:12px;box-shadow:0 2px 10px rgba(0,0,0,0.06);}}
    table {{width:100%;border-collapse:collapse;margin-top:10px;}}
    th, td {{text-align:left;border-bottom:1px solid #eee;padding:10px 8px;font-size:13px;vertical-align:top;}}
    th {{font-size:12px;color:#666;}}
    a {{color:#667eea;text-decoration:none;}}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div>
          <h2 style="margin:0;color:#667eea;">Run history</h2>
          <div style="font-size:12px;color:#666;">Automation: <b>{a.name}</b> • Type: <b>{a.type}</b></div>
        </div>
        <div style="display:flex;gap:12px;">
          <a href="/run/{a.id}">Run now</a>
          <a href="/">Back</a>
        </div>
      </div>

      <table>
        <thead><tr><th>Time (UTC)</th><th>Status</th><th>Message</th></tr></thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""


from flask import render_template_string
@app.route("/waitlist", methods=["POST"])
def waitlist():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    email = (request.form.get("email") or u.email or "").strip().lower()
    feature_key = (request.form.get("feature_key") or "").strip()

    if not email or not feature_key:
        return redirect(url_for("home"))

    with sqlite3.connect(r"d:\agentic-core\web\app.db") as c:
        c.execute(
            "INSERT INTO waitlist (email, feature_key, created_at) VALUES (?, ?, ?)",
            (email, feature_key, now_utc().strftime("%Y-%m-%d %H:%M:%S")),
        )
        c.commit()

    # If the current user is admin, jump to the admin list
    if (getattr(u, "email", "") or "").strip().lower() in {e.strip().lower() for e in ADMIN_EMAILS}:
        return redirect("/admin/waitlist")

    return redirect(url_for("home"))

@app.route("/admin/run/<int:run_id>")
@login_required
@admin_required
def admin_run_detail(run_id):
    if PH_MODE:
        abort(404)
    with sqlite3.connect(r"d:\agentic-core\web\app.db") as c:
        c.row_factory = sqlite3.Row
        r = c.execute("""
          SELECT r.id, r.status, r.message, r.created_at, r.raw_response_json,
                 r.automation_id, a.name AS automation_name
          FROM run r
          LEFT JOIN automation a ON a.id = r.automation_id
          WHERE r.id = ?
          LIMIT 1
        """, (run_id,)).fetchone()

    if not r:
        return "Not found", 404

    def esc(x):
        return ("" if x is None else str(x)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    return f"""
    <html>
      <head>
        <title>Admin: Run #{esc(r['id'])}</title>
        <style>
          body {{ font-family: Arial, sans-serif; background:#f6f7fb; }}
          .wrap {{ max-width: 1100px; margin: 40px auto; background:#fff; padding: 18px 22px; border-radius: 10px; }}
          .muted {{ color:#777; font-size:12px; }}
          pre {{ white-space: pre-wrap; background:#0b1020; color:#e8e8e8; padding:12px; border-radius:10px; overflow:auto; }}
          a {{ color:#667eea; text-decoration:none; }}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
              <h2 style="margin:0;">Run #{esc(r['id'])}</h2>
              <div class="muted">
                Automation: {esc(r['automation_name'] or '-') } ({esc(r['automation_id'])}) •
                Status: {esc(r['status'])} •
                Created: {esc(r['created_at'])}
              </div>
            </div>
            <div><a href="/admin/runs">Back</a></div>
          </div>

          <h3>Message</h3>
          <pre>{esc(r["message"] or "-")}</pre>

          <h3>Raw JSON</h3>
          <pre>{esc(r["raw_response_json"] or "-")}</pre>
        </div>
      </body>
    </html>
    """
import csv
from io import StringIO
from flask import Response
import sqlite3

from flask import abort, request  # ensure these are imported once somewhere

@app.route("/admin/waitlist", methods=["GET"])
@login_required
@admin_required
def admin_waitlist():
    if PH_MODE:
        abort(404)

    export = request.args.get("export")
    with sqlite3.connect(r"d:\agentic-core\web\app.db") as c:
        c.row_factory = sqlite3.Row
        rows = c.execute("""
            SELECT id, email, feature_key, created_at
            FROM waitlist
            ORDER BY id DESC
            LIMIT 500
        """).fetchall()

    if export == "csv":
        sio = StringIO()
        w = csv.writer(sio)
        w.writerow(["id", "email", "feature_key", "created_at"])
        for r in rows:
            w.writerow([r["id"], r["email"], r["feature_key"], r["created_at"]])

        return Response(
            sio.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=waitlist.csv"},
        )

    def esc(x):
        return ("" if x is None else str(x)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    trs = ""
    for r in rows:
        trs += f"""
        <tr>
          <td>{esc(r["id"])}</td>
          <td>{esc(r["email"])}</td>
          <td>{esc(r["feature_key"])}</td>
          <td>{esc(r["created_at"])}</td>
        </tr>
        """

    if not trs:
        trs = "<tr><td colspan='4' class='muted'>No waitlist signups yet.</td></tr>"

    return f"""
    <html>
      <head>
        <title>Admin: Waitlist</title>
        <style>
          body {{ font-family: Arial, sans-serif; background: #f6f7fb; }}
          .wrap {{ max-width: 1100px; margin: 40px auto; background: #fff; padding: 18px 22px; border-radius: 10px; }}
          table {{ width:100%; border-collapse: collapse; margin-top: 12px; }}
          th, td {{ border-bottom: 1px solid #eee; padding: 10px 8px; text-align:left; font-size: 14px; }}
          th {{ color:#555; font-weight: 600; }}
          a {{ color:#667eea; text-decoration:none; }}
          .top {{ display:flex; justify-content:space-between; align-items:center; }}
          .muted {{ color:#777; font-size:12px; }}
          .btn {{ display:inline-block; padding:8px 10px; border-radius:10px; background:#667eea; color:#fff; font-weight:700; }}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="top">
            <div>
              <h2 style="margin:0;">Admin: Waitlist</h2>
              <div class="muted">Showing last 500 signups.</div>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
              <a class="btn" href="/admin/waitlist?export=csv">Export CSV</a>
              <a href="/">Back</a>
            </div>
          </div>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Feature</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {trs}
            </tbody>
          </table>
        </div>
      </body>
    </html>
    """

from flask import abort, request  # ensure abort is imported somewhere once

@app.route("/admin/runs", methods=["GET"])
@login_required
@admin_required
def admin_runs():
    if PH_MODE:
        abort(404)

    # Query params
    status = request.args.get("status")
    automation_id = request.args.get("automation_id", type=int)
    limit = request.args.get("limit", default=50, type=int)
    limit = max(1, min(limit, 200))
    # Build WHERE safely (note table alias "r.")
    where = []
    params = []

    if status:
        where.append("r.status = ?")
        params.append(status)

    if automation_id is not None:
        where.append("r.automation_id = ?")
        params.append(automation_id)

    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    # JOIN to show automation name
    sql = f"""
    SELECT
      r.id,
      r.automation_id,
      a.name AS automation_name,
      r.status,
      r.message,
      r.created_at,
      r.raw_response_json
    FROM run r
    LEFT JOIN automation a ON a.id = r.automation_id
    {where_sql}
    ORDER BY r.id DESC
    LIMIT ?
    """
    params.append(limit)

    # Query SQLite
    with sqlite3.connect(r"d:\agentic-core\web\app.db") as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, params).fetchall()

    # Render helpers
    def esc(x):
        return ("" if x is None else str(x)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Preserve current filters and only change automation_id
    def view_runs_url(aid):
        q = request.args.to_dict(flat=True)
        q["automation_id"] = str(aid)
        return "/admin/runs?" + urlencode(q)

    trs = []
    for r in rows:
        rid = r["id"]
        aid = r["automation_id"]
        aname = r["automation_name"] or f"#{aid}"
        st = r["status"]
        created = r["created_at"]
        msg = r["message"]
        raw = r["raw_response_json"]

        trs.append(f"""
        <tr>
          <td>
  {esc(rid)}
  <div><a href="/admin/run/{esc(rid)}">View</a></div>
</td>

          <td>
            {esc(aname)} <span class="muted">({esc(aid)})</span>
            <div><a href="{view_runs_url(aid)}">View runs</a></div>
          </td>
          <td>{esc(st)}</td>
          <td style="font-family:monospace;">{esc(created)}</td>
          <td style="max-width:720px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{esc(msg)}</td>
          <td>{("-" if not raw else "json")}</td>
        </tr>
        """)

    table_html = "\n".join(trs) or "<tr><td colspan='6'>No runs found.</td></tr>"

    return f"""
    <html>
      <head>
        <title>Admin: Recent runs</title>
        <style>
          body {{ font-family: Arial, sans-serif; background: #f6f7fb; }}
          .wrap {{ max-width: 1100px; margin: 40px auto; background: #fff; padding: 18px 22px; border-radius: 10px; }}
          table {{ width: 100%; border-collapse: collapse; }}
          th, td {{ border-bottom: 1px solid #eee; padding: 10px 8px; text-align: left; font-size: 14px; }}
          th {{ color: #555; font-weight: 600; }}
          .top {{ display:flex; justify-content:space-between; align-items:center; }}
          .muted {{ color:#777; font-size:12px; }}
          .filters input {{ padding:6px 8px; }}
          .filters button {{ padding:6px 10px; }}
        </style>
      </head>
      <body>
        <div class="wrap">
          <div class="top">
            <div>
              <h2 style="margin:0;">Admin: Recent runs</h2>
              <div class="muted">Filtered results (limit={esc(limit)}).</div>
            </div>
            <div><a href="/">Back to dashboard</a></div>
          </div>

          <form class="filters" method="get" style="margin:12px 0; display:flex; gap:10px; align-items:flex-end;">
            <div>
              <div class="muted">Status</div>
              <input name="status" value="{esc(status)}" placeholder="success/fail">
            </div>
            <div>
              <div class="muted">Automation ID</div>
              <input name="automation_id" value="{esc(automation_id)}" placeholder="3">
            </div>
            <div>
              <div class="muted">Limit</div>
              <input name="limit" value="{esc(limit)}" style="width:80px;">
            </div>
            <button type="submit">Filter</button>
            <a href="/admin/runs" style="margin-left:6px;">Clear</a>
          </form>

          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Automation</th>
                <th>Status</th>
                <th>Created</th>
                <th>Message</th>
                <th>Raw JSON</th>
              </tr>
            </thead>
            <tbody>
              {table_html}
            </tbody>
          </table>
        </div>
      </body>
    </html>
    """

@app.route("/demo", methods=["POST"])
def create_demo():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    # Reuse existing demo if present
    existing = Automation.query.filter_by(
        user_id=u.id,
        type="generic",
        name="Demo: Daily report → email (simulated)",
    ).first()

    a = existing
    if not a:
        a = Automation(
            user_id=u.id,
            name="Demo: Daily report → email (simulated)",
            type="generic",
            run_daily_at=None,
            enabled=True,
            description="Demo automation created for first-run onboarding.",
            config_json=json.dumps({"demo": True}),
            minutes_saved_per_run=15,
            total_minutes_saved=0,
        )
        db.session.add(a)
        db.session.commit()

    run_and_log(a, source="demo_run")
    return redirect(f"/runs/{a.id}")


@app.route("/autopilot", methods=["GET", "POST"])
def autopilot():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    if request.method == "POST":
        goal = (request.form.get("goal") or "").strip()
        minutes_raw = (request.form.get("minutes_saved_per_run") or "").strip()
        run_daily_at = validate_hhmm(request.form.get("run_daily_at"))

        if not goal:
            return redirect(url_for("autopilot"))

        minutes_saved_per_run = 15
        if minutes_raw.isdigit():
            minutes_saved_per_run = max(0, min(240, int(minutes_raw)))

        plan = {
            "goal": goal,
            "created_at_utc": now_utc().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "v1": True,
            "note": "v1: goal→automation. Desktop 'watch you work' recording is coming next.",
        }

        a = Automation(
            user_id=u.id,
            name=f"Autopilot: {goal[:40]}",
            type="generic",
            description="Autopilot-created automation (v1).",
            config_json=json.dumps(plan),
            run_daily_at=run_daily_at,
            enabled=True,
            minutes_saved_per_run=minutes_saved_per_run,
            total_minutes_saved=0,
        )
        db.session.add(a)
        db.session.commit()

        run_and_log(a, source="autopilot_created")
        return redirect(url_for("home"))

    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Autopilot</title>
  <style>
    body {font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fb;margin:0;}
    .container {max-width:760px;margin:0 auto;padding:14px 10px 30px;}
    .top {display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#555;}
    a {color:#667eea;text-decoration:none;}
    .card {background:#fff;border-radius:12px;padding:14px 12px;margin-top:12px;box-shadow:0 2px 10px rgba(0,0,0,0.06);}
    input {width:100%;padding:10px 12px;border-radius:10px;border:1px solid #ddd;font-size:14px;margin-top:8px;}
    button {margin-top:10px;padding:10px 12px;border:none;border-radius:10px;background:#667eea;color:#fff;font-weight:800;cursor:pointer;}
    .muted {font-size:12px;color:#666;margin-top:6px;}
  </style>
</head>
<body>
  <div class="container">
    <div class="top">
      <div>Autopilot</div>
      <div><a href="/">Back</a></div>
    </div>

    <div class="card">
      <h2 style="margin:0 0 6px 0;color:#667eea;">One‑Click Automate This (v1)</h2>
      <div class="muted">Describe a repetitive task. Autopilot will create an automation button in your dashboard and log the first run.</div>

      <form method="post" action="/autopilot">
        <input name="goal" placeholder='e.g., "Every Monday: generate weekly report and email it"' required>
        <input name="run_daily_at" placeholder="HH:MM UTC (optional)">
        <input name="minutes_saved_per_run" placeholder="Minutes saved/run (default 15)">
        <button type="submit">Automate this</button>
      </form>
    </div>
  </div>
</body>
</html>
"""
@app.route("/gallery")
def gallery():
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    cards = ""
    for t in GALLERY_TEMPLATES:
        cards += f"""
        <div class="card">
          <h3 style="margin:0 0 6px 0;color:#111;">{t['name']}</h3>
          <div style="font-size:13px;color:#555;margin-bottom:10px;">{t.get('description','')}</div>
          <div style="font-size:12px;color:#666;margin-bottom:10px;">
            Type: <b>{t['type']}</b> • Saves: <b>{t.get('minutes_saved_per_run', 5)} min/run</b>
          </div>
          <form method="post" action="/install/{t['id']}">
            <button type="submit">Install</button>
          </form>
        </div>
        """

    return f"""
<!doctype html>
<html><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Gallery</title>
  <style>
    body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fb;margin:0;}}
    .container {{max-width:900px;margin:0 auto;padding:14px 10px 30px;}}
    .top {{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:#555;}}
    a {{color:#667eea;text-decoration:none;}}
    .grid {{display:grid;grid-template-columns:1fr;gap:12px;margin-top:12px;}}
    .card {{background:#fff;border-radius:12px;padding:14px 12px;box-shadow:0 2px 10px rgba(0,0,0,0.06);}}
    button {{padding:9px 12px;border:none;border-radius:10px;background:#667eea;color:#fff;font-weight:700;cursor:pointer;}}
  </style>
</head>
<body>
  <div class="container">
    <div class="top">
      <div>Automation Gallery</div>
      <div><a href="/">Back</a></div>
    </div>
    <div class="grid">{cards}</div>
  </div>
</body>
</html>
"""


@app.route("/install/<template_id>", methods=["POST"])
def install_template(template_id):
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    t = next((x for x in GALLERY_TEMPLATES if x.get("id") == template_id), None)
    if not t:
        return redirect(url_for("gallery"))

    a = Automation(
        user_id=u.id,
        name=t["name"],
        type=t.get("type", "generic"),
        run_daily_at=None,
        enabled=True,
        description=t.get("description", ""),
        config_json=json.dumps({"installed_from_gallery": t.get("id")}),
        minutes_saved_per_run=int(t.get("minutes_saved_per_run", 5)),
        total_minutes_saved=0,
    )
    db.session.add(a)
    db.session.commit()

    run_and_log(a, source="gallery_install")
    return redirect(url_for("home"))
@app.route("/fix/<int:automation_id>", methods=["POST"])
def fix_automation(automation_id):
    u = current_user()
    if not u:
        return redirect(url_for("login"))

    a = Automation.query.filter_by(id=automation_id, user_id=u.id).first()
    if not a:
        return redirect(url_for("home"))

    # v1 "Fix it" = rerun once and log result
    run_and_log(a, source="fix_it")
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


def ensure_waitlist_table():
    # Uses SQLite directly so it's independent of SQLAlchemy migrations.
    with sqlite3.connect(r"d:\agentic-core\web\app.db") as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            feature_key TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        c.commit()


# ---------------- Main ----------------
if __name__ == "__main__":
    dev_reset_db_if_schema_old()
    migrate_add_columns_if_missing()

    with app.app_context():
        db.create_all()

    ensure_waitlist_table()

    start_scheduler_once()

    print("Running at http://localhost:5000")
    print("Sheets service account:", service_account_email())
    print("SMTP configured:", smtp_config_ok())

    # Disable reloader to avoid double-process behavior with schedulers.
    app.run(
    host="127.0.0.1",
    port=5000,
    debug=(not PH_MODE),
    use_reloader=False,
)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
from waitlist import waitlist_bp
app.register_blueprint(waitlist_bp, name='waitlist_page')
