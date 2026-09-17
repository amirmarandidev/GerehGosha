<div align="center">

# 🌐 Language / زبان / Язык / 语言

**English** • [فارسی](README_FA.md) • [Русский](README_RU.md) • [简体中文](README_ZH.md)

---

# 🧅 GerehGosha · گره‌گشا

**Intelligent Multi-Country Traffic Routing & Panel Injection Utility**

Developed with ❤️ by [Amir Marandi](https://github.com/amirmarandidev)

[![Version](https://img.shields.io/badge/version-2.6.2-10b981?style=flat-square)](#)
[![Telegram](https://img.shields.io/badge/telegram-@amirmarandidev-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/amirmarandidev)
[![License](https://img.shields.io/badge/license-open%20source-6b7280?style=flat-square)](#)

</div>

---

### 💡 What is GerehGosha? (Important Clarification)

> [!IMPORTANT]
> **GerehGosha is NOT a standalone VPN panel or user-subscription system that generates direct VLESS/VMess configurations out of the box.**

Instead, **GerehGosha is a specialized infrastructure routing utility and multi-exit traffic orchestrator**. It continuously scans, discovers, and sustains high-quality, low-latency international onion exit circuits, exposing them as clean, isolated local SOCKS5 endpoints (`9050+`). 

Its primary superpower is **automated injection**: with a single click or API call, it injects these multi-country outbound nodes directly into your upstream management panels (such as **PasarGuard**) as configured inbounds and hosts. This allows panel operators to bundle multiple clean international exit locations directly into their clients' production configs without manual routing configurations.

#### 🔌 Panel Compatibility & Roadmap:
* ✅ **PasarGuard:** Fully supported with automated 1-click inbound/host injection via Admin API.
* 🔄 **x-ui / 3X-UI:** *In active development* (Automated inbound & routing injection coming soon).
* 🔄 **Marzban:** *In active development* (Node and outbound injection pipeline under active testing).

---

### 💖 Support the Project
This utility is free and open source. If it saves you time and simplifies your routing infrastructure, support ongoing development by giving a ⭐ on GitHub or contributing via crypto:

* 🔹 **USDT (BEP20):** `0xd593ae9D32bEA690EC62460C54BF3951aFFF7803`
* 🔸 **USDT (TRC20):** `THaaHzoTwXfUfcrtYTDXRsMmk9qhnXa56M`

---

### ⚠️ Critical Hosting Advisory (Read Before Deployment!)

To ensure peak performance, minimal latency, and zero connection drops with GerehGosha, host location and provider network policies are critical:

* ❌ **Providers with High Rate-Limits & Restricted Packet Policies:**  
  Servers hosted on **Hetzner**, **OVH**, and **DigitalOcean** often enforce strict protocol rate-limits and aggressive traffic filtering on multi-hop onion circuits, resulting in unstable connections, high packet loss, or unexpected timeouts.

* ✅ **Tested & Recommended Hosting Platforms:**  
  GerehGosha has undergone rigorous testing and delivers smooth, stable, high-throughput results on **Railway**, **Play2Go**, **Fly.io**, **Vultr**, and **Linode / Akamai**.

> 💬 **A Word from the Developer:**  
> This project is continually evolving! The routing engine, RAM footprint, and health-check mechanisms are continuously optimized to give you rock-solid stability. Choose your server platform wisely, and the engine will handle the rest.

---

### ✨ Key Capabilities

* 🌐 **Live Scanning & Auto-Discovery:** Real-time discovery of healthy, low-latency international relays across dozens of countries.
* ⚡ **Multi-Country Concurrent Exits:** Run multiple isolated geographical exits (US, Germany, Netherlands, UK, etc.) simultaneously on dedicated local ports (`9050`, `9051`, etc.).
* 💉 **1-Click Panel Injection:** Automatically register corresponding inbounds, ports, and tags directly inside PasarGuard with zero manual JSON editing.
* 🔄 **Instant "New IP" Circuit Rotation:** Detect route degradation and obtain a brand-new exit IP and circuit instantly with a single button press.
* 🛡️ **Secure Unified Gateway Dashboard:** Clean, responsive web dashboard with persistent database authentication, multi-language switching (English, Persian, Russian, Chinese), and credential management.
* 💻 **Interactive CLI Console:** Built-in `gerehgosha` command for effortless service monitoring, diagnostics, and credential recovery.
* 🚀 **Seamless Zero-Downtime Updates:** Run `gerehgosha update` to pull the latest code without wiping administrative accounts or existing configurations.

---

### 🚀 Quick Start & Installation

#### 1. One-Line Fast Install (Linux / Production)
Run this single command in your server terminal with root privileges:
```bash
sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/amirmarandidev/GerehGosha/master/gerehgosha.sh)" @ install
```
> 💡 **Tip:** You can also run updates or uninstallations directly via:
> - **Update:** `sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/amirmarandidev/GerehGosha/master/gerehgosha.sh)" @ update`
> - **Uninstall:** `sudo bash -c "$(curl -fsSL https://raw.githubusercontent.com/amirmarandidev/GerehGosha/master/gerehgosha.sh)" @ uninstall`

#### Alternative: Manual Git Clone
```bash
git clone https://github.com/amirmarandidev/GerehGosha.git /opt/gerehgosha
cd /opt/gerehgosha
sudo bash install.sh
```

#### 2. Windows Environment (Testing & Development)
Launch the unified runner batch script:
```cmd
run_windows.bat
```

---

### 🔑 Ports & Architecture

* 🌐 **Unified Web Dashboard:** `http://SERVER_IP:5000`
* ⚙️ **Direct Core Engine:** `http://SERVER_IP:54322`
* 🔌 **Isolated SOCKS5 Outbounds:** `9050+` (Sequential ports per selected country)
* 📁 **Default Installation Path:** `/opt/gerehgosha`

> **View Admin Credentials:** Retrieve or manage panel credentials at any time by running `gerehgosha` and selecting **Manage Admins**, or via CLI flags.

---

### 💻 Command-Line Interface (CLI)

Typing `gerehgosha` in your terminal launches the interactive management suite:

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

#### One-Liner Quick Commands:
* 🔄 **Seamless Update:** `gerehgosha update`
* 🔑 **Display Credentials:** `python3 /opt/gerehgosha/gerehgosha-cli.py --show-credentials`
* 🩺 **Health Check & Status:** `python3 /opt/gerehgosha/gerehgosha-cli.py --status`
* 🧹 **Flush Cache & Circuits:** `python3 /opt/gerehgosha/gerehgosha-cli.py --flush-cache`

---

### 📖 Documentation & Tutorials

Looking for a step-by-step tutorial on how to configure circuits and connect with upstream panels?  
Check out our [Usage Tutorial & Step-by-Step Guide](TUTORIAL.md).

---

### ❓ Frequently Asked Questions (FAQ)

* ❓ **Can I use GerehGosha by itself to connect clients?**  
  GerehGosha provides SOCKS5 proxies on ports `9050+`. While you can point local applications directly to these ports, it is primarily intended to be injected into panels like **PasarGuard** so they can serve as upstream exit nodes in VLESS/VMess configs.
* ❓ **I forgot my web dashboard credentials:**  
  Execute `python3 /opt/gerehgosha/gerehgosha-cli.py --show-credentials` on your server to retrieve active credentials.
* ❓ **Will updating overwrite my database or settings?**  
  No. The `gerehgosha update` utility automatically backs up `auth.db` and configuration files before pulling the latest codebase.
* ❓ **How do I inspect live service logs?**  
  Run `journalctl -u gerehgosha.service -f` (Gateway) or `journalctl -u tor-checker.service -f` (Engine).

---

### 📢 Community & Support

* ✈️ **Telegram:** [@amirmarandidev](https://t.me/amirmarandidev)
* 🐙 **GitHub:** [amirmarandidev](https://github.com/amirmarandidev)
* 💼 **LinkedIn:** [amirmarandi](https://linkedin.com/in/amirmarandi)
* 📧 **Email:** [amirmarandidev@gmail.com](mailto:amirmarandidev@gmail.com)

<div align="center">

🌟 **If GerehGosha helps your infrastructure, please star the repository on GitHub!**

</div>
