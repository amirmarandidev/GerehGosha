# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - High-Performance Intelligent Traffic Routing Engine
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

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import core
import os
import sys

try:
    import ui_theme
except ImportError:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    import ui_theme
import json
import subprocess
import threading
import httpx
import uuid
import platform
import copy
import shutil
import socket
import requests

def get_emoji(country_code):
    try:
        return chr(ord(country_code[0].upper()) + 127397) + chr(ord(country_code[1].upper()) + 127397)
    except:
        return ""

COUNTRY_MAP = {
    "US": "United States", "GB": "United Kingdom", "DE": "Germany", "FR": "France", "NL": "Netherlands",
    "CA": "Canada", "SG": "Singapore", "JP": "Japan", "AU": "Australia", "IT": "Italy", "ES": "Spain",
    "CH": "Switzerland", "SE": "Sweden", "NO": "Norway", "FI": "Finland", "DK": "Denmark", "IE": "Ireland",
    "AT": "Austria", "BE": "Belgium", "PL": "Poland", "RO": "Romania", "BG": "Bulgaria", "HR": "Croatia",
    "CZ": "Czechia", "PT": "Portugal", "IS": "Iceland", "TR": "Turkey", "ID": "Indonesia", "VN": "Vietnam",
    "IN": "India", "BR": "Brazil", "ZA": "South Africa", "AE": "United Arab Emirates", "IL": "Israel",
    "HK": "Hong Kong", "TW": "Taiwan", "KR": "South Korea", "NZ": "New Zealand", "MX": "Mexico"
}

