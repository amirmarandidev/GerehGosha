# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Unified Security Gateway & Auth Proxy
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
#  Notice: Unauthorized redistribution, removal of copyright notices, or
#          reverse engineering of this software is strictly prohibited.
# ==============================================================================

__author__ = "Amir (@amirmarandidev)"
__copyright__ = "Copyright (c) 2024-2026 Amir. All rights reserved."
__project__ = "GerehGosha (گره‌گشا)"
__version__ = "2.0.0-PRO"

import os
import json
import sqlite3
import requests
from datetime import timedelta
from flask import Flask, request, session, redirect, url_for, render_template_string, Response, send_file
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
import ui_theme

# Disable default static folder so we can proxy /static/
app = Flask(__name__, static_folder=None)
app.secret_key = "super_secret_gateway_key_change_in_production"
app.permanent_session_lifetime = timedelta(days=365)

# Trust Nginx reverse proxy headers (X-Forwarded-Proto, X-Forwarded-Host, etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

DB_PATH = "auth.db"

# Ensure the DB exists and includes preferred_language
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT, preferred_language TEXT)")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cursor.fetchall()]
        if "preferred_language" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN preferred_language TEXT DEFAULT NULL")
        conn.commit()

init_db()

LANGUAGES = {
    "fa": {"name": "فارسی", "en_name": "Persian (Farsi)", "flag": "🇮🇷", "dir": "rtl", "code": "FA"},
    "en": {"name": "English", "en_name": "English", "flag": "🇬🇧", "dir": "ltr", "code": "EN"},
    "ru": {"name": "Русский", "en_name": "Russian", "flag": "🇷🇺", "dir": "ltr", "code": "RU"},
    "zh": {"name": "中文", "en_name": "Chinese", "flag": "🇨🇳", "dir": "ltr", "code": "ZH"},
}
ALLOWED_LANGUAGES = set(LANGUAGES.keys())

