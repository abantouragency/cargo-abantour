# -*- coding: utf-8 -*-
"""
Aban Tour - Air Cargo Management System (cargo.abantour.ir)
Standalone Flask app: landing page + order submission + tracking + admin panel.
Database: SQLite (orders.db). No external deps beyond Flask + stdlib.
"""
import os, sqlite3, json, secrets, datetime, smtplib
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, abort

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "orders.db")

# ---- Telegram notify config (set via env or edit here) ----
BOT_TOKEN = os.environ.get("TG_TOKEN", "7211437782:AAHqK5cN3X3X3X3X3X3X3X3X3X3X3X3X3X3X3X")  # placeholder
TG_CHAT = os.environ.get("TG_CHAT", "67391189")  # owner id

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT UNIQUE,
        name TEXT, phone TEXT, email TEXT,
        origin TEXT, destination TEXT,
        cargo_type TEXT, weight REAL, dims TEXT,
        incoterm TEXT, service TEXT,
        desc TEXT, status TEXT DEFAULT 'ثبت شده',
        created_at TEXT, updated_at TEXT
    )''')
    conn.commit(); conn.close()

init_db()

def new_tracking():
    return "ABN-" + datetime.datetime.now().strftime("%Y%m") + "-" + secrets.token_hex(3).upper()

def tg_notify(text):
    """Fire-and-forget: never block the request, never crash on failure."""
    import threading
    def _send():
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": TG_CHAT, "text": text, "parse_mode": "HTML"}
            import urllib.request, urllib.parse
            req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                  headers={"User-Agent":"cargo-system"})
            urllib.request.urlopen(req, timeout=5)
        except Exception as e:
            print("TG notify failed:", e)
    threading.Thread(target=_send, daemon=True).start()

# ===== HTML templates (inline for single-file simplicity) =====
LANDING = open(os.path.join(BASE, "templates", "landing.html"), encoding="utf-8").read()
ADMIN = open(os.path.join(BASE, "templates", "admin.html"), encoding="utf-8").read()
TRACK = open(os.path.join(BASE, "templates", "track.html"), encoding="utf-8").read()

@app.route("/")
def index():
    return render_template_string(LANDING)

@app.route("/submit", methods=["POST"])
def submit():
    f = request.form
    tracking = new_tracking()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("""INSERT INTO orders (tracking,name,phone,email,origin,destination,
        cargo_type,weight,dims,incoterm,service,desc,status,created_at,updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (tracking, f.get("name"), f.get("phone"), f.get("email"),
         f.get("origin"), f.get("destination"), f.get("cargo_type"),
         f.get("weight") or 0, f.get("dims"), f.get("incoterm"),
         f.get("service"), f.get("desc"), "ثبت شده", now, now))
    conn.commit(); conn.close()
    tg_notify(f"📦 <b>سفارش بار جدید</b>\nشماره رهگیری: <code>{tracking}</code>\n"
              f"نام: {f.get('name')}\nمبدأ: {f.get('origin')} → مقصد: {f.get('destination')}\n"
              f"نوع: {f.get('cargo_type')} | وزن: {f.get('weight')} کیلو")
    return jsonify({"ok": True, "tracking": tracking})

@app.route("/track/<tracking>")
def track(tracking):
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE tracking=?", (tracking,))
    row = c.fetchone(); conn.close()
    if not row:
        return render_template_string(TRACK, order=None, tracking=tracking)
    cols = ["id","tracking","name","phone","email","origin","destination","cargo_type",
            "weight","dims","incoterm","service","desc","status","created_at","updated_at"]
    order = dict(zip(cols, row))
    return render_template_string(TRACK, order=order, tracking=tracking)

@app.route("/track")
def track_q():
    t = request.args.get("t")
    if t: return redirect(url_for("track", tracking=t))
    return render_template_string(TRACK, order=None, tracking=None)

@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = c.fetchall(); conn.close()
    cols = ["id","tracking","name","phone","email","origin","destination","cargo_type",
            "weight","dims","incoterm","service","desc","status","created_at","updated_at"]
    orders = [dict(zip(cols, r)) for r in rows]
    return render_template_string(ADMIN, orders=orders)

@app.route("/admin/update/<int:oid>", methods=["POST"])
def admin_update(oid):
    status = request.form.get("status")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("UPDATE orders SET status=?, updated_at=? WHERE id=?", (status, now, oid))
    conn.commit(); conn.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
