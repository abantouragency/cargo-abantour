# راهنمای راه‌اندازی سامانه بار هوایی آبان تور (cargo.abantour.ir)

## ۱. تنظیم DNS در ArvanCloud
۱. وارد پنل ArvanCloud شوید → بخش «DNS» → دومین abantour.ir
۲. رکورد جدید از نوع **A** اضافه کنید:
   - Name (نام): `cargo`
   - Type: `A`
   - Value (مقدار): آدرس IP سروری که سامانه روش هست (یا IP ArvanCloud PaaS)
   - TTL: پیش‌فرض
۳. اگر از CDN آروان استفاده می‌کنید، گزینه «پروکسی/Proxy» را روشن کنید.
۴. صبر کنید تا DNS منتشر شود (چند دقیقه تا ۲ ساعت).

## ۲. دیپلوی روی سرور (لینوکس/VPS)
```bash
# روی سرور:
git clone <repo> یا آپلود پوشه cargo_system
cd cargo_system
pip install -r requirements.txt
# اجرای پایدار با gunicorn یا systemd
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## ۳. اعلان تلگرام
در فایل `app.py` مقادیر را تنظیم کنید:
- `BOT_TOKEN`: توکن ربات @Abantourbot
- `TG_CHAT`: آیدی تلگرام شما (67391189)
یا از متغیرهای محیطی:
```bash
export TG_TOKEN="...."
export TG_CHAT="67391189"
```

## ۴. لینک در سایت اصلی
توی پنل abantour.ir → افزودن منو، لینک را بذارید:
`https://cargo.abantour.ir`

## ۵. تست محلی
```bash
python app.py
# مرورگر: http://127.0.0.1:5000
```