TRANSLATIONS = {
    "en": {
        "app_title": "GerehGosha",
        "app_subtitle": "گره‌گشا • Unified Gateway Access",
        "system_title": "System Control Gateway",
        "system_subtitle": "Direct access to your intelligent traffic routing network and microservices",
        "username": "Username",
        "password": "Password",
        "sign_in": "Sign In to Dashboard",
        "invalid_credentials": "Invalid username or password",
        "admin_badge": "Admin",
        "sign_out": "Sign Out",
        "core_title": "GerehGosha Engine (گره‌گشا)",
        "core_desc": "High-performance multi-node routing core, telemetry monitor, latency balancer, and Pasarguard synchronizer.",
        "core_meta": "INTERNAL PORT: 54322 • ROUTE: /tor/",
        "launch_core": "Launch GerehGosha Dashboard →",
        "status_online": "● ONLINE & ACTIVE",
        "secondary_title": "GerehGosha Secondary Carrier",
        "secondary_desc": "Secondary carrier protocol is kept in local isolation for future redesign. Excluded from active operations.",
        "secondary_meta": "INTERNAL PORT: 8088 • STATUS: OFFLINE",
        "service_standby": "Service In Standby",
        "status_standby": "ISOLATED / STANDBY",
        "footer_text": "GerehGosha (گره‌گشا) v2.0 • Designed & Developed by Amir (@amirmarandidev) • All rights reserved.",
        "setup_tag": "Initial Setup",
        "setup_title": "Select Preferred Language",
        "setup_subtitle": "Please select your preferred language to continue using GerehGosha.",
        "confirm_continue": "Confirm & Continue",
        "change_lang": "Language",
    },
    "fa": {
        "app_title": "گره‌گشا",
        "app_subtitle": "GerehGosha • درگاه یکپارچه شبکه و امنیت",
        "system_title": "درگاه کنترل و مدیریت سیستم",
        "system_subtitle": "دسترسی مستقیم به هسته مسیریابی هوشمند ترافیک و میکروسرویس‌های متصل",
        "username": "نام کاربری",
        "password": "رمز عبور",
        "sign_in": "ورود به پیشخوان مدیریت",
        "invalid_credentials": "نام کاربری یا رمز عبور اشتباه است",
        "admin_badge": "مدیر",
        "sign_out": "خروج از حساب",
        "core_title": "هسته گره‌گشا (گره‌گشا)",
        "core_desc": "هسته مسیریابی چندنود با کارایی بالا، پایش تله‌متری زنده، توازن تأخیر شبکه و همگام‌ساز پاسارگارد.",
        "core_meta": "پورت داخلی: ۵۴۳۲۲ • مسیر: /tor/",
        "launch_core": "ورود به داشبورد گره‌گشا ←",
        "status_online": "● آنلاین و فعال",
        "secondary_title": "سرویس ثانویه گره‌گشا",
        "secondary_desc": "پروتکل حامل ثانویه در محیط ایزوله نگهداری می‌شود و از چرخه عملیاتی فعال خارج است.",
        "secondary_meta": "پورت داخلی: ۸۰۸۸ • وضعیت: غیرفعال",
        "service_standby": "سرویس در حالت آماده‌باش",
        "status_standby": "ایزوله / استندبای",
        "footer_text": "گره‌گشا (GerehGosha) نسخه ۲.۰ • توسعه یافته توسط امیر (@amirmarandidev) • تمامی حقوق محفوظ است.",
        "setup_tag": "راه‌اندازی اولیه",
        "setup_title": "انتخاب زبان ترجیحی",
        "setup_subtitle": "لطفاً برای اولین ورود خود، زبان مورد نظرتان را برای محیط کاربری انتخاب فرمایید.",
        "confirm_continue": "تأیید و ورود به پیشخوان",
        "change_lang": "زبان",
    },
    "ru": {
        "app_title": "GerehGosha",
        "app_subtitle": "گره‌گشا • Единый доступ к шлюзу",
        "system_title": "Шлюз управления системой",
        "system_subtitle": "Прямой доступ к вашей интеллектуальной сети маршрутизации трафика и микросервисам",
        "username": "Имя пользователя",
        "password": "Пароль",
        "sign_in": "Войти в панель управления",
        "invalid_credentials": "Неверное имя пользователя или пароль",
        "admin_badge": "Администратор",
        "sign_out": "Выйти",
        "core_title": "Движок GerehGosha (گره‌گشا)",
        "core_desc": "Высокопроизводительное ядро многоузловой маршрутизации, мониторинг телеметрии и балансировщик.",
        "core_meta": "ВНУТРЕННИЙ ПОРТ: 54322 • МАРШРУТ: /tor/",
        "launch_core": "Запустить панель GerehGosha →",
        "status_online": "● ОНЛАЙН И АКТИВЕН",
        "secondary_title": "Вторичный сервис GerehGosha",
        "secondary_desc": "Вторичный протокол изолирован локально для будущих обновлений. Исключен из работы.",
        "secondary_meta": "ВНУТРЕННИЙ ПОРТ: 8088 • СТАТУС: ОФЛАЙН",
        "service_standby": "Служба в режиме ожидания",
        "status_standby": "ИЗОЛИРОВАНО / ОЖИДАНИЕ",
        "footer_text": "GerehGosha (گره‌گشا) v2.0 • Разработано Amir (@amirmarandidev) • Все права защищены.",
        "setup_tag": "Начальная настройка",
        "setup_title": "Выберите предпочитаемый язык",
        "setup_subtitle": "Пожалуйста, выберите предпочитаемый язык для продолжения работы с панелью.",
        "continue_btn": "Продолжить в панель",
        "change_lang": "Язык",
    },
    "zh": {
        "app_title": "GerehGosha",
        "app_subtitle": "گره‌گشا • 统一网关访问控制",
        "system_title": "系统控制网关",
        "system_subtitle": "直接访问智能流量路由网络和微服务",
        "username": "用户名",
        "password": "密码",
        "sign_in": "登录到控制面板",
        "invalid_credentials": "用户名或密码错误",
        "admin_badge": "管理员",
        "sign_out": "退出登录",
        "core_title": "GerehGosha 核心引擎 (گره‌گشا)",
        "core_desc": "高性能多节点路由核心、实时遥测监控器、延迟均衡器和 PasarGuard 同步器。",
        "core_meta": "内部端口: 54322 • 路由: /tor/",
        "launch_core": "启动 GerehGosha 仪表板 →",
        "status_online": "● 在线并已激活",
        "secondary_title": "GerehGosha 次级载体",
        "secondary_desc": "次级协议保持本地隔离以备后续设计。目前不参与日常活跃运行。",
        "secondary_meta": "内部端口: 8088 • 状态: 离线",
        "service_standby": "服务处于待命状态",
        "status_standby": "隔离 / 待命",
        "footer_text": "GerehGosha (گره‌گشا) v2.0 • 由 Amir (@amirmarandidev) 设计与开发 • 保留所有权利。",
        "setup_tag": "首次设置",
        "setup_title": "选择首选语言",
        "setup_subtitle": "请选择您的首选界面语言以继续使用控制面板。",
        "continue_btn": "确认并进入控制台",
        "change_lang": "语言",
    },
}

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ languages[lang]['dir'] }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GerehGosha Gateway - {{ t['sign_in'] }}</title>
    <link rel="icon" type="image/jpeg" href="/favicon.ico">
    <link rel="shortcut icon" href="/favicon.ico">
    <link rel="apple-touch-icon" href="/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;500;600;700&family=Vazirmatn:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(17, 24, 39, 0.75);
            --border: rgba(255, 255, 255, 0.08);
            --primary: #06b6d4;
            --primary-glow: rgba(6, 182, 212, 0.35);
            --accent: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Vazirmatn', 'Outfit', sans-serif;
            background: radial-gradient(circle at 50% 20%, #111a2e 0%, var(--bg) 70%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-main);
            padding: 1.5rem;
        }
        .login-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(6, 182, 212, 0.08);
            width: 100%;
            max-width: 420px;
            padding: 2.5rem;
            position: relative;
            overflow: hidden;
        }
        .login-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #06b6d4, #3b82f6, #10b981);
        }
        .lang-top-bar {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1rem;
            gap: 0.35rem;
        }
        .lang-pill {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 0.25rem 0.55rem;
            border-radius: 6px;
            font-size: 0.75rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }
        .lang-pill:hover {
            border-color: var(--primary);
            color: #fff;
            background: rgba(6, 182, 212, 0.1);
        }
        .lang-pill.active {
            background: rgba(6, 182, 212, 0.2);
            border-color: var(--primary);
            color: #fff;
            font-weight: 600;
        }
        .logo-area {
            text-align: center;
            margin-bottom: 2rem;
        }
        .logo-icon {
            width: 58px;
            height: 58px;
            border-radius: 16px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.75rem;
            box-shadow: 0 0 25px var(--primary-glow);
            overflow: hidden;
            border: 1px solid rgba(6, 182, 212, 0.45);
            background: #0f172a;
        }
        .logo-icon img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .logo-title {
            font-size: 1.6rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #ffffff 40%, var(--primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .logo-subtitle {
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
            letter-spacing: 0.5px;
        }
        .error-alert {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            padding: 0.75rem;
            border-radius: 10px;
            font-size: 0.85rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .form-group {
            margin-bottom: 1.25rem;
        }
        label {
            display: block;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 0.4rem;
            letter-spacing: 0.5px;
        }
        input {
            width: 100%;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border);
            color: #fff;
            padding: 0.75rem 1rem;
            border-radius: 10px;
            font-family: inherit;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }
        .btn-submit {
            width: 100%;
            background: linear-gradient(135deg, #06b6d4, #0284c7);
            color: white;
            border: none;
            padding: 0.85rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px var(--primary-glow);
            margin-top: 0.5rem;
        }
        .btn-submit:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
        }
        .footer-sig {
            margin-top: 2rem;
            text-align: center;
            font-size: 0.75rem;
            color: #6b7280;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 1rem;
        }
        .footer-sig a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="lang-top-bar">
            {% for code, info in languages.items() %}
            <a href="javascript:void(0)" onclick="setLoginLang('{{ code }}')" class="lang-pill {% if lang == code %}active{% endif %}">
                <span>{{ info['flag'] }}</span>
                <span>{{ info['name'] }}</span>
            </a>
            {% endfor %}
        </div>

        <div class="logo-area">
            <div class="logo-icon">
                <img src="/static/gereh.jpg" alt="GerehGosha Logo">
            </div>
            <div class="logo-title">{{ t['app_title'] }}</div>
            <div class="logo-subtitle">{{ t['app_subtitle'] }}</div>
        </div>

        {% if error %}
        <div class="error-alert">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label>{{ t['username'] }}</label>
                <input type="text" name="username" placeholder="admin" required autocomplete="username">
            </div>
            <div class="form-group">
                <label>{{ t['password'] }}</label>
                <input type="password" name="password" placeholder="••••••••" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn-submit">{{ t['sign_in'] }}</button>
        </form>

        <div class="footer-sig">
            {{ t['footer_text'] }}
        </div>
    </div>

    <script>
        async function setLoginLang(code) {
            document.cookie = "user_lang=" + code + "; path=/; max-age=" + (365*86400) + "; SameSite=Lax";
            try {
                await fetch('/api/language', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ language: code })
                });
            } catch(e) {}
            window.location.reload();
        }
    </script>
