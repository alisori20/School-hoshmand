# 🚀 راهنمای استقرار و راه‌اندازی سامانه چندمدرسه‌ای (v6) روی سرور لینوکس

این راهنما گام‌به‌گام نحوه داکرایز کردن و استقرار سامانه هوشمند مدیریت مدرسه نسخه ۶ به همراه دیتابیس PostgreSQL و کلاس آنلاین/هوش مصنوعی را توضیح می‌دهد.

---

## 📁 ساختار پوشه پروژه روی سرور
پوشه پروژه شما بر روی سرور لینوکس (VPS) باید حاوی ساختار زیر باشد:
```text
/my-school-project/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app-v6.py
└── schema-v6.sql
```

---

## 🛠️ مراحل استقرار (Deployment)

### گام اول: نصب داکر و داکر کامپوز روی سرور لینوکس
ترمینال سرور (از طریق SSH) را باز کرده و دستورات زیر را برای نصب داکر اجرا کنید:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable --now docker
```

### گام دوم: انتقال فایل‌ها به سرور
تمام فایل‌های ذکر شده در ساختار بالا (فایل‌های دانلود شده از استودیو و داکر) را به پوشه پروژه خود در سرور (مثلاً `/var/www/smart_school/`) انتقال دهید.

### گام سوم: ویرایش کدهای امنیتی و دیتابیس
در صورت نیاز، رمز عبور پیش‌فرض دیتابیس (`SuperSecurePassword2026!`) را در فایل `docker-compose.yml` به یک رمز عبور فوق‌العاده قوی تغییر دهید.

### گام چهارم: اجرای پروژه با داکر کامپوز
دستور زیر را در پوشه پروژه خود در سرور لینوکس اجرا کنید تا دیتابیس دانلود شده، ایمیج پایتون ساخته شود و وب‌سایت فعال گردد:
```bash
sudo docker-compose up --build -d
```
*این دستور در پس‌زمینه (Daemon mode) اجرا می‌شود و در صورتی که سرور ری‌استارت شود، کانتینرها به صورت خودکار مجدداً بالا می‌آیند.*

### گام پنجم: بررسی وضعیت اجرای پروژه
برای اطمینان از صحت کارکرد کانتینرها، دستور زیر را بزنید:
```bash
sudo docker-compose ps
```
برنامه شما اکنون بر روی پورت `8501` سرور فعال و آماده به کار است.

---

## 🛡️ ایمن‌سازی نهایی و اتصال به دامنه (HTTPS / Nginx)

جهت محافظت از داده‌های تحصیلی و جلوگیری از نشت اطلاعات حساس دانش‌آموزان در بستر اینترنت، باید حتماً وب‌سرور معکوس (Reverse Proxy) و گواهی امنیتی SSL را بر روی سرور راه‌اندازی کنید.

### کانفیگ نمونه Nginx به همراه HTTPS
۱. وب‌سرور Nginx را روی سیستم‌عامل سرور نصب کنید:
```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

۲. یک فایل کانفیگ برای دامنه خود ایجاد کنید (`/etc/nginx/sites-available/school.conf`):
```nginx
server {
    listen 80;
    server_name yourdomain.com; # دامنه اختصاصی خود را وارد کنید

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

۳. فایل کانفیگ را فعال کرده و Nginx را تست و ری‌استارت کنید:
```bash
sudo ln -s /etc/nginx/sites-available/school.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

۴. گواهی امنیتی رایگان SSL (پروتکل HTTPS) را بر روی دامنه خود فعال کنید:
```bash
sudo certbot --nginx -d yourdomain.com
```

**اکنون پورتال مدرسه هوشمند شما از طریق پروتکل فوق‌العاده امن HTTPS و با آدرس دامنه شما بدون نیاز به زدن پورت فعال و در دسترس عموم قرار گرفته است! 🌟**
