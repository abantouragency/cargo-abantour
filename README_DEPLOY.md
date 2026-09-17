# راهنمای دیپلوی سامانه بار هوایی آبان تور روی Render (رایگان)

## قدم ۱: ساخت ریپو توی GitHub
۱. برید https://github.com و وارد شوید (یا ثبت‌نام کنید — رایگان).
۲. بالا-راست روی علامت **+** → **New repository** بزنید.
۳. اسم ریپو: `cargo-abantour` (یا هر چی دوست دارید).
۴. **Public** بزنید (رایگانه).
۵. تیک **Add a README file** رو بردارید (ما خودمون داریم).
۶. دکمه **Create repository** رو بزنید.

## قدم ۲: آپلود فایل‌ها
توی صفحه ریپو، دکمه **Add file → Upload files** رو بزنید.
فایل‌های زیر رو (که توی پوشه cargo_system هستن) یکی‌یکی یا دسته‌جمعی آپلود کنید:
- `app.py`
- `Procfile`
- `requirements.txt`
- `runtime.txt`
- `README.md`
- پوشه `templates/` (با ۳ تا فایل: landing.html, track.html, admin.html)
دکمه **Commit changes** رو بزنید.

## قدم ۳: دیپلوی روی Render
۱. برید https://render.com و با حساب GitHub ثبت‌نام/ورود کنید (رایگان).
۲. دکمه **New + → Web Service** رو بزنید.
۳. ریپو `cargo-abantour` رو انتخاب کنید → **Connect**.
۴. تنظیمات:
   - Name: `cargo-abantour`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
   - Plan: **Free**
۵. دکمه **Create Web Service** رو بزنید.
۶. صبر کنید (۲-۵ دقیقه) تا Build و Deploy تموم بشه.
۷. Render یه آدرس می‌ده مثل: `https://cargo-abantour.onrender.com`

## قدم ۴: لینک در سایت اصلی
توی پنل abantour.ir → «افزودن منو»، لینک رو بذارید:
`https://cargo-abantour.onrender.com`

## قدم ۵: تنظیم اعلان تلگرام (اختیاری)
توی Render → Environment → متغیرهای محیطی اضافه کنید:
- `TG_TOKEN` = توکن ربات @Abantourbot
- `TG_CHAT` = ۶۷۳۹۱۱۸۹
(بدون این، سامانه کار می‌کنه ولی اعلان تلگرام نمی‌فرسته)

## تست:
- مرورگر باز کنید: آدرس Render
- فرم رو پر کنید → باید کد رهگیری بگیرید.
- بخش پیگیری رو چک کنید.
- `/admin` رو بزنید (پنل مدیریت).
