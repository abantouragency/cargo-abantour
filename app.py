a/cargo_system\app.py → b/cargo_system\app.py
@@ -1,33 +1,30 @@
 # -*- coding: utf-8 -*-
 """
-Aban Tour - Air Cargo Management System (cargo.abantour.ir)
-Standalone Flask app: landing page + order submission + tracking + admin panel.
-Database: SQLite (orders.db). No external deps beyond Flask + stdlib.
+Aban Tour - Air Cargo Management System (cargo.abantour.ir / Render)
+SINGLE-FILE Flask app: landing + order submit + tracking + admin.
+DB: SQLite (orders.db). No external deps beyond Flask + stdlib.
+Templates are embedded as strings so no templates/ folder is needed.
 """
-import os, sqlite3, json, secrets, datetime, smtplib
-from flask import Flask, render_template_string, request, redirect, url_for, jsonify, abort
+import os, sqlite3, json, secrets, datetime, threading
+from flask import Flask, request, redirect, url_for, jsonify
 
 app = Flask(__name__)
 BASE = os.path.dirname(os.path.abspath(__file__))
 DB = os.path.join(BASE, "orders.db")
 
-# ---- Telegram notify config (set via env or edit here) ----
-BOT_TOKEN = os.environ.get("TG_TOKEN", "7211437782:AAHqK5cN3X3X3X3X3X3X3X3X3X3X3X3X3X3X3X")  # placeholder
-TG_CHAT = os.environ.get("TG_CHAT", "67391189")  # owner id
+# ---- Telegram notify (set via env or edit) ----
+import os as _os
+BOT_TOKEN = _os.environ.get("TG_TOKEN", "")
+TG_CHAT = _os.environ.get("TG_CHAT", "67391189")
 
 def init_db():
-    conn = sqlite3.connect(DB)
-    c = conn.cursor()
+    conn = sqlite3.connect(DB); c = conn.cursor()
     c.execute('''CREATE TABLE IF NOT EXISTS orders (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
-        tracking TEXT UNIQUE,
-        name TEXT, phone TEXT, email TEXT,
-        origin TEXT, destination TEXT,
-        cargo_type TEXT, weight REAL, dims TEXT,
-        incoterm TEXT, service TEXT,
-        desc TEXT, status TEXT DEFAULT 'ثبت شده',
-        created_at TEXT, updated_at TEXT
-    )''')
+        tracking TEXT UNIQUE, name TEXT, phone TEXT, email TEXT,
+        origin TEXT, destination TEXT, cargo_type TEXT, weight REAL, dims TEXT,
+        incoterm TEXT, service TEXT, desc TEXT, status TEXT DEFAULT 'ثبت شده',
+        created_at TEXT, updated_at TEXT)''')
     conn.commit(); conn.close()
 
 init_db()
@@ -36,13 +33,13 @@
     return "ABN-" + datetime.datetime.now().strftime("%Y%m") + "-" + secrets.token_hex(3).upper()
 
 def tg_notify(text):
-    """Fire-and-forget: never block the request, never crash on failure."""
-    import threading
+    if not BOT_TOKEN:
+        return
     def _send():
         try:
+            import urllib.request, urllib.parse
             url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
             data = {"chat_id": TG_CHAT, "text": text, "parse_mode": "HTML"}
-            import urllib.request, urllib.parse
             req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                   headers={"User-Agent":"cargo-system"})
             urllib.request.urlopen(req, timeout=5)
@@ -50,10 +47,317 @@
             print("TG notify failed:", e)
     threading.Thread(target=_send, daemon=True).start()
 
-# ===== HTML templates (inline for single-file simplicity) =====
-LANDING = open(os.path.join(BASE, "templates", "landing.html"), encoding="utf-8").read()
-ADMIN = open(os.path.join(BASE, "templates", "admin.html"), encoding="utf-8").read()
-TRACK = open(os.path.join(BASE, "templates", "track.html"), encoding="utf-8").read()
+# ===== Embedded templates =====
+LANDING = r'''<!DOCTYPE html>
+<html lang="fa" dir="rtl">
+<head>
+<meta charset="utf-8">
… omitted 318 diff line(s) across 1 additional file(s)/section(s)
