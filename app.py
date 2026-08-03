# -*- coding: utf-8 -*-
"""
Aban Tour - Air Cargo Management System (cargo.abantour.ir / Render)
SINGLE-FILE Flask app: landing + order submit + tracking + admin.
DB: SQLite (orders.db). No external deps beyond Flask + stdlib.
Templates are embedded as strings so no templates/ folder is needed.
"""
import os, sqlite3, json, secrets, datetime, threading
from flask import Flask, request, redirect, url_for, jsonify

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "orders.db")

# ---- Telegram notify (shared module) ----
import os as _os
BOT_TOKEN = _os.environ.get("TG_TOKEN", "521451545:AAGcZvTXr3UHAuOIbij7wmuJ8dR-bpds5jI")
TG_CHAT = _os.environ.get("TG_CHAT", "67391189")
# import shared notifier
import cargo_notify as _cn
_cn.BOT_TOKEN = BOT_TOKEN
_cn.ADMIN_CHAT = TG_CHAT

def init_db():
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking TEXT UNIQUE, name TEXT, phone TEXT, email TEXT,
        origin TEXT, destination TEXT, cargo_type TEXT, weight REAL, dims TEXT,
        incoterm TEXT, service TEXT, desc TEXT, status TEXT DEFAULT 'ثبت شده',
        created_at TEXT, updated_at TEXT)''')
    conn.commit(); conn.close()

init_db()

def new_tracking():
    return "ABN-" + datetime.datetime.now().strftime("%Y%m") + "-" + secrets.token_hex(3).upper()

# ===== Embedded templates =====
LANDING = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>خدمات بار هوایی (فریت کارگو) | آژانس هواپیمایی آبان تور</title>
<meta name="description" content="ارسال ایمن و سریع بار تجاری و شخصی به سراسر جهان با آژانس هواپیمایی آبان تور. ثبت آنلاین سفارش و پیگیری لحظه‌ای.">
<meta name="keywords" content="فریت کارگو, بار هوایی, ارسال بار, Freight, Air Cargo, بار تجاری, بار شخصی, ترخیص گمرکی, حمل بار بین‌الملل, آبان تور, کارگو تهران, بار به خارج, بار از خارج">
<meta name="author" content="آژانس هواپیمایی آبان تور">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://cargo-abantour.onrender.com/">
<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:locale" content="fa_IR">
<meta property="og:site_name" content="فریت کارگو آبان تور">
<meta property="og:title" content="فریت کارگو | خدمات بار هوایی آبان تور — ارسال بار به سراسر جهان">
<meta property="og:description" content="ارسال ایمن و سریع بار تجاری و شخصی به سراسر جهان با آبان تور. استعلام رایگان، بسته‌بندی استاندارد، ترخیص گمرکی و پیگیری لحظه‌ای.">
<meta property="og:url" content="https://cargo-abantour.onrender.com/">
<meta property="og:image" content="https://abantour.ir/favicon.ico">
<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="فریت کارگو | خدمات بار هوایی آبان تور">
<meta name="twitter:description" content="ارسال ایمن و سریع بار تجاری و شخصی به سراسر جهان با پشتیبانی ۲۴ ساعته آبان تور.">
<meta name="twitter:image" content="https://abantour.ir/favicon.ico">
<!-- JSON-LD -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MovingCompany",
  "name": "فریت کارگو آبان تور",
  "alternateName": "آژانس هواپیمایی آبان تور - بخش بار هوایی",
  "url": "https://cargo-abantour.onrender.com/",
  "image": "https://abantour.ir/favicon.ico",
  "description": "خدمات حرفه‌ای فریت کارگو و بار هوایی شامل بار تجاری، بار شخصی، ترانزیت بین‌الملل، بار حساس و ترخیص گمرکی.",
  "telephone": "+982155009429",
  "email": "abantour.agency@gmail.com",
  "address": {"@type": "PostalAddress", "streetAddress": "خیابان شهید رجایی، پلاک ۳۲۰", "addressLocality": "تهران", "addressCountry": "IR"},
  "areaServed": "Worldwide",
  "parentOrganization": {"@type": "TravelAgency", "name": "آژانس هواپیمایی آبان تور", "url": "https://abantour.ir"},
  "sameAs": ["https://t.me/abantour_agency", "https://www.instagram.com/abantour_agency", "https://www.aparat.com/abantour"]
}
</script>
<style>
  @font-face{font-family:'Vazirmatn';font-weight:400;src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Regular.woff2') format('woff2');font-display:swap;}
  @font-face{font-family:'Vazirmatn';font-weight:700;src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-Bold.woff2') format('woff2');font-display:swap;}
  *{box-sizing:border-box;}
  body{margin:0;font-family:Vazirmatn,'Segoe UI',Tahoma,sans-serif;background:#eef2f7;color:#1d2733;line-height:2;}
  .site-header{background:linear-gradient(135deg,#0b1e3a,#16325c);padding:18px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;border-bottom:3px solid #c9a227;}
  .site-header .brand{color:#fff;font-size:22px;font-weight:800;}
  .site-header .brand span{color:#c9a227;}
  .site-header .back{color:#c9a227;text-decoration:none;font-weight:700;font-size:14px;border:1px solid #c9a227;padding:8px 16px;border-radius:8px;}
  .site-header .back:hover{background:#c9a227;color:#0b1e3a;}
  .wrap{max-width:1040px;margin:0 auto;padding:24px;}
  .hero{background:linear-gradient(135deg,#0b1e3a,#16325c);border-radius:18px;padding:48px 30px;text-align:center;margin-bottom:28px;border:1px solid #c9a227;position:relative;overflow:hidden;}
  .hero::after{content:"✈️";position:absolute;left:-10px;top:-10px;font-size:120px;opacity:.06;transform:rotate(-20deg);}
  .hero .ico{font-size:48px;line-height:1;margin-bottom:10px;}
  .hero h1{color:#fff;font-size:30px;margin:0 0 12px;}
  .hero p{color:#cbd6e6;font-size:16px;max-width:680px;margin:0 auto 24px;}
  .btn{display:inline-block;background:#c9a227;color:#0b1e3a;font-weight:700;padding:14px 30px;border-radius:10px;text-decoration:none;font-size:16px;margin:6px;transition:.2s;}
  .btn:hover{background:#e0b73a;transform:translateY(-2px);}
  .btn.ghost{background:transparent;color:#c9a227;border:1px solid #c9a227;}
  .section{background:#fff;border-radius:16px;padding:30px;margin-bottom:24px;box-shadow:0 4px 18px rgba(11,30,58,.06);}
  .section h2{color:#0b1e3a;font-size:22px;margin:0 0 18px;border-right:4px solid #c9a227;padding-right:12px;}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;}
  .card{background:#f7f9fc;border:1px solid #e3e9f2;border-radius:12px;padding:20px;transition:.2s;}
  .card:hover{box-shadow:0 6px 20px rgba(11,30,58,.1);transform:translateY(-3px);}
  .card .ic{font-size:30px;}
  .card h3{color:#0b1e3a;font-size:17px;margin:10px 0 6px;}
  .card p{color:#5a6a7e;font-size:14px;margin:0;}
  .steps{counter-reset:s;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;}
  .step{background:#f7f9fc;border-radius:12px;padding:20px;text-align:center;position:relative;}
  .step::before{counter-increment:s;content:counter(s);display:block;width:38px;height:38px;line-height:38px;background:#0b1e3a;color:#c9a227;border-radius:50%;margin:0 auto 10px;font-weight:800;}
  .step h4{color:#0b1e3a;margin:0 0 6px;font-size:15px;}
  .step p{color:#5a6a7e;font-size:13px;margin:0;}
  form label{display:block;font-weight:700;color:#0b1e3a;margin:14px 0 6px;font-size:14px;}
  form input,form select,form textarea{width:100%;padding:12px 14px;border:1px solid #d4dce8;border-radius:10px;font-family:inherit;font-size:14px;background:#fbfcfe;}
  form input:focus,form select:focus,form textarea:focus{outline:none;border-color:#c9a227;background:#fff;}
  .row{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
  .success-box{display:none;background:#e8f5e9;border:1px solid #a5d6a7;color:#1b5e20;border-radius:12px;padding:20px;margin-top:20px;text-align:center;font-weight:700;}
  footer{background:#0b1e3a;color:#9fb2cd;padding:24px;text-align:center;font-size:13px;margin-top:30px;}
  footer a{color:#c9a227;text-decoration:none;}
  @media(max-width:600px){.row{grid-template-columns:1fr;}.hero h1{font-size:24px;}}
</style>
</head>
<body>
<header class="site-header">
  <div class="brand">آبان <span>تور</span></div>
  <a class="back" href="https://abantour.ir">← بازگشت به سایت اصلی</a>
</header>
<div class="wrap">
  <section class="hero">
    <div class="ico">📦✈️</div>
    <h1>خدمات بار هوایی (فریت کارگو)</h1>
    <p>ارسال ایمن و سریع بار تجاری و شخصی به سراسر جهان. استعلام رایگان، بسته‌بندی استاندارد، ترخیص و پیگیری تا لحظه تحویل — با پشتیبانی ۲۴ ساعته آبان تور.</p>
    <a class="btn" href="#order">ثبت آنلاین سفارش بار</a>
    <a class="btn ghost" href="#track">پیگیری بار</a>
  </section>
  <section class="section">
    <h2>خدمات ما</h2>
    <div class="grid">
      <div class="card"><div class="ic">🏢</div><h3>بار تجاری</h3><p>حمل محموله‌های تجاری، نمونه کالا و قطعات صنعتی با بهترین نرخ‌های شرکت‌های هواپیمایی.</p></div>
      <div class="card"><div class="ic">🧳</div><h3>بار شخصی</h3><p>ارسال وسایل شخصی، خورجین و هدایا به ایران و سایر کشورها با خیال آسوده.</p></div>
      <div class="card"><div class="ic">🚚</div><h3>درب‌به‌درب</h3><p>تحویل و دریافت بار از درب منزل/انبار تا وجه مقصد بدون دغدغه حمل.</p></div>
      <div class="card"><div class="ic">🌐</div><h3>ترانزیت بین‌الملل</h3><p>عبور و جابه‌جایی بار از مسیرهای ترانزیتی جهانی با هماهنگی کامل.</p></div>
      <div class="card"><div class="ic">🔬</div><h3>بار حساس</h3><p>حمل کالاهای خطرناک (DG)، دارو و تجهیزات حساس طبق استانداردهای IATA.</p></div>
      <div class="card"><div class="ic">📑</div><h3>ترخیص گمرکی</h3><p>انجام تشریفات گمرکی و بارنامه (AWB) با تیم مجرب ترخیص کالا.</p></div>
    </div>
  </section>
  <section class="section">
    <h2>چرا آبان تور؟</h2>
    <div class="grid">
      <div class="card"><div class="ic">⭐</div><h3>تجربه چندساله</h3><p>سابقه درخشان در صدور بلیط و خدمات مسافرتی با اعتبار ثبت‌شده.</p></div>
      <div class="card"><div class="ic">🤝</div><h3>همکاری با ایرلاین‌های معتبر</h3><p>قرارداد با شرکت‌های هواپیمایی داخلی و بین‌المللی.</p></div>
      <div class="card"><div class="ic">💰</div><h3>نرخ رقابتی</h3><p>استعلام رایگان و سریع قبل از هرگونه پرداخت.</p></div>
      <div class="card"><div class="ic">📞</div><h3>پشتیبانی ۲۴ ساعته</h3><p>پاسخگویی تلفنی و تلگرامی در تمام ایام.</p></div>
    </div>
  </section>
  <section class="section">
    <h2>فرآیند ارسال بار</h2>
    <div class="steps">
      <div class="step"><h4>استعلام نرخ</h4><p>ثبت درخواست و دریافت قیمت آنلاین</p></div>
      <div class="step"><h4>بسته‌بندی</h4><p>بسته‌بندی استاندارد و ایمن‌سازی</p></div>
      <div class="step"><h4>حمل به فرودگاه</h4><p>تحویل درب‌به‌درب یا تحویل در دفتر</p></div>
      <div class="step"><h4>بارنامه AWB</h4><p>صدور بارنامه و کد رهگیری</p></div>
      <div class="step"><h4>پیگیری</h4><p>ردیابی لحظه‌ای تا مقصد</p></div>
    </div>
  </section>
  <section class="section" id="order">
    <h2>ثبت آنلاین سفارش بار</h2>
    <form id="orderForm">
      <div class="row">
        <div><label>نام و نام خانوادگی *</label><input name="name" required></div>
        <div><label>شماره تماس *</label><input name="phone" required dir="ltr"></div>
      </div>
      <div class="row">
        <div><label>ایمیل</label><input name="email" dir="ltr"></div>
        <div><label>نوع سرویس</label>
          <select name="service">
            <option value="درب‌به‌درب">درب‌به‌درب</option>
            <option value="تحویل در دفتر">تحویل در دفتر</option>
            <option value="ترانزیت">ترانزیت بین‌الملل</option>
          </select>
        </div>
      </div>
      <div class="row">
        <div><label>مبدأ (شهر/کشور) *</label><input name="origin" required></div>
        <div><label>مقصد (شهر/کشور) *</label><input name="destination" required></div>
      </div>
      <div class="row">
        <div><label>نوع بار *</label>
          <select name="cargo_type">
            <option>تجاری</option><option>شخصی</option><option>مواد غذایی</option>
            <option>دارو</option><option>قطعات صنعتی</option><option>مدارک</option><option>سایر</option>
          </select>
        </div>
        <div><label>وزن تقریبی (کیلوگرم)</label><input name="weight" type="number" min="0" dir="ltr"></div>
      </div>
      <div class="row">
        <div><label>ابعاد (طول×عرض×ارتفاع سانتی‌متر)</label><input name="dims" dir="ltr" placeholder="مثلاً 50×40×30"></div>
        <div><label>شرایط حمل (Incoterm)</label>
          <select name="incoterm">
            <option>EXW</option><option>FOB</option><option>CIF</option><option>DAP</option><option>DDP</option>
          </select>
        </div>
      </div>
      <label>توضیحات تکمیلی</label>
      <textarea name="desc" rows="3" placeholder="جزئیات بار، زمان‌بندی مورد نظر و..."></textarea>
      <button class="btn" type="submit" style="margin-top:18px;">ثبت سفارش و دریافت کد رهگیری</button>
    </form>
    <div class="success-box" id="okBox"></div>
  </section>
  <section class="section" id="track">
    <h2>پیگیری بار</h2>
    <form onsubmit="event.preventDefault();location.href='/track/'+document.getElementById('tcode').value">
      <label>شماره رهگیری خود را وارد کنید</label>
      <div class="row">
        <div><input id="tcode" dir="ltr" placeholder="ABN-202607-XXXXXX" style="text-transform:uppercase;"></div>
        <div><button class="btn" type="submit">پیگیری</button></div>
      </div>
    </form>
  </section>
  <section class="section">
    <h2>تماس با ما</h2>
    <p>📞 تلفن: <a href="tel:02155009429" style="color:#0b1e3a;">۰۲۱۵۵۰۰۹۴۲۹</a> &nbsp;|&nbsp; 📱 موبایل: ۰۹۳۶۲۰۱۸۱۷۸</p>
    <p>✈️ تلگرام: <a href="https://t.me/Abantourbot" style="color:#0b1e3a;">@Abantourbot</a> &nbsp;|&nbsp; 🌐 سایت: <a href="https://abantour.ir" style="color:#0b1e3a;">abantour.ir</a></p>
  </section>
</div>
<footer>
  کلیه حقوق محفوظ است &copy; آژانس هواپیمایی آبان تور | سامانه بار هوایی (فریت کارگو)<br>
  پشتیبانی ۲۴ ساعته: ۰۲۱۵۵۰۰۹۴۲۹
</footer>
<script>
document.getElementById('orderForm').addEventListener('submit', async function(e){
  e.preventDefault();
  const fd = new FormData(this);
  const btn = this.querySelector('button');
  btn.disabled = true; btn.textContent = 'در حال ارسال...';
  try {
    const r = await fetch('/submit', {method:'POST', body: fd});
    const j = await r.json();
    if (j.ok) {
      const box = document.getElementById('okBox');
      box.style.display = 'block';
      box.innerHTML = '✅ سفارش شما با موفقیت ثبت شد!<br>شماره رهگیری شما: <b style="font-size:20px;color:#0b1e3a;">'+j.tracking+'</b><br><br><a class="btn" href="/track/'+j.tracking+'">پیگیری بار</a>';
      this.reset();
    }
  } catch(err) {
    alert('خطا در ارسال. لطفاً تماس بگیرید.');
  } finally {
    btn.disabled = false; btn.textContent = 'ثبت سفارش و دریافت کد رهگیری';
  }
});
</script>
</body>
</html>'''