</body>
</html>
"""

LANGUAGE_SETUP_HTML = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ languages[lang]['dir'] }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GerehGosha - {{ t['setup_title'] }}</title>
    <link rel="icon" type="image/jpeg" href="/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;500;600;700&family=Vazirmatn:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(17, 24, 39, 0.75);
            --border: rgba(255, 255, 255, 0.08);
            --primary: #06b6d4;
            --primary-glow: rgba(6, 182, 212, 0.35);
            --accent: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Vazirmatn', 'Outfit', sans-serif;
            background: radial-gradient(circle at 50% 20%, #111a2e 0%, var(--bg) 70%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-main);
            padding: 1.5rem;
        }
        .setup-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(6, 182, 212, 0.08);
            width: 100%;
            max-width: 480px;
            padding: 2.5rem;
            position: relative;
            overflow: hidden;
        }
        .setup-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #06b6d4, #3b82f6, #10b981);
        }
        .logo-area { text-align: center; margin-bottom: 1.25rem; }
        .logo-icon {
            width: 58px; height: 58px; border-radius: 16px;
            display: inline-flex; align-items: center; justify-content: center;
            margin-bottom: 0.75rem; box-shadow: 0 0 25px var(--primary-glow);
            overflow: hidden; border: 1px solid rgba(6, 182, 212, 0.45);
            background: #0f172a;
        }
        .logo-icon img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .logo-title {
            font-size: 1.6rem; font-weight: 700;
            background: linear-gradient(135deg, #ffffff 40%, var(--primary) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .setup-tag {
            display: inline-block;
            background: rgba(6, 182, 212, 0.15);
            border: 1px solid rgba(6, 182, 212, 0.3);
            color: #38bdf8;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            margin-top: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .setup-title {
            font-size: 1.25rem; font-weight: 700; margin-top: 1rem; text-align: center;
        }
        .setup-subtitle {
            font-size: 0.85rem; color: var(--text-muted); margin-top: 0.4rem; text-align: center; line-height: 1.5; margin-bottom: 1.5rem;
        }
        .lang-options-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.9rem;
            margin-bottom: 1.75rem;
        }
        .lang-card-option {
            background: rgba(15, 23, 42, 0.7);
            border: 2px solid var(--border);
            border-radius: 14px;
            padding: 1.1rem 0.8rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            position: relative;
        }
        .lang-card-option:hover {
            border-color: rgba(6, 182, 212, 0.5);
            transform: translateY(-2px);
            background: rgba(15, 23, 42, 0.9);
        }
        .lang-card-option.selected {
            border-color: var(--primary);
            background: rgba(6, 182, 212, 0.12);
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.25);
        }
        .lang-flag { font-size: 2.2rem; margin-bottom: 0.4rem; line-height: 1; }
        .lang-name { font-weight: 700; font-size: 1rem; color: #fff; }
        .lang-sub { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem; }
        .lang-check {
            position: absolute; top: 8px; right: 8px;
            width: 20px; height: 20px; border-radius: 50%;
            background: var(--primary); color: #000;
            display: none; align-items: center; justify-content: center;
            font-size: 0.7rem; font-weight: bold;
        }
        [dir="rtl"] .lang-check { right: auto; left: 8px; }
        .lang-card-option.selected .lang-check { display: flex; }
        .btn-submit {
            width: 100%;
            background: linear-gradient(135deg, #06b6d4, #0284c7);
            color: white;
            border: none;
            padding: 0.9rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px var(--primary-glow);
            display: flex; align-items: center; justify-content: center; gap: 0.5rem;
        }
        .btn-submit:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
        }
        .footer-sig {
            margin-top: 1.5rem; text-align: center; font-size: 0.75rem; color: #6b7280;
            border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 0.75rem;
        }
        .footer-sig a { color: var(--primary); text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="setup-card">
        <div class="logo-area">
            <div class="logo-icon">
                <img src="/static/gereh.jpg" alt="GerehGosha Logo">
            </div>
            <div class="logo-title">{{ t['app_title'] }}</div>
            <span class="setup-tag">{{ t['setup_tag'] }}</span>
        </div>

        <h2 class="setup-title">{{ t['setup_title'] }}</h2>
        <p class="setup-subtitle">{{ t['setup_subtitle'] }}</p>

        <form method="POST" action="/setup-language" id="lang-form">
            <input type="hidden" name="language" id="selected-language-input" value="{{ lang }}">
            <div class="lang-options-grid">
                <div class="lang-card-option {% if lang == 'fa' %}selected{% endif %}" onclick="selectLangOption('fa', this)">
                    <div class="lang-check"><i class="fa-solid fa-check"></i></div>
                    <span class="lang-flag">🇮🇷</span>
                    <span class="lang-name">فارسی</span>
                    <span class="lang-sub">Persian (Farsi)</span>
                </div>
                <div class="lang-card-option {% if lang == 'en' %}selected{% endif %}" onclick="selectLangOption('en', this)">
                    <div class="lang-check"><i class="fa-solid fa-check"></i></div>
                    <span class="lang-flag">🇬🇧</span>
                    <span class="lang-name">English</span>
                    <span class="lang-sub">English</span>
                </div>
                <div class="lang-card-option {% if lang == 'ru' %}selected{% endif %}" onclick="selectLangOption('ru', this)">
                    <div class="lang-check"><i class="fa-solid fa-check"></i></div>
                    <span class="lang-flag">🇷🇺</span>
                    <span class="lang-name">Русский</span>
                    <span class="lang-sub">Russian</span>
                </div>
                <div class="lang-card-option {% if lang == 'zh' %}selected{% endif %}" onclick="selectLangOption('zh', this)">
                    <div class="lang-check"><i class="fa-solid fa-check"></i></div>
                    <span class="lang-flag">🇨🇳</span>
                    <span class="lang-name">中文</span>
                    <span class="lang-sub">Chinese</span>
                </div>
            </div>

            <button type="submit" class="btn-submit">
                <span>{{ t['confirm_continue'] }}</span>
                <i class="fa-solid fa-arrow-right"></i>
            </button>
        </form>

        <div class="footer-sig">
            {{ t['footer_text'] }}
        </div>
    </div>

    <script>
        function selectLangOption(code, el) {
            document.querySelectorAll('.lang-card-option').forEach(c => c.classList.remove('selected'));
            el.classList.add('selected');
            document.getElementById('selected-language-input').value = code;
        }
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="{{ lang }}" dir="{{ languages[lang]['dir'] }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GerehGosha Unified Dashboard</title>
    <link rel="icon" type="image/jpeg" href="/favicon.ico">
    <link rel="shortcut icon" href="/favicon.ico">
    <link rel="apple-touch-icon" href="/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;500;600;700&family=Vazirmatn:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg: #090d16;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border: rgba(255, 255, 255, 0.08);
            --primary: #06b6d4;
            --primary-glow: rgba(6, 182, 212, 0.3);
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.3);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Vazirmatn', 'Outfit', sans-serif;
            background: radial-gradient(circle at 50% 10%, #111a2e 0%, var(--bg) 75%);
            min-height: 100vh;
            color: var(--text-main);
            display: flex;
            flex-direction: column;
        }
        .navbar {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .brand-icon {
            width: 38px;
            height: 38px;
            border: 1px solid rgba(6, 182, 212, 0.4);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background: #0f172a;
            box-shadow: 0 0 15px var(--primary-glow);
        }
        .brand-icon img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .brand-text h1 {
            font-size: 1.15rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-text span {
            font-size: 0.72rem;
            color: var(--text-muted);
            letter-spacing: 0.4px;
        }
        .user-nav {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }
        
        /* Language Dropdown */
        .lang-dropdown {
            position: relative;
        }
        .lang-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.4rem 0.8rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            transition: all 0.2s;
            font-family: inherit;
        }
        .lang-btn:hover {
            border-color: var(--primary);
            background: rgba(6, 182, 212, 0.1);
        }
        .lang-btn i.fa-globe {
            color: var(--primary);
        }
        .lang-menu {
            position: absolute;
            top: calc(100% + 6px);
            right: 0;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.5), 0 0 20px rgba(6, 182, 212, 0.1);
            width: 170px;
            padding: 0.4rem;
            display: none;
            flex-direction: column;
            gap: 0.2rem;
            z-index: 100;
        }
        [dir="rtl"] .lang-menu {
            right: auto;
            left: 0;
        }
        .lang-menu.show {
            display: flex;
        }
        .lang-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.85rem;
            transition: all 0.15s;
        }
        .lang-item:hover {
            background: rgba(6, 182, 212, 0.15);
            color: #fff;
        }
        .lang-item.active {
            background: rgba(6, 182, 212, 0.2);
            color: var(--primary);
            font-weight: 600;
        }
        .lang-item-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .lang-item i.check {
            font-size: 0.75rem;
            color: var(--primary);
        }

        .user-badge {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            padding: 0.4rem 0.85rem;
            border-radius: 8px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }
        .user-badge b { color: #fff; }
        .nav-btn {
            color: #fca5a5;
            text-decoration: none;
            padding: 0.4rem 0.9rem;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.25);
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s;
        }
        .nav-btn:hover {
            background: rgba(239, 68, 68, 0.25);
        }
        .main-container {
            flex: 1;
            max-width: 1000px;
            margin: 0 auto;
            padding: 3rem 1.5rem;
            width: 100%;
        }
        .hero {
            text-align: center;
            margin-bottom: 3rem;
        }
        .hero h2 {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .hero p {
            color: var(--text-muted);
            font-size: 1rem;
            max-width: 550px;
            margin: 0 auto;
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.75rem;
        }
        .card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
        }
        .card.active-primary {
            border-color: rgba(6, 182, 212, 0.4);
            box-shadow: 0 10px 30px rgba(6, 182, 212, 0.1);
        }
        .card.active-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(6, 182, 212, 0.2);
            border-color: var(--primary);
        }
        .card.isolated-card {
            opacity: 0.65;
            border-style: dashed;
        }
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
        }
        .card-tag {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
        }
        .tag-active {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
        }
        .tag-standby {
            background: rgba(156, 163, 175, 0.15);
            border: 1px solid rgba(156, 163, 175, 0.3);
            color: #9ca3af;
        }
        .card-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .card-desc {
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.5;
            margin-bottom: 1.5rem;
            flex: 1;
        }
        .card-meta {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            color: #64748b;
            margin-bottom: 1.25rem;
            background: rgba(0, 0, 0, 0.2);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
        }
        .card-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.85rem 1.5rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.95rem;
            text-decoration: none;
            transition: all 0.2s;
        }
        .btn-launch {
            background: linear-gradient(135deg, #06b6d4, #0284c7);
            color: white;
            box-shadow: 0 4px 14px var(--primary-glow);
        }
        .btn-launch:hover {
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45);
            transform: translateY(-1px);
        }
        .btn-disabled {
            background: rgba(255, 255, 255, 0.05);
            color: #6b7280;
            cursor: not-allowed;
            pointer-events: none;
        }
        .footer {
            text-align: center;
            padding: 2rem 1.5rem;
            font-size: 0.8rem;
            color: #6b7280;
            border-top: 1px solid var(--border);
        }
        .footer a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="brand">
            <div class="brand-icon">
                <img src="/static/gereh.jpg" alt="GerehGosha Logo">
            </div>
            <div class="brand-text">
                <h1>{{ t['app_title'] }}</h1>
                <span>{{ t['app_subtitle'] }}</span>
            </div>
        </div>
        <div class="user-nav">
            <!-- Language Selection Icon & Dropdown -->
            <div class="lang-dropdown">
                <button class="lang-btn" id="lang-btn" type="button" onclick="toggleLangMenu()" title="{{ t['change_lang'] }}">
                    <i class="fa-solid fa-globe"></i>
                    <span>{{ languages[lang]['flag'] }} {{ languages[lang]['name'] }}</span>
                    <i class="fa-solid fa-chevron-down" style="font-size: 0.7rem;"></i>
                </button>
                <div class="lang-menu" id="lang-menu">
                    {% for code, info in languages.items() %}
                    <a href="javascript:void(0)" onclick="switchLanguage('{{ code }}')" class="lang-item {% if lang == code %}active{% endif %}">
                        <div class="lang-item-content">
                            <span>{{ info['flag'] }}</span>
                            <span>{{ info['name'] }}</span>
                        </div>
                        {% if lang == code %}<i class="fa-solid fa-check check"></i>{% endif %}
                    </a>
                    {% endfor %}
                </div>
            </div>

            <div class="user-badge">{{ t['admin_badge'] }}: <b>{{ session['username'] }}</b></div>
            <a href="/logout" class="nav-btn">{{ t['sign_out'] }}</a>
        </div>
    </div>

    <div class="main-container">
        <div class="hero">
            <h2>{{ t['system_title'] }}</h2>
            <p>{{ t['system_subtitle'] }}</p>
        </div>

        <div class="cards-grid">
            <div class="card active-primary">
                <div class="card-header">
                    <span class="card-tag tag-active">{{ t['status_online'] }}</span>
                </div>
                <h3 class="card-title">{{ t['core_title'] }}</h3>
                <p class="card-desc">{{ t['core_desc'] }}</p>
                <div class="card-meta">{{ t['core_meta'] }}</div>
                <a href="/tor/" class="card-btn btn-launch">{{ t['launch_core'] }}</a>
            </div>

            <div class="card isolated-card">
                <div class="card-header">
                    <span class="card-tag tag-standby">{{ t['status_standby'] }}</span>
                </div>
                <h3 class="card-title">{{ t['secondary_title'] }}</h3>
                <p class="card-desc">{{ t['secondary_desc'] }}</p>
                <div class="card-meta">{{ t['secondary_meta'] }}</div>
                <span class="card-btn btn-disabled">{{ t['service_standby'] }}</span>
            </div>
        </div>
    </div>

    <div class="footer">
        {{ t['footer_text'] }}
    </div>

    <script>
        function toggleLangMenu() {
            const menu = document.getElementById('lang-menu');
            menu.classList.toggle('show');
        }
        window.addEventListener('click', function(e) {
            const btn = document.getElementById('lang-btn');
            const menu = document.getElementById('lang-menu');
            if (menu && btn && !btn.contains(e.target) && !menu.contains(e.target)) {
                menu.classList.remove('show');
            }
        });
        async function switchLanguage(code) {
            document.cookie = "user_lang=" + code + "; path=/; max-age=" + (365*86400) + "; SameSite=Lax";
            try {
                const res = await fetch('/api/language', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ language: code })
                });
            } catch(e) {}
            window.location.reload();
        }
    </script>
</body>
</html>
"""

