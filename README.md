<div align="center">

<img src="gereh.jpg" alt="GerehGosha Logo" width="130" height="130" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">

# 🧅 گره‌گشا · GerehGosha

**سامانه هوشمند مدیریت ترافیک، مسیریابی پیازی چندکشوره و تزریق مستقیم به پاسارگارد**

توسعه‌یافته توسط [امیر مرندی](https://github.com/amirmarandidev)

[![Version](https://img.shields.io/badge/version-2.5.0-10b981?style=flat-square)](#)
[![Telegram](https://img.shields.io/badge/telegram-@amirmarandidev-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/amirmarandidev)
[![License](https://img.shields.io/badge/license-open%20source-6b7280?style=flat-square)](#)

</div>

---

### 💖 حمایت از پروژه
این ابزار کاملاً رایگان و متن‌باز است. اگر برایتان سودمند بوده، با زدن ⭐ در گیت‌هاب یا حمایت رمزارزی به ادامه‌ی این مسیر انرژی دهید:

* 🔹 **USDT (BEP20):** `0xd593ae9D32bEA690EC62460C54BF3951aFFF7803`
* 🔸 **USDT (TRC20):** `THaaHzoTwXfUfcrtYTDXRsMmk9qhnXa56M`

---

### ⚠️ نکته حیاتی درباره انتخاب سرور (قبل از راه‌اندازی بخونید!)

برای اینکه از **گره‌گشا** نهایت سرعت و پایداری رو بگیرید و درگیر کندی یا تایم‌اوت نشید، توجه به محل میزبانی سرور بسیار کلیدیه:

* ❌ **سرورهایی با عملکرد ضعیف و ریت‌لیمیت بالا:**  
  سرورهای شرکت **هتزنر (Hetzner)** و دیتاسنترهایی مثل **OVH** و **DigitalOcean** به خاطر محدودیت‌ها و پالیسی‌های انضباطی روی پکت‌های شبکه پیازی، کیفیت ثابتی ندارند و باعث قطعی‌های مکرر یا تایم‌اوت می‌شوند.

* ✅ **سرورها و پلتفرم‌های تست‌شده و عالی:**  
  این پروژه روی سرورهای ابری **Railway** و **Play2Go** (و همین‌طور **Fly.io**، **Vultr** و **Linode / Akamai**) بارها تست شده و عملکردی فوق‌العاده نرم، پایدار و پرسرعت ارائه می‌دهد.

> 💬 **یه کلام رفاقتی:**  
> این پروژه قراره روزبه‌روز خفن‌تر بشه! مدام در حال بازنویسی، بهینه‌سازی مصرف رم و ارتقای متدهای ارتباطی هستم تا بالاترین پایداری ممکن رو تجربه کنید. خیالتون از آپدیت‌ها تخت باشه، فقط سرور رو هوشمندانه انتخاب کنید.

---

### ✨ قابلیت‌های کلیدی

* 🌐 **اسکن زنده و کشف خودکار:** پیدا کردن رله‌های سالم و پرسرعت بین‌المللی با بررسی لتنسی لحظه‌ای.
* ⚡ **خروجی همزمان چند کشوره (Multi-Exit):** اجرای پایدار لوکیشن‌های منتخب (آمریکا، آلمان، هلند و ...) روی پورت‌های مجزا و ایزوله.
* 💉 **تزریق مستقیم به پاسارگارد:** ساخت خودکار Inbound و Host متناظر با هر کشور در پنل PasarGuard فقط با یک کلیک.
* 🔄 **دریافت آی‌پی جدید (New IP):** تشخیص افت کیفیت مسیر و تغییر بلافاصله‌ی آی‌پی خروجی با یک کلیک.
* 🛡️ **داشبورد متمرکز و امن:** پنل وب سبک، واکنش‌گرا و سریع مجهز به احراز هویت دیتابیسی و مدیریت ادمین‌ها.
* 💻 **کنسول ترمینال اختصاصی (CLI):** دستور سیستمی `gerehgosha` برای مدیریت آسان سرور، عیب‌یابی و لاگ زنده.
* 🚀 **آپدیت هوشمند بدون قطعی دیتا:** دستور `gerehgosha update` برای دریافت کدهای تازه بدون از دست رفتن ادمین‌ها یا تنظیمات.

---

### 🚀 نصب و راه‌اندازی سریع

#### ۱. سرور لینوکس (پیشنهادی)
کافیست دستورات زیر را با دسترسی روت اجرا کنید:
```bash
git clone https://github.com/thekourox/gerehgosha.git
cd gerehgosha
sudo bash install.sh
```
> اسکریپت به صورت خودکار پیش‌نیازها را نصب، سرویس پس‌زمینه را تنظیم و اطلاعات ورود اولیه را تولید می‌کند.

#### ۲. محیط ویندوز (تست و توسعه)
فایل اجرایی زیر را باز کنید:
```cmd
run_windows.bat
```

---

### 🔑 پورت‌ها و درگاه‌های دسترسی

* 🌐 **داشبورد مدیریت اصلی:** `http://SERVER_IP:5000`
* ⚙️ **درگاه مستقیم انجین:** `http://SERVER_IP:54322`
* 🔌 **پورت‌های خروجی ساکس:** `9050+` (به ترتیب کشورهای انتخابی)
* 📁 **مسیر نصب روی سرور:** `/opt/gerehgosha`

> **مشاهده مشخصات ورود:** در هر زمان با اجرای دستور `gerehgosha` و انتخاب گزینه **Manage Admins**، مشخصات ورود قابل مشاهده و تغییر است.

---

### 💻 دستورات خط فرمان (CLI)

با اجرای دستور `gerehgosha` در ترمینال، منوی تعاملی باز می‌شود:

```text
=====================================
    GerehGosha (گره‌گشا) Manager     
   Developed by Amir (@amirmarandidev) 
=====================================
1. Install All Services (Tor Engine & Gateway)
2. Manage Admins (Add/View users)
3. View System Logs (Gateway)
4. Restart Gateway Service
5. Restart GerehGosha Engine (Tor)
6. Update GerehGosha (Git Pull & Seamless Upgrade)
7. Fetch Pasarguard Token
8. Uninstall GerehGosha
9. Exit
=====================================
```

#### دستورات تک‌خطی و مستقیم:
* 🔄 **آپدیت سریع:** `gerehgosha update`
* 🔑 **نمایش ادمین‌ها:** `python3 gerehgosha-cli.py --show-credentials`
* 🩺 **بررسی سلامت سیستم:** `python3 gerehgosha-cli.py --status`
* 🧹 **پاکسازی کش:** `python3 gerehgosha-cli.py --flush-cache`

---

### ❓ سوالات متداول

* ❓ **رمز عبور پنل را فراموش کرده‌ام:**  
  دستور `python3 /opt/gerehgosha/gerehgosha-cli.py --show-credentials` را در سرور بزنید تا مشخصات را ببینید.
* ❓ **آیا تنظیمات با آپدیت پاک می‌شوند؟**  
  خیر؛ با اجرای `gerehgosha update`، نسخه جدید بدون دست‌خوردن فایل دیتابیس یا تنظیمات جایگزین می‌شود.
* ❓ **دیدن زنده لاگ‌های سرویس:**  
  دستور `journalctl -u gerehgosha.service -f` را در ترمینال اجرا کنید.

---

### 📢 ارتباط و پشتیبانی

* ✈️ **تلگرام:** [@amirmarandidev](https://t.me/amirmarandidev)
* 🐙 **گیت‌هاب:** [amirmarandidev](https://github.com/amirmarandidev)
* 💼 **لینکدین:** [amirmarandi](https://linkedin.com/in/amirmarandi)
* 📧 **ایمیل:** [amirmarandidev@gmail.com](mailto:amirmarandidev@gmail.com)

<div align="center">

🌟 **اگر این پروژه برایتان کاربردی بود، با دادن یک ستاره در گیت‌هاب از ما حمایت کنید.**

</div>