TRACK = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>پیگیری بار | آبان تور</title>
<style>
  *{box-sizing:border-box;}
  body{margin:0;font-family:Vazirmatn,'Segoe UI',Tahoma,sans-serif;background:#eef2f7;color:#1d2733;line-height:2;padding:24px;}
  .wrap{max-width:640px;margin:40px auto;background:#fff;border-radius:16px;padding:30px;box-shadow:0 4px 18px rgba(11,30,58,.08);}
  h1{color:#0b1e3a;text-align:center;font-size:24px;}
  .box{padding:16px;border-radius:12px;margin:16px 0;}
  .ok{background:#e8f5e9;border:1px solid #a5d6a7;color:#1b5e20;}
  .err{background:#fdecea;border:1px solid #ef9a9a;color:#b71c1c;}
  table{width:100%;border-collapse:collapse;margin-top:10px;}
  td{padding:10px;border-bottom:1px solid #eef2f7;font-size:14px;}
  td:first-child{color:#5a6a7e;width:40%;}
  .status{display:inline-block;background:#0b1e3a;color:#c9a227;padding:6px 16px;border-radius:20px;font-weight:700;}
  a.btn{display:inline-block;background:#c9a227;color:#0b1e3a;font-weight:700;padding:10px 20px;border-radius:8px;text-decoration:none;margin-top:10px;}
  input{width:100%;padding:12px;border:1px solid #d4dce8;border-radius:10px;font-family:inherit;font-size:15px;}
  .track-form{margin-top:20px;}
</style>
</head>
<body>
<div class="wrap">
  <h1>🔍 پیگیری بار هوایی</h1>
  {% if tracking %}
    {% if order %}
      <div class="box ok">
        <p style="text-align:center;font-size:18px;margin:0;">شماره رهگیری: <b>{{ order.tracking }}</b></p>
        <p style="text-align:center;"><span class="status">{{ order.status }}</span></p>
      </div>
      <table>
        <tr><td>نام</td><td>{{ order.name }}</td></tr>
        <tr><td>مبدأ → مقصد</td><td>{{ order.origin }} → {{ order.destination }}</td></tr>
        <tr><td>نوع بار</td><td>{{ order.cargo_type }}</td></tr>
        <tr><td>وزن</td><td>{{ order.weight }} کیلوگرم</td></tr>
        <tr><td>سرویس</td><td>{{ order.service }}</td></tr>
        <tr><td>ثبت شده در</td><td>{{ order.created_at }}</td></tr>
        <tr><td>آخرین به‌روزرسانی</td><td>{{ order.updated_at }}</td></tr>
        {% if order.desc %}<tr><td>توضیحات</td><td>{{ order.desc }}</td></tr>{% endif %}
      </table>
      <p style="text-align:center;color:#5a6a7e;font-size:13px;">برای اطلاعات بیشتر با ۰۲۱۵۵۰۰۹۴۲۹ تماس بگیرید.</p>
    {% else %}
      <div class="box err">❌ شماره رهگیری <b>{{ tracking }}</b> یافت نشد. لطفاً صحت کد را بررسی کنید.</div>
    {% endif %}
  {% else %}
    <p style="text-align:center;color:#5a6a7e;">شماره رهگیری خود را وارد کنید:</p>
  {% endif %}
  <form class="track-form" onsubmit="event.preventDefault();location.href='/track/'+document.getElementById('t').value">
    <input id="t" dir="ltr" placeholder="ABN-202607-XXXXXX" style="text-transform:uppercase;" value="{{ tracking or '' }}">
    <button class="btn" style="width:100%;margin-top:12px;border:none;cursor:pointer;" type="submit">پیگیری</button>
  </form>
  <p style="text-align:center;margin-top:20px;"><a href="/" style="color:#0b1e3a;">← بازگشت به صفحه اصلی</a></p>
</div>
</body>
</html>'''

ADMIN = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>پنل مدیریت بار | آبان تور</title>
<style>
  *{box-sizing:border-box;}
  body{margin:0;font-family:Vazirmatn,'Segoe UI',Tahoma,sans-serif;background:#eef2f7;color:#1d2733;line-height:1.8;padding:20px;}
  .wrap{max-width:1100px;margin:0 auto;}
  h1{color:#0b1e3a;font-size:22px;}
  .bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px;}
  .count{background:#0b1e3a;color:#c9a227;padding:8px 18px;border-radius:20px;font-weight:700;}
  table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 18px rgba(11,30,58,.06);font-size:13px;}
  th,td{padding:10px 12px;text-align:right;border-bottom:1px solid #eef2f7;}
  th{background:#0b1e3a;color:#c9a227;font-weight:700;}
  tr:hover{background:#f7f9fc;}
  .st{display:inline-block;padding:4px 12px;border-radius:14px;font-weight:700;font-size:12px;}
  select{padding:6px 10px;border-radius:8px;border:1px solid #d4dce8;font-family:inherit;}
  a{color:#0b1e3a;}
  .empty{text-align:center;color:#5a6a7e;padding:40px;}
</style>
</head>
<body>
<div class="wrap">
  <div class="bar">
    <h1>📋 پنل مدیریت سفارشات بار هوایی</h1>
    <span class="count">تعداد: {{ orders|length }}</span>
  </div>
  {% if orders %}
  <table>
    <tr><th>رهگیری</th><th>نام</th><th>تماس</th><th>مسیر</th><th>نوع</th><th>وزن</th><th>وضعیت</th><th>تغییر وضعیت</th></tr>
    {% for o in orders %}
    <tr>
      <td><b>{{ o.tracking }}</b><br><small style="color:#5a6a7e;">{{ o.created_at }}</small></td>
      <td>{{ o.name }}</td>
      <td dir="ltr">{{ o.phone }}</td>
      <td>{{ o.origin }} → {{ o.destination }}</td>
      <td>{{ o.cargo_type }}</td>
      <td>{{ o.weight }}kg</td>
      <td><span class="st" style="background:#e8f5e9;color:#1b5e20;">{{ o.status }}</span></td>
      <td>
        <form onsubmit="event.preventDefault();updateStatus({{ o.id }}, this.querySelector('select').value)">
          <select onchange="updateStatus({{ o.id }}, this.value)">
            <option {% if o.status=='ثبت شده' %}selected{% endif %}>ثبت شده</option>
            <option {% if o.status=='در حال بررسی' %}selected{% endif %}>در حال بررسی</option>
            <option {% if o.status=='بسته‌بندی' %}selected{% endif %}>بسته‌بندی</option>
            <option {% if o.status=='تحویل به ایرلاین' %}selected{% endif %}>تحویل به ایرلاین</option>
            <option {% if o.status=='در مسیر' %}selected{% endif %}>در مسیر</option>
            <option {% if o.status=='رسیده به مقصد' %}selected{% endif %}>رسیده به مقصد</option>
            <option {% if o.status=='تحویل داده شد' %}selected{% endif %}>تحویل داده شد</option>
          </select>
        </form>
      </td>
    </tr>
    {% endfor %}
  </table>
  {% else %}
  <div class="empty">هنوز سفارشی ثبت نشده است.</div>
  {% endif %}
</div>
<script>
async function updateStatus(id, status){
  await fetch('/admin/update/'+id, {method:'POST', body: new URLSearchParams({status:status})});
  location.reload();
}
</script>
</body>
</html>'''

from flask import render_template_string

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
    order = {
        "tracking": tracking, "name": f.get("name"), "phone": f.get("phone"),
        "email": f.get("email"), "origin": f.get("origin"), "destination": f.get("destination"),
        "cargo_type": f.get("cargo_type"), "weight": f.get("weight") or 0, "dims": f.get("dims"),
        "incoterm": f.get("incoterm"), "service": f.get("service"), "desc": f.get("desc"),
        "status": "ثبت شده", "created_at": now,
    }
    # Dual notify (channel + admin) via shared module
    import threading as _th
    _th.Thread(target=_cn.notify_new_order, args=(order, "وب‌سایت"), daemon=True).start()
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
    c.execute("SELECT tracking,name,origin,destination,cargo_type,weight FROM orders WHERE id=?", (oid,))
    row = c.fetchone()
    c.execute("UPDATE orders SET status=?, updated_at=? WHERE id=?", (status, now, oid))
    conn.commit(); conn.close()
    if row:
        order = {"tracking": row[0], "name": row[1], "origin": row[2], "destination": row[3],
                 "cargo_type": row[4], "weight": row[5], "status": status}
        import threading as _th
        _th.Thread(target=_cn.notify_status_change, args=(order,), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/admin/export")
def admin_export():
    """Export all orders as CSV (Excel-compatible, UTF-8 BOM)."""
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = c.fetchall(); conn.close()
    cols = ["id","tracking","name","phone","email","origin","destination","cargo_type",
            "weight","dims","incoterm","service","desc","status","created_at","updated_at","source"]
    import io, csv
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow(["" if v is None else v for v in r])
    data = "\ufeff" + buf.getvalue()  # BOM for Excel Persian
    return data, 200, {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": "attachment; filename=cargo_orders.csv"
    }

@app.route("/cron/summary")
def cron_summary():
    """Daily/weekly summary trigger. Protected by SUMMARY_KEY. Sends to channel+admin."""
    key = request.args.get("key", "")
    secret = os.environ.get("SUMMARY_KEY", "cargo-summary-secret")
    if key != secret:
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    period = request.args.get("period", "daily")
    days = 1 if period == "daily" else 7
    since = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB); c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE created_at >= ? ORDER BY id DESC", (since,))
    rows = c.fetchall(); conn.close()
    cols = ["id","tracking","name","phone","email","origin","destination","cargo_type",
            "weight","dims","incoterm","service","desc","status","created_at","updated_at","source"]
    orders = [dict(zip(cols, r)) for r in rows]
    label = "روزانه" if period == "daily" else "هفتگی"
    text, markup = _cn.build_summary(orders, label)
    _cn.send_to_channel(text, markup)
    _cn.send_to_admin(text, markup)
    return jsonify({"ok": True, "count": len(orders), "period": period})

if __name__ == "__main__":
    import os as _os2
    port = int(_os2.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