def get_current_language():
    lang = session.get("lang") or request.cookies.get("user_lang") or "en"
    if lang not in ALLOWED_LANGUAGES:
        lang = "en"
    return lang

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    lang = get_current_language()
    t = TRANSLATIONS[lang]

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash, preferred_language FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and check_password_hash(row[0], password):
                session.permanent = True
                session["logged_in"] = True
                session["username"] = username
                preferred_lang = row[1]
                
                # Check for first-time login: if preferred_language is NOT set in DB
                if not preferred_lang or preferred_lang not in ALLOWED_LANGUAGES:
                    session["needs_language_setup"] = True
                    return redirect(url_for("setup_language"))
                else:
                    # Subsequent logins: retrieve saved language into session
                    session["lang"] = preferred_lang
                    session.pop("needs_language_setup", None)
                    resp = redirect(url_for("dashboard"))
                    resp.set_cookie("user_lang", preferred_lang, max_age=365*86400, samesite="Lax")
                    return resp
            else:
                error = t["invalid_credentials"]

    return render_template_string(LOGIN_HTML, error=error, lang=lang, languages=LANGUAGES, t=t)

@app.route("/setup-language", methods=["GET", "POST"])
def setup_language():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    username = session.get("username")
    lang = get_current_language()
    
    if request.method == "POST":
        selected_lang = request.form.get("language")
        if selected_lang in ALLOWED_LANGUAGES:
            session.permanent = True
            session["lang"] = selected_lang
            session.pop("needs_language_setup", None)
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("UPDATE users SET preferred_language = ? WHERE username = ?", (selected_lang, username))
                conn.commit()
            resp = redirect(url_for("dashboard"))
            resp.set_cookie("user_lang", selected_lang, max_age=365*86400, samesite="Lax")
            return resp

    t = TRANSLATIONS[lang]
    return render_template_string(LANGUAGE_SETUP_HTML, lang=lang, languages=LANGUAGES, t=t)