app = FastAPI(
    title="GerehGosha Engine (گره‌گشا)",
    description="Engineered and Maintained by Amir (@amirmarandidev)",
    version="2.0.0-PRO"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

@app.get("/favicon.ico", include_in_schema=False)
@app.get("/static/gereh.jpg", include_in_schema=False)
async def get_favicon_and_logo():
    return Response(
        content=ui_theme.ICON_BYTES,
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=86400"}
    )

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
async def startup_event():
    """Boot the engine in IDLE state.

    Auto-start is intentionally disabled: the operator picks their exit
    locations first and then presses Start Engine. Nothing is spawned here.
    """
    core.dashboard_state['status'] = 'idle'
    core.dashboard_state['phase'] = 'idle'
    core.dashboard_state['discovery_progress'] = 0
    core.dashboard_state['instances'] = {}
    core.dashboard_state['discovery_msg'] = (
        'Engine is idle. Run a Live Network Scan, select your exit locations, then press Start Engine.'
    )
    
    # Clear any stale mapping left behind by a previous run so PasarGuard
    # injection can never target instances that are not running.
    try:
        with open(core.PORT_MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
    except Exception:
        pass

@app.get("/")
def get_index():
    import os
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/status")
async def get_status():
    core.dashboard_state["engine"] = "GerehGosha"
    core.dashboard_state["project"] = "GerehGosha (گره‌گشا)"
    core.dashboard_state["author"] = "Amir (@amirmarandidev)"
    core.dashboard_state["telegram"] = "https://t.me/amirmarandidev"
    core.dashboard_state["email"] = "amirmarandidev@gmail.com"
    core.dashboard_state["copyright"] = "Copyright (c) 2024-2026 Amir. All rights reserved."
    return core.dashboard_state

@app.get("/api/language")
async def get_language(request: Request):
    user_lang = request.cookies.get("user_lang", "en")
    if user_lang not in ["fa", "en", "ru", "zh"]:
        user_lang = "en"
    return {"language": user_lang}

@app.post("/api/language")
async def set_language(request: Request):
    try:
        body = await request.json()
        lang = body.get("language", "en")
    except Exception:
        lang = "en"
    if lang not in ["fa", "en", "ru", "zh"]:
        lang = "en"
    resp = JSONResponse({"status": "ok", "language": lang})
    resp.set_cookie("user_lang", lang, max_age=365*86400, samesite="lax")
    return resp

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# PasarGuard inbounds are numbered from here, NOT from the template inbound's port.
DEFAULT_INBOUND_BASE_PORT = 8070

# TLS ports Cloudflare will proxy (orange cloud). Anything else is rejected at
# the Cloudflare edge before it ever reaches the server.
CLOUDFLARE_TLS_PORTS = [2053, 2083, 2087, 2096, 8443, 443]

# PasarGuard core saves and node restarts can take minutes on busy panels.
# Anything short (httpx defaults to 5s) makes a successful injection look failed.
PASARGUARD_TIMEOUT = httpx.Timeout(connect=30.0, read=600.0, write=600.0, pool=600.0)
PASARGUARD_RESTART_TIMEOUT = httpx.Timeout(connect=30.0, read=900.0, write=900.0, pool=900.0)

DEFAULT_SETTINGS = {
    'max_instances': 20,
    'ping_interval': 30,
    'ram_limit_mb': 15,
    'bandwidth_limit_kb': 0,
    'worker_count': 0,
    'selected_countries': "",
    'host_country_override': "",
    'inbound_base_port': DEFAULT_INBOUND_BASE_PORT,
    'inbound_port_overrides': {},
    'inbound_port_strategy': "base",
    # 'country' lets Tor choose among every exit in the country using consensus
    # weights. 'fingerprints' pins the top relays (legacy, more brittle).
    'exit_node_mode': "country",
    # Pinning entry guards with StrictNodes can make a client unusable, so off.
    'pin_guards': False
}

def load_settings():
    """Read persisted settings from config.json, backfilled with defaults."""
    settings = dict(DEFAULT_SETTINGS)
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                stored = json.load(f)
            if isinstance(stored, dict):
                for key in DEFAULT_SETTINGS:
                    if key in stored and stored[key] is not None:
                        settings[key] = stored[key]
    except Exception as e:
        print(f"[settings] Failed to read {CONFIG_FILE}: {e}")
    return settings

def save_settings(settings):
    """Persist settings to config.json on disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    return settings

def normalize_country_list(raw):
    """Normalize a country selection into a clean, de-duplicated 'is,jp,nl' string."""
    if raw is None:
        return ""
    if isinstance(raw, (list, tuple, set)):
        parts = [str(c) for c in raw]
    else:
        parts = str(raw).replace("|", ",").replace(" ", ",").split(",")
        
    seen = []
    for p in parts:
        code = p.strip().lower()
        if len(code) == 2 and code.isalpha() and code not in seen:
            seen.append(code)
    return ",".join(seen)

def sanitize_port(value, fallback=None):
    """Coerce anything into a valid TCP port, or return the fallback."""
    try:
        port = int(str(value).strip())
    except (TypeError, ValueError):
        return fallback
    if 1 <= port <= 65535:
        return port
    return fallback

def normalize_port_overrides(raw):
    """Normalize manual per-location ports into { 'is': 8075, 'jp': 8090 }.

    Accepts a dict, a JSON string, or a list of {code, port} objects.
    Invalid codes/ports are dropped instead of breaking the whole injection.
    """
    result = {}
    if not raw:
        return result
        
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return result
            
    items = []
    if isinstance(raw, dict):
        items = list(raw.items())
    elif isinstance(raw, (list, tuple)):
        for entry in raw:
            if isinstance(entry, dict):
                items.append((entry.get('code') or entry.get('country'), entry.get('port')))
                
    for code, port in items:
        cc = str(code or "").strip().lower()
        p = sanitize_port(port)
        if len(cc) == 2 and cc.isalpha() and p:
            result[cc] = p
    return result

def build_inbound_port_plan(mapping, base_port=None, overrides=None, reserved_ports=None,
                           strategy="base", existing_ports=None):
    """Assign a dedicated PasarGuard inbound port to every active node.

    Rules:
      * A manual override for a location always wins and is used verbatim.
      * strategy 'keep' reuses the port an already-created host listens on, so a
        port the operator tuned inside PasarGuard is never clobbered.
      * strategy 'cloudflare' prefers TLS ports Cloudflare will proxy.
      * otherwise ports are numbered sequentially from base_port (default 8070).
      * Ports already taken by unrelated inbounds (e.g. the template's 443) are
        skipped for auto-assigned nodes.
      * The template inbound's own port is never inherited.

    Returns (plan, conflicts) where plan is { country_code: port } and conflicts
    lists manual overrides that collide with a reserved port or each other.
    """
    base = sanitize_port(base_port, DEFAULT_INBOUND_BASE_PORT) or DEFAULT_INBOUND_BASE_PORT
    manual = normalize_port_overrides(overrides)
    reserved = {p for p in (sanitize_port(x) for x in (reserved_ports or [])) if p}
    existing = {
        str(k).lower(): sanitize_port(v)
        for k, v in (existing_ports or {}).items() if sanitize_port(v)
    }
    strategy = (strategy or "base").strip().lower()
    
    # Deterministic order: follow the SOCKS port order of the running instances
    ordered = sorted(mapping.items(), key=lambda kv: sanitize_port(kv[0], 0) or 0)
    
    plan = {}
    conflicts = []
    taken = set(reserved)
    
    for _socks, country in ordered:
        cc = str(country).strip().lower()
        if cc not in manual or cc in plan:
            continue
        wanted = manual[cc]
        if wanted in reserved:
            conflicts.append(f"{cc.upper()} -> {wanted} (already used by another inbound)")
            continue
        if wanted in plan.values():
            conflicts.append(f"{cc.upper()} -> {wanted} (duplicate manual port)")
            continue
        plan[cc] = wanted
        taken.add(wanted)
        
    # 'keep' reuses whatever port the existing PasarGuard host already serves
    if strategy == "keep":
        for _socks, country in ordered:
            cc = str(country).strip().lower()
            if cc in plan:
                continue
            current = existing.get(cc)
            if current and current not in taken:
                plan[cc] = current
                taken.add(current)
                
    # 'cloudflare' fills from the TLS ports Cloudflare actually proxies
    if strategy == "cloudflare":
        for _socks, country in ordered:
            cc = str(country).strip().lower()
            if cc in plan:
                continue
            free = next((p for p in CLOUDFLARE_TLS_PORTS if p not in taken), None)
            if free is None:
                break
            plan[cc] = free
            taken.add(free)
        
    cursor = base
    for _socks, country in ordered:
        cc = str(country).strip().lower()
        if cc in plan:
            continue
        while cursor in taken and cursor < 65535:
            cursor += 1
        plan[cc] = cursor
        taken.add(cursor)
        cursor += 1
        
    return plan, conflicts

def resolve_outbound_address(req):
    """Address the Xray SOCKS outbound must dial to reach the Tor engine.

    Loopback is the only safe default: Xray and the Tor instances normally run on
    the same host, Tor's SOCKS ports are not meant to be exposed publicly, and a
    public address would be dropped by the server firewall. A remote address is
    used only when the operator explicitly opts in and supplies a host.
    """
    if not getattr(req, "remote_tor", False):
        return "127.0.0.1", None
        
    host = (getattr(req, "tor_host", None) or getattr(req, "server_ip", None) or "").strip()
    host = host.split("://")[-1].split("/")[0].strip()
    
    if not host or host in ("127.0.0.1", "localhost", "::1"):
        return "127.0.0.1", None
        
    warning = (
        f"Outbounds dial Tor at {host}. That host must expose the SOCKS ports "
        f"({', '.join(str(p) for p in sorted(set(get_active_instance_mapping().keys()))) or 'n/a'}) "
        "to the Xray server, otherwise every node fails with connection refused."
    )
    return host, warning

def open_firewall_port(port):
    """Best-effort local firewall opening. Never fatal, never blocking for long.

    Cloud-level firewalls and security groups are NOT covered here: those must be
    opened by the operator in their provider console.
    """
    port = sanitize_port(port)
    if not port:
        return False
        
    commands = []
    if platform.system() == 'Windows':
        commands.append(
            f'netsh advfirewall firewall add rule name="GerehGosha-{port}" '
            f'dir=in action=allow protocol=TCP localport={port}'
        )
    else:
        commands.append(f"ufw allow {port}/tcp")
        commands.append(f"firewall-cmd --add-port={port}/tcp")
        commands.append(f"iptables -I INPUT -p tcp --dport {port} -j ACCEPT")
        
    opened = False
    for cmd in commands:
        try:
            result = subprocess.run(
                cmd, shell=True, timeout=10,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                opened = True
        except Exception:
            continue
    return opened

class SettingsPayload(BaseModel):
    max_instances: int = None
    ping_interval: int = None
    ram_limit_mb: int = None
    bandwidth_limit_kb: int = None
    worker_count: int = None
    selected_countries: str = None
    host_country_override: str = None
    inbound_base_port: int = None
    inbound_port_overrides: dict = None
    inbound_port_strategy: str = None
    exit_node_mode: str = None
    pin_guards: bool = None

@app.get("/api/settings")
async def get_settings():
    return load_settings()

@app.post("/api/settings")
async def update_settings(payload: SettingsPayload):
    """Persist engine settings (including selected_countries) to config.json."""
    try:
        settings = load_settings()
        incoming = payload.dict(exclude_unset=True)
        
        for key in ('max_instances', 'ping_interval', 'ram_limit_mb', 'bandwidth_limit_kb', 'worker_count'):
            if incoming.get(key) is not None:
                settings[key] = int(incoming[key])
                
        if incoming.get('selected_countries') is not None:
            settings['selected_countries'] = normalize_country_list(incoming['selected_countries'])
            
        if incoming.get('host_country_override') is not None:
            settings['host_country_override'] = str(incoming['host_country_override']).strip().lower()
            
        if incoming.get('inbound_base_port') is not None:
            settings['inbound_base_port'] = sanitize_port(
                incoming['inbound_base_port'], DEFAULT_INBOUND_BASE_PORT
            )
            
        if incoming.get('inbound_port_overrides') is not None:
            settings['inbound_port_overrides'] = normalize_port_overrides(incoming['inbound_port_overrides'])
            
        if incoming.get('inbound_port_strategy') is not None:
            strategy = str(incoming['inbound_port_strategy']).strip().lower()
            settings['inbound_port_strategy'] = strategy if strategy in ('base', 'keep', 'cloudflare') else 'base'
            
        if incoming.get('exit_node_mode') is not None:
            mode = str(incoming['exit_node_mode']).strip().lower()
            settings['exit_node_mode'] = mode if mode in ('country', 'fingerprints') else 'country'
            
        if incoming.get('pin_guards') is not None:
            settings['pin_guards'] = bool(incoming['pin_guards'])
            
        save_settings(settings)
        
        selected = settings['selected_countries']
        count = len([c for c in selected.split(",") if c]) if selected else 0
        return {
            "status": "success",
            "message": f"Settings saved ({count} exit location(s) selected).",
            "settings": settings
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/scan_countries")
def scan_countries():
    """Discover every currently active Tor exit country without spawning instances.

    Declared as a sync endpoint so FastAPI runs this blocking network work in its
    threadpool instead of stalling the event loop.
    """
    try:
        countries, counts, source = core.scan_available_countries()
        
        if not countries:
            return {
                "status": "error",
                "message": "Unable to reach the Tor consensus. Check the server's internet connection and try again.",
                "countries": [],
                "country_details": []
            }
            
        country_details = []
        for code in countries:
            upper = code.upper()
            country_details.append({
                "code": code,
                "name": COUNTRY_MAP.get(upper, upper),
                "flag": get_emoji(upper),
                "relays": counts.get(code, 0)
            })
            
        return {
            "status": "success",
            "source": source,
            "total": len(countries),
            "selected_countries": load_settings().get('selected_countries', ""),
            "countries": countries,
            "country_details": country_details
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "countries": [], "country_details": []}

def get_auto_config():
    tier = core.HARDWARE_TIER
    if tier == 'ULTRA_LOW':
        return {
            'max_instances': 40,
            'ping_interval': 60,
            'ram_limit_mb': 5,
            'bandwidth_limit_kb': 0,
            'worker_count': 5,
            'selected_countries': ""
        }
    elif tier == 'LOW':
        return {
            'max_instances': 15,
            'ping_interval': 60,
            'ram_limit_mb': 15,
            'bandwidth_limit_kb': 0,
            'worker_count': 5,
            'selected_countries': ""
        }
    elif tier == 'MID':
        return {
            'max_instances': 40,
            'ping_interval': 30,
            'ram_limit_mb': 30,
            'bandwidth_limit_kb': 0,
            'worker_count': 0,
            'selected_countries': ""
        }
    else:
        return {
            'max_instances': 100,
            'ping_interval': 15,
            'ram_limit_mb': 50,
            'bandwidth_limit_kb': 0,
            'worker_count': 16,
            'selected_countries': ""
        }

class StartConfig(BaseModel):
    max_instances: int = None
    ping_interval: int = None
    ram_limit_mb: int = None
    bandwidth_limit_kb: int = None
    worker_count: int = None
    selected_countries: str = None
    host_country_override: str = None
    exit_node_mode: str = None
    pin_guards: bool = None

@app.post("/api/start")
async def start_network_api(config: StartConfig):
    try:
        stored = load_settings()
        auto = get_auto_config()
        
        max_c = config.max_instances or stored.get('max_instances') or auto['max_instances']
        ping_i = config.ping_interval or stored.get('ping_interval') or auto['ping_interval']
        ram_l = config.ram_limit_mb or stored.get('ram_limit_mb') or auto['ram_limit_mb']
        bw_l = config.bandwidth_limit_kb if config.bandwidth_limit_kb is not None else stored.get('bandwidth_limit_kb', auto['bandwidth_limit_kb'])
        workers = config.worker_count if config.worker_count is not None else stored.get('worker_count', 0)
        
        # Strict selection: whatever the request carries wins; otherwise fall back
        # to the persisted selection. Never silently widen the selection.
        if config.selected_countries is not None:
            selected = normalize_country_list(config.selected_countries)
        else:
            selected = normalize_country_list(stored.get('selected_countries', ""))
            
        host_override = config.host_country_override
        if host_override is None:
            host_override = stored.get('host_country_override', "")
        host_override = str(host_override).strip().lower()
        
        # Routing behaviour: request wins, then config.json, then the safe default
        exit_mode = config.exit_node_mode
        if exit_mode is None:
            exit_mode = stored.get('exit_node_mode', 'country')
        exit_mode = str(exit_mode).strip().lower()
        if exit_mode not in ('country', 'fingerprints'):
            exit_mode = 'country'
            
        pin_guards = config.pin_guards
        if pin_guards is None:
            pin_guards = bool(stored.get('pin_guards', False))
        pin_guards = bool(pin_guards)
        
        # Persist what we are actually starting with so a restart keeps the choice
        stored.update({
            'max_instances': int(max_c),
            'ping_interval': int(ping_i),
            'ram_limit_mb': int(ram_l),
            'bandwidth_limit_kb': int(bw_l or 0),
            'worker_count': int(workers or 0),
            'selected_countries': selected,
            'host_country_override': host_override,
            'exit_node_mode': exit_mode,
            'pin_guards': pin_guards
        })
        try:
            save_settings(stored)
        except Exception as e:
            print(f"[settings] Failed to persist start config: {e}")
        
        core.start_network(
            max_instances=int(max_c),
            ping_interval=int(ping_i),
            ram_limit_mb=int(ram_l),
            bandwidth_limit_kb=int(bw_l or 0),
            worker_count=int(workers or 0),
            selected_countries=selected,
            host_country_override=host_override,
            exit_node_mode=exit_mode,
            pin_guards=pin_guards
        )
        
        if selected:
            picked = [c for c in selected.split(",") if c]
            msg = f"Starting engine with {len(picked)} selected location(s): {', '.join(c.upper() for c in picked)}"
        else:
            msg = f"Starting engine in auto mode (top {int(max_c)} locations by relay count)..."
            
        return {"status": "success", "message": msg, "selected_countries": selected}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/stop")
async def stop_network():
    core.stop_all()
    return {"status": "success", "message": "Network stopped"}

class LifecycleRequest(BaseModel):
    action: str
    pasargard_url: str
    pasargard_token: str

class FetchCoresRequest(BaseModel):
    pasargard_url: str
    pasargard_token: str

class FetchInboundsRequest(BaseModel):
    pasargard_url: str
    pasargard_token: str
    core_id: str

class PasargardInjectRequest(BaseModel):
    pasargard_url: str
    pasargard_token: str
    core_id: str
    template_inbound_id: str
    # Legacy field. Ignored unless remote_tor is explicitly enabled, because the
    # Xray outbound must dial Tor over loopback when both run on the same box.
    server_ip: str = "127.0.0.1"
    # Set true ONLY when the Tor engine runs on a different machine than Xray.
    remote_tor: bool = False
    # Address of the Tor engine when remote_tor is true.
    tor_host: str = None
    # Inbound numbering starts here (default 8070). The template inbound's own
    # port is never reused.
    base_port: int = None
    # Manual per-location ports, e.g. {"is": 8075}. Applied verbatim.
    port_overrides: dict = None
    # base       -> number every node upward from base_port
    # keep       -> preserve the port an already-created host uses
    # cloudflare -> use Cloudflare-proxyable TLS ports first
    port_strategy: str = None

@app.post("/api/pasargard/cores")
async def fetch_cores_api(req: FetchCoresRequest):
    try:
        async with httpx.AsyncClient(timeout=PASARGUARD_TIMEOUT) as client:
            auth_header = {"Authorization": f"Bearer {req.pasargard_token.replace('Bearer ', '')}"}
            host_url = req.pasargard_url.rstrip('/')
            
            resp = await client.get(f"{host_url}/api/cores/simple", headers=auth_header)
            if not resp.is_success:
                return {"status": "error", "message": f"Failed to fetch cores: {resp.text}"}
                
            cores = [{"id": str(c["id"]), "setting_key": c["name"]} for c in resp.json().get("cores", [])]
            return {"status": "success", "cores": cores}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/pasargard/inbounds")
async def fetch_inbounds_api(req: FetchInboundsRequest):
    try:
        async with httpx.AsyncClient(timeout=PASARGUARD_TIMEOUT) as client:
            auth_header = {"Authorization": f"Bearer {req.pasargard_token.replace('Bearer ', '')}"}
            host_url = req.pasargard_url.rstrip('/')
            
            resp = await client.get(f"{host_url}/api/hosts", headers=auth_header)
            if not resp.is_success:
                return {"status": "error", "message": f"Failed to fetch inbounds: {resp.text}"}
                
            inbounds = []
            for host in resp.json():
                inbounds.append({
                    "id": str(host["id"]),
                    "remark": host.get("remark", f"Host {host['id']}"),
                    "port": host.get("port", 0)
                })
            return {"status": "success", "inbounds": inbounds}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_active_instance_mapping():
    """Return { "<socks_port>": "<country>" } for ONLY the currently active instances.

    Live engine state (core.instances) is authoritative. port_mapping.json is used
    as a fallback when the engine object list is empty (e.g. after an API reload).
    country_ports.json is deliberately NOT used as a source, because it is a
    persistent catalog of every country ever assigned a port and would inject
    locations the user never selected.
    """
    mapping = {}
    try:
        for inst in list(core.instances):
            mapping[str(inst.socks_port)] = inst.country
    except Exception as e:
        print(f"[inject] Failed reading live instances: {e}")
        
    if not mapping:
        try:
            if os.path.exists(core.PORT_MAPPING_FILE):
                with open(core.PORT_MAPPING_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                if isinstance(stored, dict):
                    mapping = {str(k): str(v) for k, v in stored.items() if k and v}
        except Exception as e:
            print(f"[inject] Failed reading port_mapping.json: {e}")
            
    return mapping

def resolve_fixed_socks_port(country, mapping_key=None):
    """Return the permanent Tor SOCKS port a location's outbound must terminate on.

    This is the fixed per-country port owned by the engine. Manual inbound ports
    never influence it: an operator can pin the Netherlands inbound to 8075 while
    its outbound still dials the Netherlands SOCKS port (e.g. 9052).

    Order of truth:
      1. the live engine instance for that country
      2. the SOCKS port recorded in port_mapping.json (the mapping key)
      3. country_ports.json, the persistent per-country catalog
    """
    code = str(country or "").strip().lower()
    
    try:
        for inst in list(core.instances):
            if str(inst.country).strip().lower() == code:
                port = sanitize_port(inst.socks_port)
                if port:
                    return port
    except Exception as e:
        print(f"[inject] Failed reading live SOCKS port for {code}: {e}")
        
    port = sanitize_port(mapping_key)
    if port:
        return port
        
    return sanitize_port(core.get_fixed_socks_port(code))

@app.get("/api/active_instances")
async def get_active_instances():
    """Expose exactly which selected instances are live and injectable.

    Each node carries two independent ports:
      * inbound_port - the PasarGuard inbound, auto-numbered or pinned by hand
      * socks_port   - the location's fixed Tor SOCKS port the outbound dials
    """
    mapping = get_active_instance_mapping()
    settings = load_settings()
    base_port = sanitize_port(settings.get('inbound_base_port'), DEFAULT_INBOUND_BASE_PORT)
    manual = normalize_port_overrides(settings.get('inbound_port_overrides'))
    strategy = str(settings.get('inbound_port_strategy') or 'base').strip().lower()
    plan, conflicts = build_inbound_port_plan(mapping, base_port, manual, strategy=strategy)
    
    nodes = []
    for mapping_key, country in mapping.items():
        code = str(country).lower()
        upper = code.upper()
        socks_port = resolve_fixed_socks_port(code, mapping_key)
        nodes.append({
            "port": socks_port,
            "socks_port": socks_port,
            "code": code,
            "name": COUNTRY_MAP.get(upper, upper),
            "flag": get_emoji(upper),
            "inbound_port": plan.get(code),
            "manual": code in manual
        })
    nodes.sort(key=lambda n: n["inbound_port"] or 0)
    return {
        "status": "success",
        "total": len(nodes),
        "base_port": base_port,
        "strategy": strategy,
        "cloudflare_ports": CLOUDFLARE_TLS_PORTS,
        "conflicts": conflicts,
        "nodes": nodes
    }

def probe_tcp(host, port, timeout=3.0):
    """Return True when a TCP connection to host:port is accepted."""
    port = sanitize_port(port)
    if not port:
        return False
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def probe_socks_exit(socks_port, timeout=12.0):
    """Send a real request through a Tor SOCKS port and report the exit country."""
    port = sanitize_port(socks_port)
    if not port:
        return False, None
    try:
        proxies = {
            'http': f'socks5h://127.0.0.1:{port}',
            'https': f'socks5h://127.0.0.1:{port}'
        }
        resp = requests.get(
            'https://1.1.1.1/cdn-cgi/trace', proxies=proxies, timeout=timeout
        )
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                if line.startswith('loc='):
                    return True, line.split('=')[1].strip().upper()
            return True, None
    except Exception:
        pass
    return False, None

def get_instance_rss_mb(country):
    """Resident memory of the Tor process serving a location, in MB."""
    try:
        import psutil
        for inst in list(core.instances):
            if str(inst.country).strip().lower() != str(country).strip().lower():
                continue
            proc = getattr(inst, 'process', None)
            if not proc or not getattr(proc, 'pid', None):
                return None
            return round(psutil.Process(proc.pid).memory_info().rss / (1024 * 1024), 1)
    except Exception:
        pass
    return None

class DiagnoseRequest(BaseModel):
    # Host clients dial (panel address). Leave blank to skip the inbound probe.
    panel_host: str = None
    # Test the SOCKS proxies end-to-end through the Tor network (slower).
    deep: bool = False

@app.post("/api/diagnose")
def diagnose_injection(req: DiagnoseRequest):
    """Report exactly where an injected node breaks: Tor side or panel side.

    For every active node this checks
      * the Tor SOCKS port accepts a local TCP connection
      * optionally, a real request through that SOCKS port and its exit country
      * whether the planned inbound port is listening on the panel host

    Declared sync so FastAPI runs the blocking probes in its threadpool.
    """
    mapping = get_active_instance_mapping()
    if not mapping:
        return {"status": "error", "message": "No active instances. Start the engine first.", "nodes": []}
        
    settings = load_settings()
    base_port = sanitize_port(settings.get('inbound_base_port'), DEFAULT_INBOUND_BASE_PORT)
    manual = normalize_port_overrides(settings.get('inbound_port_overrides'))
    strategy = str(settings.get('inbound_port_strategy') or 'base').strip().lower()
    plan, _conflicts = build_inbound_port_plan(mapping, base_port, manual, strategy=strategy)
    
    panel_host = (req.panel_host or "").strip()
    panel_host = panel_host.split("://")[-1].split("/")[0].split(":")[0].strip()
    
    nodes = []
    for mapping_key, country in sorted(mapping.items(), key=lambda kv: sanitize_port(kv[0], 0) or 0):
        code = str(country).lower()
        socks_port = resolve_fixed_socks_port(code, mapping_key)
        inbound_port = plan.get(code)
        
        socks_open = probe_tcp("127.0.0.1", socks_port)
        exit_ok, exit_country = (None, None)
        if req.deep and socks_open:
            exit_ok, exit_country = probe_socks_exit(socks_port)
            
        inbound_open = probe_tcp(panel_host, inbound_port) if panel_host else None
        
        nodes.append({
            "code": code,
            "name": COUNTRY_MAP.get(code.upper(), code.upper()),
            "socks_port": socks_port,
            "inbound_port": inbound_port,
            "socks_listening": socks_open,
            "tor_exit_ok": exit_ok,
            "tor_exit_country": exit_country,
            "inbound_reachable": inbound_open,
            "rss_mb": get_instance_rss_mb(code),
            "bootstrap_seconds": core.dashboard_state.get('metrics', {}).get('bootstrap_seconds', {}).get(code),
            "rotations": core.dashboard_state.get('metrics', {}).get('rotations', {}).get(code, 0)
        })
        
    problems = []
    dead_socks = [n["code"].upper() for n in nodes if not n["socks_listening"]]
    if dead_socks:
        problems.append(
            f"Tor SOCKS not listening for {', '.join(dead_socks)}. Xray cannot hand traffic to these nodes."
        )
    if panel_host:
        closed = [f"{n['code'].upper()}:{n['inbound_port']}" for n in nodes if n["inbound_reachable"] is False]
        if closed:
            problems.append(
                f"Inbound ports unreachable on {panel_host}: {', '.join(closed)}. "
                "Open them in the server AND cloud firewall, or switch to Cloudflare-safe ports."
            )
    non_cf = sorted({n["inbound_port"] for n in nodes if n["inbound_port"] not in CLOUDFLARE_TLS_PORTS})
    if non_cf:
        problems.append(
            f"Ports {', '.join(str(p) for p in non_cf)} are not proxyable by Cloudflare. "
            "With the orange cloud enabled clients cannot reach them; use DNS-only or the Cloudflare port preset."
        )
    if req.deep:
        broken = [n["code"].upper() for n in nodes if n["socks_listening"] and n["tor_exit_ok"] is False]
        if broken:
            problems.append(f"SOCKS port answers but no traffic exits Tor for {', '.join(broken)}.")
            
    metrics = core.dashboard_state.get('metrics', {})
    slow_boots = [
        f"{c.upper()} {v}s" for c, v in (metrics.get('bootstrap_seconds') or {}).items()
        if isinstance(v, (int, float)) and v > 45
    ]
    if slow_boots:
        problems.append(
            f"Slow bootstrap: {', '.join(slow_boots)}. Guard state is reused after the first run, "
            "so repeated slowness points at host network quality."
        )
    total_rss = sum(n["rss_mb"] for n in nodes if n.get("rss_mb"))
        
    return {
        "status": "success",
        "panel_host": panel_host or None,
        "strategy": strategy,
        "exit_mode": metrics.get('exit_mode'),
        "pinned_guards": metrics.get('pinned_guards', 0),
        "total_rss_mb": round(total_rss, 1) if total_rss else None,
        "sleep_events": metrics.get('sleep_events', {}),
        "bootstrap_failures": metrics.get('bootstrap_failures', {}),
        "problems": problems,
        "nodes": nodes
    }

@app.post("/api/inject_pasargard")
async def inject_pasargard(req: PasargardInjectRequest):
    try:
        # ONLY the currently active, user-selected instances get injected.
        mapping = get_active_instance_mapping()
        
        if not mapping:
            return {"status": "error", "message": "No active instances found. Select your locations and start the engine first."}
            
        # Resolve the inbound numbering: request wins, then config.json, then 8070.
        settings = load_settings()
        base_port = sanitize_port(
            req.base_port if req.base_port is not None else settings.get('inbound_base_port'),
            DEFAULT_INBOUND_BASE_PORT
        )
        manual_ports = normalize_port_overrides(
            req.port_overrides if req.port_overrides is not None else settings.get('inbound_port_overrides')
        )
        strategy = str(
            req.port_strategy if req.port_strategy is not None else settings.get('inbound_port_strategy') or 'base'
        ).strip().lower()
        if strategy not in ('base', 'keep', 'cloudflare'):
            strategy = 'base'
        
        # Xray must dial Tor over loopback unless the operator explicitly opted
        # into a remote Tor host. A public address here breaks every node.
        server_ip, remote_warning = resolve_outbound_address(req)
        warnings = [remote_warning] if remote_warning else []
        
        # Remember the numbering so re-injections stay stable
        try:
            settings['inbound_base_port'] = base_port
            settings['inbound_port_overrides'] = manual_ports
            settings['inbound_port_strategy'] = strategy
            save_settings(settings)
        except Exception as e:
            print(f"[inject] Failed to persist port plan: {e}")
        
        async with httpx.AsyncClient(timeout=PASARGUARD_TIMEOUT) as client:
            auth_header = {"Authorization": f"Bearer {req.pasargard_token.replace('Bearer ', '')}"}
            host_url = req.pasargard_url.rstrip('/')
            
            # 1. Fetch Core Config
            core_resp = await client.get(f"{host_url}/api/core/{req.core_id}", headers=auth_header)
            if not core_resp.is_success:
                return {"status": "error", "message": f"Failed to fetch Core {req.core_id}: {core_resp.text}"}
            
            core_data = core_resp.json()
            xray_config = core_data.get("config", {})
            
            if "inbounds" not in xray_config: xray_config["inbounds"] = []
            if "outbounds" not in xray_config: xray_config["outbounds"] = []
            if "routing" not in xray_config: xray_config["routing"] = {"rules": []}
            if "rules" not in xray_config["routing"]: xray_config["routing"]["rules"] = []
            
            # STRIP PREVIOUS INJECTIONS TO PREVENT DUPLICATES
            xray_config["inbounds"] = [i for i in xray_config.get("inbounds", []) if not (i.get("tag", "").startswith("grpA-in-"))]
            xray_config["outbounds"] = [o for o in xray_config.get("outbounds", []) if not (o.get("tag", "").startswith("grpA-out-"))]
            xray_config["routing"]["rules"] = [
                r for r in xray_config["routing"]["rules"] 
                if not (
                    (isinstance(r.get("inboundTag"), list) and any(t.startswith("grpA-in-") for t in r.get("inboundTag"))) or 
                    (isinstance(r.get("outboundTag"), str) and r.get("outboundTag", "").startswith("grpA-out-"))
                )
            ]
            
            existing_hosts = {}
            try:
                hosts_resp = await client.get(f"{host_url}/api/hosts", headers=auth_header)
                if hosts_resp.status_code == 200:
                    for old_h in hosts_resp.json():
                        tag = old_h.get("inbound_tag", "")
                        if tag.startswith("grpA-in-"):
                            # Tag format: grpA-in-country-uid
                            parts = tag.split("-")
                            if len(parts) >= 3:
                                country_part = parts[2].lower()
                                existing_hosts[country_part] = old_h
            except Exception as e:
                pass

            
            # 2. Fetch Template Host
            host_resp = await client.get(f"{host_url}/api/host/{req.template_inbound_id}", headers=auth_header)
            if not host_resp.is_success:
                return {"status": "error", "message": f"Failed to fetch Host {req.template_inbound_id}: {host_resp.text}"}
                
            template_host = host_resp.json()
            template_inbound_tag = template_host.get("inbound_tag")
            if not template_inbound_tag:
                return {"status": "error", "message": "Template host has no inbound_tag."}
                
            template_inbound = next((inb for inb in xray_config["inbounds"] if inb.get("tag") == template_inbound_tag), None)
            if not template_inbound:
                return {"status": "error", "message": "Template inbound tag not found in core config."}
                
            # The template only donates protocol/security settings. Its port is
            # explicitly discarded so a 443 template can never leak into the nodes.
            template_blueprint = copy.deepcopy(template_inbound)
            template_blueprint.pop("port", None)
            with open("tor_template.json", "w") as f:
                json.dump(template_blueprint, f)
            
            # Ports held by every inbound that is NOT ours (including the template's 443)
            reserved_ports = {
                p for p in (sanitize_port(inb.get("port")) for inb in xray_config["inbounds"]) if p
            }
            
            # The fixed Tor SOCKS port of every active location. Inbounds must
            # never land on one of these, since Tor already owns them locally.
            socks_in_use = {}
            for mapping_key, country in mapping.items():
                cc = str(country).lower()
                fixed = resolve_fixed_socks_port(cc, mapping_key)
                if fixed:
                    socks_in_use[fixed] = cc
                    
            # A manual inbound port hitting a SOCKS port is a hard error: we must
            # not silently move a port the operator explicitly asked for.
            manual_socks_clashes = [
                f"{cc.upper()} inbound {port} is the fixed SOCKS port of {socks_in_use[port].upper()}"
                for cc, port in manual_ports.items() if port in socks_in_use
            ]
            if manual_socks_clashes:
                return {
                    "status": "error",
                    "message": "Manual inbound port collides with a Tor SOCKS port: " + "; ".join(manual_socks_clashes)
                }
            
            # Ports the already-created hosts serve today. Used by the 'keep'
            # strategy so a port the operator tuned inside PasarGuard survives.
            existing_ports = {
                cc: sanitize_port(h.get("port"))
                for cc, h in existing_hosts.items() if sanitize_port(h.get("port"))
            }
            
            port_plan, port_conflicts = build_inbound_port_plan(
                mapping, base_port, manual_ports, reserved_ports | set(socks_in_use),
                strategy=strategy, existing_ports=existing_ports
            )
            if port_conflicts:
                return {
                    "status": "error",
                    "message": "Manual port conflict: " + "; ".join(port_conflicts)
                }
                
            # Invariant guard: auto-numbering already skips SOCKS ports
            socks_clashes = [
                f"{cc.upper()} inbound {port} is the SOCKS port of {socks_in_use[port].upper()}"
                for cc, port in port_plan.items() if port in socks_in_use
            ]
            if socks_clashes:
                return {
                    "status": "error",
                    "message": "Inbound port collides with a Tor SOCKS port: " + "; ".join(socks_clashes)
                }
            
            host_payloads = []
            hosts_to_update = []
            assigned = []
            skipped = []
            opened_ports = []
            
            for mapping_key, country in sorted(mapping.items(), key=lambda kv: sanitize_port(kv[0], 0) or 0):
                country_lower = str(country).lower()
                existing_host = existing_hosts.get(country_lower)
                
                # Inbound: the planned port (auto-numbered or manually pinned).
                # It never comes from the template inbound or a stale host.
                this_port = port_plan.get(country_lower)
                if not this_port:
                    continue
                    
                # Outbound: the location's FIXED Tor SOCKS port. Completely
                # independent from the inbound port the operator chose.
                outbound_socks_port = resolve_fixed_socks_port(country_lower, mapping_key)
                if not outbound_socks_port:
                    skipped.append(country_lower.upper())
                    print(f"[inject] Skipping {country_lower}: no fixed SOCKS port found for this location.")
                    continue
                
                if existing_host:
                    cloned_tag = existing_host.get("inbound_tag")
                    # Extract uid from existing tag if possible
                    parts = cloned_tag.split("-")
                    uid = parts[3] if len(parts) >= 4 else uuid.uuid4().hex[:6]
                    outbound_tag = f"grpA-out-{country_lower}-{uid}"
                    new_uuid = existing_host.get("uuid", str(uuid.uuid4()))
                    is_new = False
                    
                    # Re-point the existing host at the planned port if it drifted
                    if sanitize_port(existing_host.get("port")) != this_port:
                        updated_host = copy.deepcopy(existing_host)
                        updated_host["port"] = this_port
                        hosts_to_update.append(updated_host)
                else:
                    uid = uuid.uuid4().hex[:6]
                    outbound_tag = f"grpA-out-{country_lower}-{uid}"
                    cloned_tag = f"grpA-in-{country_lower}-{uid}"
                    new_uuid = str(uuid.uuid4())
                    is_new = True

                # Clone Inbound for Core
                new_inbound = copy.deepcopy(template_blueprint)
                new_inbound["tag"] = cloned_tag
                new_inbound["port"] = int(this_port)
                
                # Auto-open the port on the local firewall (ufw / firewalld /
                # iptables / Windows). Cloud firewalls are NOT covered.
                if open_firewall_port(this_port):
                    opened_ports.append(int(this_port))
                
                xray_config["inbounds"].append(new_inbound)
                
                # Add SOCKS Outbound -> always the location's fixed Tor port
                xray_config["outbounds"].append({
                    "tag": outbound_tag,
                    "protocol": "socks",
                    "settings": {"servers": [{"address": server_ip, "port": int(outbound_socks_port)}]}
                })
                
                # Add Routing Rule
                xray_config["routing"]["rules"].insert(0, {
                    "type": "field",
                    "inboundTag": [cloned_tag],
                    "outboundTag": outbound_tag
                })
                
                new_host_payload = None
                if is_new:
                    # Prepare Host Payload for API
                    full_country_name = COUNTRY_MAP.get(country_lower.upper(), country_lower.upper())
                    flag = get_emoji(country_lower.upper())
                    new_remark = f"{full_country_name} {flag}"
                    new_host_payload = copy.deepcopy(template_host)
                    new_host_payload.pop("id", None)
                    new_host_payload["uuid"] = new_uuid
                    new_host_payload.pop("created_at", None)
                    new_host_payload.pop("updated_at", None)
                    new_host_payload["remark"] = new_remark
                    new_host_payload["inbound_tag"] = cloned_tag
                    new_host_payload["port"] = int(this_port)
                    host_payloads.append(new_host_payload)
                
                # Update Xray config to accept this specific UUID
                if "settings" in new_inbound and "clients" in new_inbound["settings"] and len(new_inbound["settings"]["clients"]) > 0:
                    client_template = copy.deepcopy(new_inbound["settings"]["clients"][0])
                    client_template["id"] = new_uuid
                    client_template["email"] = existing_host.get("email", new_uuid) if not is_new else new_host_payload.get("email", new_uuid)
                    new_inbound["settings"]["clients"] = [client_template]
                    
                assigned.append({
                    "code": country_lower,
                    "name": COUNTRY_MAP.get(country_lower.upper(), country_lower.upper()),
                    "inbound_port": int(this_port),
                    "socks_port": int(outbound_socks_port),
                    "manual": country_lower in manual_ports
                })
                
            if not assigned:
                return {"status": "error", "message": "No injectable node had a valid SOCKS port. Restart the engine and try again."}
                
            # 3. Save Core Config FIRST
            core_data["config"] = xray_config
            update_core_resp = await client.put(
                f"{host_url}/api/core/{req.core_id}?restart_nodes=false",
                headers=auth_header, json=core_data
            )
            if not update_core_resp.is_success:
                return {"status": "error", "message": f"Failed to save core config: {update_core_resp.text}"}
                
            # 4. Create Hosts
            for payload in host_payloads:
                c_resp = await client.post(f"{host_url}/api/host/", headers=auth_header, json=payload)
                if not c_resp.is_success:
                    print(f"Failed to create host {payload.get('remark')}: {c_resp.text}")
                    
            # 5. Re-point existing hosts whose port no longer matches the plan
            repointed = 0
            for payload in hosts_to_update:
                try:
                    u_resp = await client.put(
                        f"{host_url}/api/host/{payload['id']}", headers=auth_header, json=payload
                    )
                    if u_resp.is_success:
                        repointed += 1
                    else:
                        print(f"Failed to update host {payload.get('remark')}: {u_resp.text}")
                except Exception as e:
                    print(f"Failed to update host {payload.get('remark')}: {e}")
                    
            # Restart nodes finally. A slow restart must not be reported as a
            # failed injection, because the config is already saved at this point.
            restart_note = ""
            try:
                await client.put(
                    f"{host_url}/api/core/{req.core_id}?restart_nodes=true",
                    headers=auth_header, json=core_data, timeout=PASARGUARD_RESTART_TIMEOUT
                )
            except Exception as e:
                restart_note = " Node restart is still finishing in the background."
                print(f"[inject] Node restart did not confirm in time: {e}")

            ports_preview = ", ".join(
                f"{a['code'].upper()} in:{a['inbound_port']}->socks:{a['socks_port']}" for a in assigned
            )
            
            # Surface reachability risks instead of letting the operator guess
            non_cf = sorted({a['inbound_port'] for a in assigned if a['inbound_port'] not in CLOUDFLARE_TLS_PORTS})
            if non_cf:
                warnings.append(
                    f"Ports {', '.join(str(p) for p in non_cf)} are not proxyable by Cloudflare. "
                    "With the orange cloud on, clients never reach them: switch the DNS record to "
                    "DNS-only or pick the Cloudflare port strategy."
                )
            listen_addr = template_blueprint.get("listen")
            if listen_addr and str(listen_addr) not in ("0.0.0.0", "::"):
                warnings.append(
                    f"The template inbound listens on {listen_addr}, so the cloned inbounds only accept "
                    "traffic from that address. Clients on the internet cannot connect."
                )
            if opened_ports:
                warnings.append(
                    f"Opened {len(opened_ports)} port(s) in the local firewall. "
                    "Cloud firewalls and security groups still have to be opened manually."
                )
            
            message = (
                f"Injected {len(assigned)} Group A nodes ({ports_preview})."
                f" Outbounds dial Tor at {server_ip}."
                f"{f' Re-pointed {repointed} existing host(s).' if repointed else ''}"
                f"{f' Skipped (no SOCKS port): {chr(44).join(skipped)}.' if skipped else ''}"
                f"{restart_note}"
            )
            return {
                "status": "success",
                "message": message,
                "base_port": base_port,
                "strategy": strategy,
                "outbound_address": server_ip,
                "warnings": warnings,
                "created": len(host_payloads),
                "repointed": repointed,
                "skipped": skipped,
                "nodes": assigned
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/lifecycle")
async def handle_lifecycle(req: LifecycleRequest):
    try:
        async with httpx.AsyncClient(timeout=PASARGUARD_TIMEOUT) as client:
            auth_header = {"Authorization": f"Bearer {req.pasargard_token.replace('Bearer ', '')}"}
            host_url = req.pasargard_url.rstrip('/')
            
            # Fetch all hosts
            list_resp = await client.get(f"{host_url}/api/hosts", headers=auth_header)
            if not list_resp.is_success:
                return {"status": "error", "message": f"Failed to fetch hosts: {list_resp.text}"}
                
            hosts = list_resp.json()
            tor_hosts = [h for h in hosts if h.get("inbound_tag", "").startswith("grpA-in-")]
            
            if req.action in ['enable', 'disable']:
                count = 0
                for h in tor_hosts:
                    h["enable"] = (req.action == 'enable')
                    r = await client.put(f"{host_url}/api/host/{h['id']}", headers=auth_header, json=h)
                    if r.is_success: count += 1
                
                template_inb = None
                if req.action == 'enable' and os.path.exists("tor_template.json"):
                    with open("tor_template.json", "r") as f:
                        template_inb = json.load(f)
                        
                # Restart all cores and modify inbounds
                cores_resp = await client.get(f"{host_url}/api/cores/simple", headers=auth_header)
                if cores_resp.is_success:
                    for core in cores_resp.json().get("cores", []):
                        c_id = core["id"]
                        cd_resp = await client.get(f"{host_url}/api/core/{c_id}", headers=auth_header)
                        if cd_resp.is_success:
                            c_data = cd_resp.json()
                            xc = c_data.get("config", {})
                            inbounds = xc.get("inbounds", [])
                            
                            for h in tor_hosts:
                                tag = h.get("inbound_tag")
                                if req.action == 'disable':
                                    inbounds = [i for i in inbounds if i.get("tag") != tag]
                                elif req.action == 'enable' and template_inb:
                                    if not any(i.get("tag") == tag for i in inbounds):
                                        # Re-attach on the host's own port. Never fall
                                        # back to the template inbound's port.
                                        host_port = sanitize_port(h.get("port"))
                                        if not host_port:
                                            print(f"Skipping re-enable of {tag}: host has no valid port.")
                                            continue
                                        new_inb = copy.deepcopy(template_inb)
                                        new_inb["tag"] = tag
                                        new_inb["port"] = host_port
                                        inbounds.append(new_inb)
                                        
                            xc["inbounds"] = inbounds
                            c_data["config"] = xc
                            await client.put(
                                f"{host_url}/api/core/{c_id}?restart_nodes=true",
                                headers=auth_header, json=c_data, timeout=PASARGUARD_RESTART_TIMEOUT
                            )
                            
                return {"status": "success", "message": f"Successfully {req.action}d {count} Tor nodes and restarted core."}
                
            elif req.action == 'cleanup':
                count = 0
                for h in tor_hosts:
                    r = await client.delete(f"{host_url}/api/host/{h['id']}", headers=auth_header)
                    if r.is_success: count += 1
                    
                # Clean Core Config for ALL cores
                cores_resp = await client.get(f"{host_url}/api/cores/simple", headers=auth_header)
                for core in cores_resp.json().get("cores", []):
                    c_id = core["id"]
                    cd_resp = await client.get(f"{host_url}/api/core/{c_id}", headers=auth_header)
                    c_data = cd_resp.json()
                    xc = c_data.get("config", {})
                    
                    xc["inbounds"] = [i for i in xc.get("inbounds", []) if not i.get("tag", "").startswith("grpA-in-")]
                    xc["outbounds"] = [o for o in xc.get("outbounds", []) if not o.get("tag", "").startswith("grpA-out-")]
                    if "routing" in xc and "rules" in xc["routing"]:
                        xc["routing"]["rules"] = [r for r in xc["routing"]["rules"] if not r.get("outboundTag", "").startswith("grpA-out-")]
                        
                    await client.put(
                        f"{host_url}/api/core/{c_id}?restart_nodes=true",
                        headers=auth_header, json=c_data, timeout=PASARGUARD_RESTART_TIMEOUT
                    )
                
                return {"status": "success", "message": f"Successfully deleted {count} Group A nodes and cleaned core configs."}
                
            return {"status": "error", "message": "Unknown action."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=54322)
