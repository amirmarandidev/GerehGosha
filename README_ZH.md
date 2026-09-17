<div align="center">

# 🌐 Language / زبان / Язык / 语言

[English](README.md) • [فارسی](README_FA.md) • [Русский](README_RU.md) • **简体中文**

---

# 🧅 GerehGosha · گره‌گشا

**智能多国流量路由与面板直连注入工具**

由 [Amir Marandi](https://github.com/amirmarandidev) 用 ❤️ 倾力打造

[![Version](https://img.shields.io/badge/version-2.6.2-10b981?style=flat-square)](#)
[![Telegram](https://img.shields.io/badge/telegram-@amirmarandidev-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/amirmarandidev)
[![License](https://img.shields.io/badge/license-open%20source-6b7280?style=flat-square)](#)

</div>

---

### 💡 什么是 GerehGosha？（核心定位与概念说明）

> [!IMPORTANT]
> **GerehGosha 并不是一个开箱即用、直接生成并分发 VLESS/VMess 订阅节点的单体 VPN 面板。**

实际上，**GerehGosha 是一个专为复杂网络环境打造的基础设施流量路由与多国出口编排工具（Routing Utility）**。它在后台自动化探测、建立并维护低延迟、高可用性的国际洋葱网络链路，并为每个国家/地区提供相互隔离的本地 SOCKS5 代理端口（`9050+`）。

它的杀手级功能是 **「一键自动注入（Injection）」**：仅需一次点击或通过 API，它就能将这些多国出站落地节点直接注入到您现有的管理面板（如 **PasarGuard**）中，自动创建对应的 Inbound 节点与 Host。这使得面板管理员能够轻松地在现有节点配置中集成多个纯净的海外出口，无需手动编写复杂的路由规则与端口映射。

#### 🔌 面板兼容性与开发计划：
* ✅ **PasarGuard：** 完美支持，通过 Admin API 实现一键自动化注入 Inbound 与 Host。
* 🔄 **x-ui / 3X-UI：** *正在积极开发中*（即将推出专属的一键 Inbound 及分流规则注入功能）。
* 🔄 **Marzban（麦兹班）：** *正在积极开发中*（多节点与独立出站链路线路正在实测中）。

---

### 💖 支持开源项目
本工具完全免费且开源。如果它提升了您的网络基础设施与运维效率，欢迎在 GitHub 上点亮 ⭐ Star，或通过加密货币赞助我们：

* 🔹 **USDT (BEP20):** `0xd593ae9D32bEA690EC62460C54BF3951aFFF7803`
* 🔸 **USDT (TRC20):** `THaaHzoTwXfUfcrtYTDXRsMmk9qhnXa56M`

---

### ⚠️ 服务器选型至关重要的建议（部署前必读！）

为了确保 GerehGosha 发挥最大速率、获得极低延迟且避免意外掉线，服务器机房的选择和运营商策略至关重要：

* ❌ **存在严重限速与封包审查策略的机房：**  
  托管在 **Hetzner**、**OVH** 以及 **DigitalOcean** 的服务器，由于机房针对多跳链路实施了严格的速率限制与丢包策略，会导致节点经常断流、延迟骤增或超时。

* ✅ **经过严格测试并强烈推荐的云平台：**  
  本项目在 **Railway** 和 **Play2Go**（以及 **Fly.io**、**Vultr** 和 **Linode / Akamai**）上经过多轮长期高负载压测，表现出极为流畅、稳定且高吞吐的网络表现。

> 💬 **开发者的话：**  
> 本项目处于持续活跃维护与迭代中！核心路由引擎、内存占用率以及健康检查算法都在持续重构优化。选对机房，剩下的稳定运行交由 GerehGosha 保障。

---

### ✨ 核心功能亮点

* 🌐 **实时扫描与自愈探测：** 毫秒级探测全球可用中继，全自动挑选低延迟、高质量的国际出口。
* ⚡ **多国家并发出口（Multi-Exit）：** 在专用本地独立端口（`9050`、`9051` 等）上同时运行多个国家出口（如美国、德国、荷兰、英国等）。
* 💉 **一键注入 PasarGuard：** 告别手动配置繁琐的 JSON 文件，全自动将各地区节点注入面板。
* 🔄 **一键秒切新 IP（New IP）：** 实时感知链路拥塞，一键重置当前国家出口回路并获取全新 IP。
* 🛡️ **安全多语言统一网关仪表盘：** 轻量级响应式 Web 界面，支持 SQLite 数据库持久化认证、4 种语言即时切换（英文、波斯语、俄语、简体中文）及多管理员权限管理。
* 💻 **专属终端交互套件（CLI）：** 系统命令 `gerehgosha`，支持菜单式运维、实时诊断与凭据重置。
* 🚀 **无感平滑版本升级：** 执行 `gerehgosha update` 即可无损拉取 Git 最新代码，数据库与配置永不丢失。

---

### 🚀 快速安装与运行

#### 1. Linux 服务器（生产环境推荐）
使用 `root` 权限执行以下命令：
```bash
git clone https://github.com/thekourox/gerehgosha.git
cd gerehgosha
sudo bash install.sh
```
> 安装脚本将自动安装系统依赖、配置 systemd 后台常驻服务，并在终端打印初始管理员凭据。

#### 2. Windows 环境（测试与开发）
双击运行控制台批处理文件：
```cmd
run_windows.bat
```

---

### 🔑 端口与架构体系

* 🌐 **统一网关管理面板：** `http://SERVER_IP:5000`
* ⚙️ **核心引擎直连端口：** `http://SERVER_IP:54322`
* 🔌 **隔离的 SOCKS5 出口端口：** `9050+`（按所选国家顺序顺延递增）
* 📁 **默认服务器安装路径：** `/opt/gerehgosha`

> **查看管理员登录信息：** 随时在服务器终端输入 `gerehgosha` 并选择 **Manage Admins** 即可查看或修改密码。

---

### 💻 命令行套件（CLI）

在服务器终端输入 `gerehgosha` 即可唤出交互式管理控制台：

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

#### 一键常用命令：
* 🔄 **平滑升级：** `gerehgosha update`
* 🔑 **查看管理员密码：** `python3 /opt/gerehgosha/gerehgosha-cli.py --show-credentials`
* 🩺 **系统健康检测：** `python3 /opt/gerehgosha/gerehgosha-cli.py --status`
* 🧹 **清空缓存与回路：** `python3 /opt/gerehgosha/gerehgosha-cli.py --flush-cache`

---

### 📖 使用教程与详细指南

想要了解如何从零开始配置出口回路并完成面板对接？  
请阅读我们的 [GerehGosha 使用教程与实战指南](TUTORIAL.md)。

---

### ❓ 常见问题（FAQ）

* ❓ **我可以单独使用 GerehGosha 供客户端直连吗？**  
  GerehGosha 在 `9050+` 端口上提供纯本地 SOCKS5 代理。虽然本地软件可以直接对接该端口，但它的主要设计目的是注入到诸如 **PasarGuard** 之类的面板中，以便作为出站落地节点打包进 VLESS/VMess 配置。
* ❓ **忘记了 Web 面板的登录密码：**  
  在服务器端执行 `python3 /opt/gerehgosha/gerehgosha-cli.py --show-credentials` 即可快速找回当前有效凭据。
* ❓ **更新后会清空我的配置与数据库吗？**  
  不会。`gerehgosha update` 在拉取最新代码前会自动备份 `auth.db` 和配置文件，完成平滑迁移。
* ❓ **如何查看后台服务的实时日志？**  
  运行 `journalctl -u gerehgosha.service -f`（网关日志）或 `journalctl -u tor-checker.service -f`（引擎日志）。

---

### 📢 社区与交流

* ✈️ **Telegram：** [@amirmarandidev](https://t.me/amirmarandidev)
* 🐙 **GitHub：** [amirmarandidev](https://github.com/amirmarandidev)
* 💼 **LinkedIn：** [amirmarandi](https://linkedin.com/in/amirmarandi)
* 📧 **Email：** [amirmarandidev@gmail.com](mailto:amirmarandidev@gmail.com)

<div align="center">

🌟 **如果 GerehGosha 对您有所帮助，请在 GitHub 上给予一个 Star 鼓励！**

</div>
