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

import sqlite3
import requests
from flask import Flask, request, session, redirect, url_for, render_template_string, Response
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Disable default static folder so we can proxy /static/
app = Flask(__name__, static_folder=None)
app.secret_key = "super_secret_gateway_key_change_in_production"

# Trust Nginx reverse proxy headers (X-Forwarded-Proto, X-Forwarded-Host, etc.)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

DB_PATH = "auth.db"

# Ensure the DB exists
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)")
init_db()

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GerehGosha Gateway - Login</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
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
            font-family: 'Outfit', sans-serif;
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
            max-width: 400px;
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
        .logo-area {
            text-align: center;
            margin-bottom: 2rem;
        }
        .logo-icon {
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(16, 185, 129, 0.2));
            border: 1px solid rgba(6, 182, 212, 0.4);
            border-radius: 14px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 0.75rem;
            box-shadow: 0 0 20px var(--primary-glow);
        }
        .logo-icon svg { width: 28px; height: 28px; fill: var(--primary); }
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
            text-transform: uppercase;
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
        <div class="logo-area">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
            </div>
            <div class="logo-title">GerehGosha</div>
            <div class="logo-subtitle">گره‌گشا • Unified Gateway Access</div>
        </div>

        {% if error %}
        <div class="error-alert">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="admin" required autocomplete="username">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="••••••••" required autocomplete="current-password">
            </div>
            <button type="submit" class="btn-submit">Sign In to Dashboard</button>
        </form>

        <div class="footer-sig">
            GerehGosha v2.0 • Created by <a href="https://t.me/amirmarandidev" target="_blank">Amir (@amirmarandidev)</a>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GerehGosha Unified Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
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
            font-family: 'Outfit', sans-serif;
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
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.25), rgba(16, 185, 129, 0.25));
            border: 1px solid rgba(6, 182, 212, 0.4);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .brand-icon svg { width: 20px; height: 20px; fill: var(--primary); }
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
            gap: 1rem;
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
                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
            </div>
            <div class="brand-text">
                <h1>GerehGosha</h1>
                <span>گره‌گشا • Core Gateway</span>
            </div>
        </div>
        <div class="user-nav">
            <div class="user-badge">Admin: <b>{{ session['username'] }}</b></div>
            <a href="/logout" class="nav-btn">Sign Out</a>
        </div>
    </div>

    <div class="main-container">
        <div class="hero">
            <h2>System Control Gateway</h2>
            <p>Direct access to your intelligent traffic routing network and microservices</p>
        </div>

        <div class="cards-grid">
            <div class="card active-primary">
                <div class="card-header">
                    <span class="card-tag tag-active">● ONLINE & ACTIVE</span>
                </div>
                <h3 class="card-title">GerehGosha Engine (گره‌گشا)</h3>
                <p class="card-desc">High-performance multi-node routing core, telemetry monitor, latency balancer, and Pasarguard synchronizer.</p>
                <div class="card-meta">INTERNAL PORT: 54322 • ROUTE: /tor/</div>
                <a href="/tor/" class="card-btn btn-launch">Launch GerehGosha Dashboard →</a>
            </div>

            <div class="card isolated-card">
                <div class="card-header">
                    <span class="card-tag tag-standby">ISOLATED / STANDBY</span>
                </div>
                <h3 class="card-title">GerehGosha Secondary Carrier</h3>
                <p class="card-desc">Secondary carrier protocol is kept in local isolation for future redesign. Excluded from active operations.</p>
                <div class="card-meta">INTERNAL PORT: 8088 • STATUS: OFFLINE</div>
                <span class="card-btn btn-disabled">Service In Standby</span>
            </div>
        </div>
    </div>

    <div class="footer">
        GerehGosha (گره‌گشا) v2.0 • Designed & Developed by <a href="https://t.me/amirmarandidev" target="_blank">Amir (@amirmarandidev)</a> • All rights reserved.
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and check_password_hash(row[0], password):
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid credentials"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.before_request
def require_login():
    if not session.get("logged_in") and request.endpoint != "login":
        return redirect(url_for("login"))

@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

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