@app.route("/api/language", methods=["GET", "POST"])
def api_language():
    if request.method == "POST":
        data = request.get_json(silent=True) or request.form
        chosen_lang = data.get("language") if data else None
        if chosen_lang in ALLOWED_LANGUAGES:
            session.permanent = True
            session["lang"] = chosen_lang
            username = session.get("username")
            if username:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute("UPDATE users SET preferred_language = ? WHERE username = ?", (chosen_lang, username))
                    conn.commit()
            resp = Response(json.dumps({"status": "ok", "language": chosen_lang}), mimetype="application/json")
            resp.set_cookie("user_lang", chosen_lang, max_age=365*86400, samesite="Lax")
            return resp
        return Response(json.dumps({"status": "error", "message": "Invalid language"}), status=400, mimetype="application/json")

    lang = get_current_language()
    return Response(json.dumps({"language": lang, "username": session.get("username")}), mimetype="application/json")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/favicon.ico")
@app.route("/static/gereh.jpg")
def serve_gateway_logo():
    return Response(
        ui_theme.ICON_BYTES,
        mimetype="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"}
    )

@app.before_request
def require_login():
    if request.path in ["/favicon.ico", "/static/gereh.jpg"] or request.path.startswith("/static/"):
        return
    if not session.get("logged_in") and request.endpoint not in ["login", "serve_gateway_logo", "api_language"]:
        return redirect(url_for("login"))
    if session.get("logged_in") and session.get("needs_language_setup"):
        if request.endpoint not in ["setup_language", "logout", "serve_gateway_logo", "api_language"]:
            return redirect(url_for("setup_language"))

