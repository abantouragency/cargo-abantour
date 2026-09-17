# -*- coding: utf-8 -*-
"""
Aban Tour Cargo - Telegram Notify Watcher (live-site polling)
Runs locally (Windows) on a cron. Polls the LIVE cargo site /admin page for new
orders and sends a Telegram alert to the admin if a new tracking code appears.
This is a backup path so admin always gets notified even if the Render app's
own notify is not configured.
"""
import os, re, html
import urllib.request, urllib.parse

BOT_TOKEN = os.environ.get("TG_TOKEN", "521451545:AAGcZvTXr3UHAuOIbij7wmuJ8dR-bpds5jI")
ADMIN_CHAT = os.environ.get("TG_CHAT", "67391189")
SITE = os.environ.get("CARGO_SITE", "https://cargo-abantour.onrender.com")
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".notify_state")
PROXY = os.environ.get("TG_PROXY") or os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")

def load_seen():
    try:
        return set(line.strip() for line in open(STATE_FILE, encoding="utf-8") if line.strip())
    except Exception:
        return set()

def save_seen(s):
    try:
        open(STATE_FILE, "w", encoding="utf-8").write("\n".join(sorted(s)))
    except Exception:
        pass

def fetch_admin():
    url = SITE + "/admin"
    req = urllib.request.Request(url, headers={"User-Agent": "cargo-watcher"})
    if PROXY:
        # simple: rely on environment proxy for urllib; if set, pass through
        proxy_handler = urllib.request.ProxyHandler({"https": PROXY, "http": PROXY})
        opener = urllib.request.build_opener(proxy_handler)
        return opener.open(req, timeout=20).read().decode("utf-8", "replace")
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": ADMIN_CHAT, "text": text, "parse_mode": "HTML"}
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                 headers={"User-Agent": "cargo-watcher"})
    if PROXY:
        proxy_handler = urllib.request.ProxyHandler({"https": PROXY, "http": PROXY})
        opener = urllib.request.build_opener(proxy_handler)
        return opener.open(req, timeout=10).read().decode()
    return urllib.request.urlopen(req, timeout=10).read().decode()

def main():
    try:
        page = fetch_admin()
    except Exception as e:
        print("fetch err:", e)
        return
    # Extract tracking codes
    codes = re.findall(r"ABN-\d{6}-[A-F0-9]{6}", page)
    codes = list(dict.fromkeys(codes))  # unique, preserve order
    if not codes:
        print("no orders found")
        return
    seen = load_seen()
    new = [c for c in codes if c not in seen]
    if not new:
        print("no new orders (seen %d)" % len(seen))
        # still update state to keep it current
        save_seen(set(codes))
        return
    for tr in new:
        # Pull details via track page
        try:
            tp = urllib.request.urlopen(SITE + "/track/" + tr, timeout=15).read().decode("utf-8", "replace")
            name = re.search(r"<td>نام</td><td>(.*?)</td>", tp)
            name = html.unescape(name.group(1)) if name else "?"
            route = re.search(r"<td>مبدأ → مقصد</td><td>(.*?)</td>", tp)
            route = html.unescape(route.group(1)) if route else "?"
            ctype = re.search(r"<td>نوع بار</td><td>(.*?)</td>", tp)
            ctype = html.unescape(ctype.group(1)) if ctype else "?"
            weight = re.search(r"<td>وزن</td><td>(.*?)</td>", tp)
            weight = html.unescape(weight.group(1)) if weight else "?"
            text = (f"📦 <b>سفارش بار جدید (هشدار نگهبان)</b>\n"
                    f"رهگیری: <code>{tr}</code>\n"
                    f"نام: {name}\nمسیر: {route}\n"
                    f"نوع: {ctype} | وزن: {weight}")
        except Exception:
            text = f"📦 <b>سفارش بار جدید</b>\nرهگیری: <code>{tr}</code>"
        send_telegram(text)
        print("notified", tr)
    save_seen(set(codes))
    print("done, new=%d total=%d" % (len(new), len(codes)))

if __name__ == "__main__":
    main()
