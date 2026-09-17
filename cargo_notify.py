# -*- coding: utf-8 -*-
"""
Shared Telegram notification module for Aban Tour Cargo.
Used by BOTH the web service (app.py) and the bot (bot.py) so the
order/cargo message format stays identical everywhere.

Features (per user request):
  1. Inline button "مشاهده در پنل" -> opens admin panel
  2. Pretty HTML + easy-to-copy tracking code
  3. Dual notify: cargo channel (@abantour_cargo) + admin chat (67391189)
  4. Daily/weekly summary (build_summary)
  5. Filter by cargo type (hazardous/drug -> flagged in channel)
  6. Status-change messages (status_update_message)
"""
import os, urllib.request, urllib.parse, json, threading, datetime

BOT_TOKEN = os.environ.get("TG_TOKEN", "521451545:AAGcZvTXr3UHAuOIbij7wmuJ8dR-bpds5jI")
ADMIN_CHAT = os.environ.get("TG_CHAT", "67391189")
CARGO_CHANNEL = os.environ.get("TG_CHANNEL", "-1004497515605")  # @abantour_cargo
SITE = os.environ.get("CARGO_SITE", "https://cargo-abantour.onrender.com")

# Cargo types considered "sensitive / hazardous" -> flagged in channel
HAZARD_TYPES = {"دارو", "مواد غذایی", "بار حساس", "DG", "خطرناک"}

def _post(payload, timeout=8):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "cargo-notify"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print("TG post err:", e)
        return None

def _escape_html(s):
    if s is None:
        return "-"
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_order_message(o, source="وب‌سایت"):
    """Return (text_html, reply_markup) for a new order."""
    tr = _escape_html(o.get("tracking"))
    name = _escape_html(o.get("name"))
    phone = _escape_html(o.get("phone"))
    email = _escape_html(o.get("email") or "-")
    origin = _escape_html(o.get("origin"))
    dest = _escape_html(o.get("destination"))
    ctype = _escape_html(o.get("cargo_type"))
    weight = _escape_html(o.get("weight"))
    dims = _escape_html(o.get("dims") or "-")
    incoterm = _escape_html(o.get("incoterm") or "-")
    service = _escape_html(o.get("service"))
    desc = _escape_html(o.get("desc") or "-")
    status = _escape_html(o.get("status", "ثبت شده"))
    created = _escape_html(o.get("created_at"))

    # Hazard flag
    flag = ""
    if ctype in HAZARD_TYPES:
        flag = "\n🔴 <b>بار حساس / نیازمند توجه ویژه</b>"

    text = (
        "📦 <b>سفارش بار هوایی جدید - آبان تور</b>\n"
        f"🔖 <b>کد رهگیری:</b> <code>{tr}</code>\n"
        f"👤 <b>نام:</b> {name}\n"
        f"📱 <b>تماس:</b> {phone}\n"
        f"📧 <b>ایمیل:</b> {email}\n"
        f"📍 <b>مبدأ:</b> {origin}\n"
        f"🏁 <b>مقصد:</b> {dest}\n"
        f"📦 <b>نوع بار:</b> {ctype}\n"
        f"⚖️ <b>وزن:</b> {weight} کیلوگرم\n"
        f"📏 <b>ابعاد:</b> {dims}\n"
        f"📋 <b>Incoterm:</b> {incoterm}\n"
        f"🚚 <b>سرویس:</b> {service}\n"
        f"📝 <b>توضیحات:</b> {desc}\n"
        f"📊 <b>وضعیت:</b> {status}\n"
        f"🕐 <b>زمان ثبت:</b> {created}\n"
        f"🔗 <b>منبع:</b> {_escape_html(source)}\n"
        f"{flag}\n"
        f"――――――――――――\n"
        f"🔗 پیگیری: {SITE}/track/{tr}\n"
        f"📞 پشتیبانی: ۰۲۱۵۵۰۰۹۴۲۹ | @Abantourbot"
    )
    # Inline keyboard: view in panel + track
    markup = {
        "inline_keyboard": [
            [
                {"text": "📋 مشاهده در پنل مدیریت", "url": f"{SITE}/admin"},
                {"text": "🔍 پیگیری آنلاین", "url": f"{SITE}/track/{tr}"}
            ]
        ]
    }
    return text, markup