@app.route("/")
def dashboard():
    lang = get_current_language()
    t = TRANSLATIONS[lang]
    return render_template_string(DASHBOARD_HTML, lang=lang, languages=LANGUAGES, t=t)

# Reverse proxy for Tor Panel (Port 54322)
@app.route("/tor", defaults={"path": ""})
@app.route("/tor/", defaults={"path": ""})
@app.route("/tor/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_tor(path):
    target_path = request.path.replace("/tor", "", 1) or "/"
    return _proxy_request("http://127.0.0.1:54322", target_path, request)

# Reverse proxy for Surfshark Panel (Port 8088)
@app.route("/surfshark", defaults={"path": ""})
@app.route("/surfshark/", defaults={"path": ""})
@app.route("/surfshark/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_surfshark(path):
    target_path = request.path.replace("/surfshark", "", 1) or "/"
    return _proxy_request("http://127.0.0.1:8088", target_path, request)

# Catch-all proxy for /static/ and /api/ based on Referer header
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_shared(path):
    referer = request.headers.get("Referer", "")
    if "/tor/" in referer or "/tor" in referer:
        base_url = "http://127.0.0.1:54322"
    elif "/surfshark/" in referer or "/surfshark" in referer:
        base_url = "http://127.0.0.1:8088"
    else:
        # If no referer is available, try to route based on path hints or default to Tor
        if "surfshark" in path:
            base_url = "http://127.0.0.1:8088"
        else:
            base_url = "http://127.0.0.1:54322"

    return _proxy_request(base_url, "/" + path, request)

def _proxy_request(base_url, path, req):
    url = f"{base_url}{path}"
    if req.query_string:
        url += f"?{req.query_string.decode('utf-8')}"
    
    try:
        # Forward the request to the underlying microservice
        headers = {key: value for (key, value) in req.headers if key.lower() not in ['host', 'content-length']}
        resp = requests.request(
            method=req.method,
            url=url,
            headers=headers,
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            timeout=120)
        
        # Exclude headers that cause issues with Flask's response mechanism
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [(name, value) for (name, value) in resp.raw.headers.items()
                            if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, response_headers)
    except requests.exceptions.RequestException as e:
        error_msg = f"""<!DOCTYPE html>
<html><head><title>GerehGosha - Core Warming Up</title>
<style>
    body {{ font-family: sans-serif; background: #090d16; color: #f3f4f6; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
    .card {{ background: rgba(17, 24, 39, 0.85); border: 1px solid rgba(255,255,255,0.1); padding: 2.5rem; border-radius: 16px; text-align: center; max-width: 450px; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
    h3 {{ color: #06b6d4; margin-bottom: 0.5rem; font-size: 1.3rem; }}
    p {{ color: #9ca3af; font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem; }}
    a {{ background: linear-gradient(135deg, #06b6d4, #0284c7); color: #fff; padding: 0.65rem 1.25rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
</style>
</head><body>
    <div class="card">
        <h3>GerehGosha Service Initializing</h3>
        <p>The routing backend at <b>{base_url}</b> is currently booting up or establishing circuits. Please wait a moment and reload.</p>
        <a href="javascript:location.reload()">Reload Page ↻</a>
    </div>
</body></html>"""
        return error_msg, 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