def build_status_message(o):
    """Status-change notification for channel + admin."""
    tr = _escape_html(o.get("tracking"))
    status = _escape_html(o.get("status"))
    origin = _escape_html(o.get("origin"))
    dest = _escape_html(o.get("destination"))
    name = _escape_html(o.get("name"))
    text = (
        f"🔄 <b>بروزرسانی وضعیت بار</b>\n"
        f"🔖 کد رهگیری: <code>{tr}</code>\n"
        f"👤 {name} | 📍 {origin} → {dest}\n"
        f"📊 وضعیت جدید: <b>{status}</b>\n"
        f"🔗 {SITE}/track/{tr}"
    )
    markup = {"inline_keyboard": [[{"text": "🔍 پیگیری آنلاین", "url": f"{SITE}/track/{tr}"}]]}
    return text, markup

def build_summary(orders, period="روزانه"):
    """Daily/weekly summary message."""
    if not orders:
        return "📊 <b>گزارش " + period + " بار هوایی آبان تور</b>\n\n✅ سفارش جدیدی در این بازه ثبت نشد.", None
    total = len(orders)
    total_weight = sum(float(o.get("weight") or 0) for o in orders)
    by_type = {}
    for o in orders:
        t = o.get("cargo_type", "سایر")
        by_type[t] = by_type.get(t, 0) + 1
    lines = "\n".join(f"  • {k}: {v} مورد" for k, v in sorted(by_type.items(), key=lambda x: -x[1]))
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    text = (
        f"📊 <b>گزارش {period} بار هوایی آبان تور</b>\n"
        f"📅 تاریخ: {today}\n"
        f"📦 تعداد کل سفارشات: <b>{total}</b>\n"
        f"⚖️ مجموع وزن: <b>{total_weight:.0f} کیلوگرم</b>\n"
        f"📈 تفکیک بر اساس نوع بار:\n{lines}\n"
        f"🔗 پنل مدیریت: {SITE}/admin"
    )
    markup = {"inline_keyboard": [[{"text": "📋 مشاهده پنل مدیریت", "url": f"{SITE}/admin"}]]}
    return text, markup

def send_to_channel(text, markup=None, parse_mode="HTML"):
    payload = {"chat_id": CARGO_CHANNEL, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if markup:
        payload["reply_markup"] = json.dumps(markup)
    return _post(payload)

def send_to_admin(text, markup=None, parse_mode="HTML"):
    payload = {"chat_id": ADMIN_CHAT, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if markup:
        payload["reply_markup"] = json.dumps(markup)
    return _post(payload)

def notify_new_order(o, source="وب‌سایت"):
    """Dual notify (channel + admin) for a new order."""
    text, markup = build_order_message(o, source)
    # Channel gets the rich message with inline buttons
    send_to_channel(text, markup)
    # Admin gets same (no need to duplicate buttons but fine)
    send_to_admin(text, markup)

def notify_status_change(o):
    """Status-change message to channel + admin."""
    text, markup = build_status_message(o)
    send_to_channel(text, markup)
    send_to_admin(text, markup)

def _send_async(fn, *a, **k):
    """Run a notify function in background thread (non-blocking)."""
    threading.Thread(target=lambda: fn(*a, **k), daemon=True).start()

if __name__ == "__main__":
    # quick self-test
    sample = {"tracking": "ABN-202608-TEST01", "name": "تست سیستم", "phone": "09120000000",
              "email": "test@abantour.ir", "origin": "تهران", "destination": "دبی",
              "cargo_type": "تجاری", "weight": "50", "dims": "60×40×30", "incoterm": "FOB",
              "service": "درب‌به‌درب", "desc": "تست اعلان", "status": "ثبت شده",
              "created_at": "2026-08-02 01:00"}
    print("order msg ok:", bool(build_order_message(sample)[0]))
    print("status msg ok:", bool(build_status_message(sample)[0]))
    print("summary ok:", bool(build_summary([sample])[0]))
