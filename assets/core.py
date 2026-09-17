# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Core Traffic Routing & Multi-Instance Manager
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

import os
import time
import signal
import threading
import logging
import requests
import stem.process
from stem.control import Controller
from stem import Signal
import shutil
import platform
import json
import re
import psutil
import subprocess
import random
import socket
import socks
import atexit

socket.setdefaulttimeout(20)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Setup File Logging ONLY (No console spam)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(BASE_DIR, "manager_logs.txt"), mode='a', encoding='utf-8')]
)
logger = logging.getLogger("TorManager")
logging.getLogger('stem').setLevel(logging.WARNING)

TEST_URL = "https://1.1.1.1/cdn-cgi/trace"
SPEED_TEST_URL = "https://speed.cloudflare.com/__down?bytes=100000" # 100KB payload
TIMEOUT = 15

# Rotate a circuit once its latency trend crosses this. 8s was far past any
# usable threshold, so degraded exits were effectively never replaced.
LATENCY_THRESHOLD = 2.5
SPEED_THRESHOLD_KBS = 5.0
PORT_LOCK = threading.Lock()

# How long Tor may spend building a circuit before abandoning the attempt.
# A real three-hop path with DH handshakes needs well over 5s; Tor's own
# default is 60s. These stay below BOOTSTRAP_WALL so a slow-but-working
# circuit is not killed by our own bootstrap deadline.
CIRCUIT_BUILD_TIMEOUT = {'ULTRA_LOW': 30, 'LOW': 25, 'MID': 20, 'HIGH': 20}
BOOTSTRAP_WALL = {'ULTRA_LOW': 120, 'LOW': 90, 'MID': 75, 'HIGH': 75}

# Max age at which a circuit still accepts NEW streams. 24h pinned users to
# degraded exits; 10min would churn their exit IP constantly.
MAX_CIRCUIT_DIRTINESS = 3600

# How long a stream waits before Tor retries it on a fresh circuit. The old
# 300s turned a dead exit into a five-minute hang for the user.
CIRCUIT_STREAM_TIMEOUT = 20

# Tor refuses values below 256 MB and silently raises them, so anything
# smaller is a no-op that only makes the config lie about the real ceiling.
MIN_MAX_MEM_IN_QUEUES_MB = 256

# Concurrent health checks. 2 meant a 60-node sweep took minutes, so dead
# nodes stayed advertised long after they died.
PING_CONCURRENCY = {'ULTRA_LOW': 3, 'LOW': 6, 'MID': 10, 'HIGH': 16}

NEXT_SOCKS_PORT = 9050
NEXT_CONTROL_PORT = 10050
G_STANDBY_POOL = []
G_COUNTRY_FINGERPRINTS = {}
G_TOR_CMD = "tor"

# 'country'      -> ExitNodes {cc}: every exit in the country, weighted by Tor
#                   itself. No dead-node cliff, country still guaranteed.
# 'fingerprints' -> pin the top relays by consensus weight (legacy behaviour).
G_EXIT_NODE_MODE = "country"
# Pinning EntryNodes together with StrictNodes can make a client unusable if
# those guards are unreachable, so guard pinning is opt-in.
G_PIN_GUARDS = False

# Quality gate for exit relays. Slow or churn-prone relays are exactly what
# turned a pinned exit set into a dead end.
REQUIRED_EXIT_FLAGS = ('Exit', 'Fast', 'Stable', 'Valid', 'Running')

COUNTRY_PORTS_FILE = os.path.join(BASE_DIR, "country_ports.json")
PORT_MAPPING_FILE = os.path.join(BASE_DIR, "port_mapping.json")

def get_geoip_paths():
    """Locate geoip and geoip6 files across Windows and Linux."""
    candidates = [
        os.path.join(BASE_DIR, "data"),
        os.path.join(os.getcwd(), "data"),
        os.path.join(BASE_DIR, "Tor"),
        os.path.join(BASE_DIR, "tor"),
        os.path.join(os.getcwd(), "Tor"),
        os.path.join(os.getcwd(), "tor"),
        "/usr/share/tor",
        "/var/lib/tor"
    ]
    for c in candidates:
        g = os.path.join(c, "geoip")
        g6 = os.path.join(c, "geoip6")
        if os.path.isfile(g) and os.path.isfile(g6):
            if platform.system() == 'Windows':
                return os.path.normpath(g), os.path.normpath(g6)
            return g.replace('\\', '/'), g6.replace('\\', '/')
    return None, None

def ensure_windows_tor():
    """Automated Tor Expert Bundle download & extract for Windows if tor.exe is missing."""
    target_dir = os.path.join(BASE_DIR, "Tor")
    target_exe = os.path.join(target_dir, "tor.exe")
    if os.path.isfile(target_exe):
        return target_exe

    os.makedirs(target_dir, exist_ok=True)
    logger.info("Tor binary not found on Windows. Downloading Tor Expert Bundle...")
    dashboard_state['discovery_msg'] = "Downloading Tor Expert Bundle for Windows..."

    bundle_urls = [
        "https://dist.torproject.org/torbrowser/15.0.17/tor-expert-bundle-windows-x86_64-15.0.17.tar.gz",
        "https://archive.torproject.org/tor-package-archive/torbrowser/15.0.17/tor-expert-bundle-windows-x86_64-15.0.17.tar.gz"
    ]
    archive_path = os.path.join(BASE_DIR, "tor_bundle.tar.gz")

    import urllib.request
    import tarfile

    for url in bundle_urls:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=45) as resp, open(archive_path, 'wb') as out_f:
                shutil.copyfileobj(resp, out_f)

            if os.path.isfile(archive_path) and os.path.getsize(archive_path) > 100000:
                with tarfile.open(archive_path, "r:gz") as tar:
                    tar.extractall(path=BASE_DIR)
                try:
                    os.remove(archive_path)
                except Exception:
                    pass
                if os.path.isfile(target_exe):
                    logger.info(f"Tor successfully installed to {target_exe}")
                    return target_exe
                alt_exe = os.path.join(BASE_DIR, "tor", "tor.exe")
                if os.path.isfile(alt_exe):
                    return alt_exe
        except Exception as e:
            logger.warning(f"Failed download from {url}: {e}")
            if os.path.exists(archive_path):
                try:
                    os.remove(archive_path)
                except Exception:
                    pass

    return None

def resolve_tor_cmd():
    """Intelligently resolves Tor executable path across Windows and Linux."""
    which_cmd = shutil.which("tor.exe" if platform.system() == 'Windows' else "tor")
    if which_cmd:
        return which_cmd

    search_dirs = [
        BASE_DIR,
        os.path.join(BASE_DIR, "Tor"),
        os.path.join(BASE_DIR, "tor"),
        os.getcwd(),
        os.path.join(os.getcwd(), "Tor"),
        os.path.join(os.getcwd(), "tor"),
        os.path.join(os.getcwd(), "assets"),
        os.path.join(os.getcwd(), "assets", "Tor"),
        os.path.join(os.getcwd(), "assets", "tor"),
        os.path.join(os.getcwd(), "pasarguard-tor"),
        os.path.join(os.getcwd(), "pasarguard-tor", "Tor"),
        os.path.join(os.getcwd(), "pasarguard-tor", "tor")
    ]

    if platform.system() == 'Windows':
        for pf in [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"), os.environ.get("LOCALAPPDATA")]:
            if pf:
                search_dirs.append(os.path.join(pf, "Tor Browser", "Browser", "TorBrowser", "Tor"))
                search_dirs.append(os.path.join(pf, "Tor"))

        for d in search_dirs:
            exe = os.path.join(d, "tor.exe")
            if os.path.isfile(exe):
                return exe

        auto_tor = ensure_windows_tor()
        if auto_tor and os.path.isfile(auto_tor):
            return auto_tor
        return "tor.exe"
    else:
        for d in search_dirs + ["/usr/bin", "/usr/local/bin"]:
            binary = os.path.join(d, "tor")
            if os.path.isfile(binary):
                return binary
        return "tor"

def get_port_for_country(country_code):
    mapping = {}
    if os.path.exists(COUNTRY_PORTS_FILE):
        try:
            with open(COUNTRY_PORTS_FILE, "r") as f:
                mapping = json.load(f)
        except:
            pass
            
    if country_code in mapping:
        return mapping[country_code]['socks'], mapping[country_code]['control']
        
    used_socks = [v['socks'] for v in mapping.values()]
    used_control = [v['control'] for v in mapping.values()]
    
    new_socks = max(used_socks) + 1 if used_socks else 9050
    new_control = max(used_control) + 1 if used_control else 10050
    
    while new_socks in used_socks:
        new_socks += 1
    while new_control in used_control:
        new_control += 1
        
    mapping[country_code] = {'socks': new_socks, 'control': new_control}
    
    try:
        with open(COUNTRY_PORTS_FILE, "w") as f:
            json.dump(mapping, f, indent=4)
    except:
        pass
        
    return new_socks, new_control

def load_country_ports():
    """Return the persistent { country: {socks, control} } port catalog."""
    if os.path.exists(COUNTRY_PORTS_FILE):
        try:
            with open(COUNTRY_PORTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}

def get_fixed_socks_port(country_code):
    """Read-only lookup of the SOCKS port permanently assigned to a country.

    Outbounds must always terminate on this port. Unlike get_port_for_country()
    this never allocates a new port, so calling it cannot shift the catalog.
    """
    if not country_code:
        return None
    entry = load_country_ports().get(str(country_code).strip().lower())
    if isinstance(entry, dict):
        try:
            return int(entry.get('socks'))
        except (TypeError, ValueError):
            return None
    return None

def sync_port_mapping():
    """Persist port_mapping.json containing ONLY the currently spawned/active instances.

    Format: { "<socks_port>": "<country_code>" }
    This file is the single source of truth for PasarGuard injection, so it must
    never contain countries that are not actually running right now.
    """
    mapping = {}
    try:
        for inst in list(instances):
            mapping[str(inst.socks_port)] = inst.country
        with open(PORT_MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=4)
        logger.info(f"Synced port_mapping.json with {len(mapping)} active instances: {','.join(mapping.values())}")
    except Exception as e:
        logger.error(f"Failed to sync port_mapping.json: {e}")
    return mapping

def spawn_country(country_code):
    global instances
    
    socks_port, control_port = get_port_for_country(country_code)
    
    data_dir = os.path.join(BASE_DIR, 'tor_data', f'data_{country_code}')
    fps = G_COUNTRY_FINGERPRINTS.get(country_code, [])
    
    instance = TorInstance(country_code, socks_port, control_port, data_dir, G_TOR_CMD, fps)
    
    with QUEUE_LOCK:
        instances.append(instance)
        
    # Keep port_mapping.json strictly in sync with what is actually spawned
    sync_port_mapping()
        
    threading.Thread(target=instance.start, daemon=True).start()
    
    stagger_delay = 1
    if HARDWARE_TIER == 'ULTRA_LOW':
        stagger_delay = 5
    elif HARDWARE_TIER == 'LOW':
        stagger_delay = 2
    time.sleep(stagger_delay) # Staggered Bootstrapping delay

def detect_hardware_tier():
    try:
        ram_gb = psutil.virtual_memory().total / (1024**3)
        cores = psutil.cpu_count(logical=True) or 2
    except:
        ram_gb = 4.0
        cores = 2
        
    tier = 'HIGH'
    if ram_gb < 2.5 or cores <= 1:
        tier = 'ULTRA_LOW'
    elif ram_gb < 6.0 or cores <= 2:
        tier = 'LOW'
    elif ram_gb < 12.0 or cores <= 4:
        tier = 'MID'
        
    return tier, cores, ram_gb

HARDWARE_TIER, CPU_CORES, RAM_GB = detect_hardware_tier()

# Health checks used to run 2-at-a-time, so a large fleet took minutes per sweep
PING_SEMAPHORE = threading.Semaphore(PING_CONCURRENCY.get(HARDWARE_TIER, 8))

# Global variables
instances = []
dashboard_state = {
    'status': 'idle',
    'phase': 'idle',
    'discovery_progress': 0,
    'discovery_msg': 'Engine is idle. Select your exit locations and press Start Engine.',
    'instances': {},
    'ping_history': {},
    # Instrumentation so tuning changes can be measured instead of guessed at
    'metrics': {
        'bootstrap_seconds': {},
        'bootstrap_failures': {},
        'sleep_events': {},
        'rotations': {},
        'exit_mode': G_EXIT_NODE_MODE,
        'pinned_guards': 0
    }
}

def record_metric(bucket, country, value=None):
    """Track bootstrap times, sleep events and rotations per location."""
    try:
        store = dashboard_state.setdefault('metrics', {}).setdefault(bucket, {})
        if value is None:
            store[country] = store.get(country, 0) + 1
        else:
            store[country] = value
    except Exception:
        pass

G_STANDBY_POOL = {}
# Reentrant: spawn_country() acquires this lock and is itself called from
# sections (e.g. Live Reload) that already hold it.
QUEUE_LOCK = threading.RLock()

G_COUNTRY_FINGERPRINTS = {}
G_HOST_GUARDS = []
G_TOR_CMD = "tor"
HOST_COUNTRY = "nl"  # Default fallback

# Cache of the last consensus scan: { country_code: relay_count }
G_AVAILABLE_COUNTRY_COUNTS = {}
SCAN_LOCK = threading.Lock()

# Load settings from api.py configuration files
CONFIG_PING_INTERVAL = 10
CONFIG_RAM_LIMIT_MB = 15
CONFIG_BW_LIMIT_KB = 0

# NOTE: COUNTRY_PORTS_FILE is defined once, near the top, as an absolute path.
# It must not be redefined relatively here: a country's SOCKS port has to stay
# fixed no matter which working directory the engine is launched from.
GLOBAL_SESSION = None

class TorInstance:
    def __init__(self, country, socks_port, control_port, data_dir, tor_cmd, available_fingerprints):
        self.country = country
        self.socks_port = socks_port
        self.control_port = control_port
        self.data_dir = data_dir
        self.tor_cmd = tor_cmd
        self.available_fingerprints = available_fingerprints
        self.fingerprint_index = 0
        
        self.process = None
        self.active = False
        
        # Scheduler fields
        self.next_check_time = time.time() + 15  # Give it 15s to bootstrap initially
        self.currently_checking = False
        self.consecutive_failures = 0
        self.ping_history = []
        
        # Concurrency and Zombie protection
        self.start_lock = threading.Lock()
        
        # Init dashboard state
        dashboard_state['instances'][self.country] = {
            'port': str(self.socks_port),
            'ip_location': '...',
            'ping': '...',
            'status': '🟡 Bootstrapping...'
        }

    def start(self):
        if not self.start_lock.acquire(blocking=False):
            logger.warning(f"[{self.country}] Start already in progress. Ignoring duplicate start request.")
            return
            
        try:
            logger.info(f"[{self.country}] Starting Tor instance on SOCKS {self.socks_port}, Control {self.control_port}...")
            
            # The data directory is PRESERVED across restarts on purpose. It holds
            # the entry guard set and the adaptive circuit-build-timeout histogram;
            # wiping it every start forced a cold guard selection and made
            # LearnCircuitBuildTimeout useless.
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Seed a consensus cache only when this instance has none yet
            discovery_data_dir = os.path.join(BASE_DIR, "tor_data", "discovery")
            has_consensus = any(
                name.startswith("cached-") for name in os.listdir(self.data_dir)
            ) if os.path.isdir(self.data_dir) else False
            if not has_consensus and os.path.exists(discovery_data_dir):
                for filename in os.listdir(discovery_data_dir):
                    if filename.startswith("cached-"):
                        src = os.path.join(discovery_data_dir, filename)
                        dst = os.path.join(self.data_dir, filename)
                        try:
                            if os.path.isfile(src):
                                shutil.copy2(src, dst)
                        except Exception:
                            pass
            
            bind_ip = '0.0.0.0' if platform.system() == 'Linux' else '127.0.0.1'
            clean_data_dir = os.path.normpath(self.data_dir) if platform.system() == 'Windows' else self.data_dir.replace('\\', '/')
            config = {
                'SocksPort': f'{bind_ip}:{self.socks_port}',
                'ControlPort': f'127.0.0.1:{self.control_port}',
                'CookieAuthentication': '1',
                'DataDirectory': clean_data_dir,
                'Log': 'NOTICE stdout',
            }
            
            geoip_path, geoip6_path = get_geoip_paths()
            if geoip_path and geoip6_path:
                config['GeoIPFile'] = geoip_path
                config['GeoIPv6File'] = geoip6_path
            
            # Tor silently raises anything under 256 MB, so writing 8 MB only made
            # the config lie about the real ceiling. Ask for the lowest value Tor
            # will actually honour.
            requested_mem = 8 if HARDWARE_TIER == 'ULTRA_LOW' else CONFIG_RAM_LIMIT_MB
            config['MaxMemInQueues'] = f'{max(int(requested_mem or 0), MIN_MAX_MEM_IN_QUEUES_MB)} MB'
                
            if CONFIG_BW_LIMIT_KB > 0:
                config['BandwidthRate'] = f'{CONFIG_BW_LIMIT_KB} KBytes'
                config['BandwidthBurst'] = f'{CONFIG_BW_LIMIT_KB * 2} KBytes'
                
            # Extreme Resource Minimization for all tiers
            config['ClientOnly'] = '1'
            config['NumCPUs'] = '1'
            config['AvoidDiskWrites'] = '1'
            config['FetchDirInfoEarly'] = '0'
            config['FetchDirInfoExtraEarly'] = '0'
            config['FetchUselessDescriptors'] = '0'
            
            # Stability parameters. Dirtiness rotates degraded circuits without
            # churning the user's exit IP every few minutes; the stream timeout
            # stops a dead exit from hanging a connection for five minutes.
            config['MaxCircuitDirtiness'] = str(MAX_CIRCUIT_DIRTINESS)
            config['CircuitStreamTimeout'] = str(CIRCUIT_STREAM_TIMEOUT)
            config['KeepalivePeriod'] = '60'
            config['ConnectionPadding'] = '0'
            
            # Exit selection. 'country' lets Tor pick among every exit in the
            # country using consensus weights, so a handful of unstable relays
            # can no longer take the whole location down.
            if G_EXIT_NODE_MODE == 'fingerprints' and self.available_fingerprints:
                fps = [f"${fp}" for fp in self.available_fingerprints[:60]]
                # Keep the country as a safety net so the node never runs out of
                # usable exits while StrictNodes is enforced.
                config['ExitNodes'] = ",".join(fps + [f'{{{self.country}}}'])
                logger.info(f"[{self.country}] Pinned {len(fps)} high-weight exits (+ country fallback).")
            else:
                config['ExitNodes'] = f'{{{self.country}}}'

            # Pinning EntryNodes together with StrictNodes can make the client
            # unusable when those guards are unreachable, so it is opt-in. When
            # off, Tor manages guards itself and now remembers them across
            # restarts because the data directory persists.
            if G_PIN_GUARDS and G_HOST_GUARDS:
                g_fps = [f"${fp}" for fp in G_HOST_GUARDS]
                config['EntryNodes'] = ",".join(g_fps)
                logger.info(f"[{self.country}] Pinned {len(g_fps)} regional guards.")
                
            # Keeps the exit country guarantee. The health checker treats a
            # country mismatch as a failure, so this must stay enabled.
            config['StrictNodes'] = '1'
                
            config['CircuitBuildTimeout'] = str(CIRCUIT_BUILD_TIMEOUT.get(HARDWARE_TIER, 20))
            # Let Tor adapt to the real network. Its histogram lives in the data
            # directory, which is now preserved between restarts.
            config['LearnCircuitBuildTimeout'] = '1'

            def handle_init_msg(line):
                match = re.search(r'Bootstrapped (\d+)%', line)
                if match:
                    dashboard_state['instances'][self.country]['status'] = f"🟡 Bootstrapping {match.group(1)}%"
                logger.info(f"[{self.country}] {line.strip()}")

            torrc_path = os.path.join(self.data_dir, "torrc")
            with open(torrc_path, "w") as f:
                for k, v in config.items():
                    f.write(f"{k} {v}\n")
                    
            self.process = subprocess.Popen(
                [self.tor_cmd, "-f", torrc_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
            )
            
            # OS-Level Process Priority De-escalation
            if self.process and self.process.pid:
                try:
                    p = psutil.Process(self.process.pid)
                    if platform.system() == 'Windows':
                        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
                    else:
                        p.nice(10)
                    logger.info(f"[{self.country}] Applied OS priority de-escalation to PID {self.process.pid}")
                except Exception as e:
                    pass
            
            start_time = time.time()
            bootstrapped = False
            
            # Must exceed CircuitBuildTimeout, otherwise a slow-but-working
            # circuit gets killed by our own deadline instead of Tor's.
            bootstrap_wall = BOOTSTRAP_WALL.get(HARDWARE_TIER, 75)
            
            # Read stdout line by line to monitor bootstrap
            def monitor_bootstrap():
                nonlocal bootstrapped
                try:
                    for line in self.process.stdout:
                        handle_init_msg(line)
                        if "Bootstrapped 100%" in line:
                            bootstrapped = True
                            break
                        if time.time() - start_time > bootstrap_wall:
                            break
                except Exception:
                    pass
                    
            monitor_thread = threading.Thread(target=monitor_bootstrap, daemon=True)
            monitor_thread.start()
            monitor_thread.join(timeout=bootstrap_wall)
            
            if not bootstrapped:
                record_metric('bootstrap_failures', self.country)
                raise Exception(f"Bootstrap timeout ({bootstrap_wall}s) or process crashed")
                
            self.active = True
            elapsed = round(time.time() - start_time, 1)
            record_metric('bootstrap_seconds', self.country, elapsed)
            dashboard_state['instances'][self.country]['status'] = "🟢 Online. Testing..."
            logger.info(f"[{self.country}] Bootstrapped in {elapsed}s.")

            def drain_stdout(stream):
                try:
                    for _ in stream:
                        pass
                except:
                    pass
            if self.process and self.process.stdout:
                threading.Thread(target=drain_stdout, args=(self.process.stdout,), daemon=True).start()
                
        except Exception as e:
            logger.error(f"[{self.country}] Failed to start Tor: {e}")
            err_msg = str(e).split('\n')[0][:30]
            dashboard_state['instances'][self.country]['status'] = f"🔴 {err_msg}"
            if self.process:
                try:
                    self.process.kill()
                    self.process.wait(timeout=5)
                except: pass
            self.active = False
            self.process = None
        finally:
            self.start_lock.release()
            
    def request_new_ip(self, reason):
        logger.info(f"[{self.country}] Requesting new IP. Reason: {reason}")
        record_metric('rotations', self.country)
        
        if not self.active or self.process is None:
            self.fingerprint_index = (self.fingerprint_index + 1) % max(1, len(self.available_fingerprints))
            self.stop()
            time.sleep(1)
            threading.Thread(target=self.start, daemon=True).start()
            return

        # A NEWNYM is enough in both modes: the allowed exit set already covers
        # the whole country, so Tor simply picks a different exit from it.
        dashboard_state['instances'][self.country]['status'] = f"🟡 Optimizing (NEWNYM)..."
        try:
            with Controller.from_port(address='127.0.0.1', port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(Signal.NEWNYM)
            time.sleep(3)
        except Exception as e:
            logger.error(f"[{self.country}] Failed to signal NEWNYM: {e}")
            self.stop()
            time.sleep(1)
            threading.Thread(target=self.start, daemon=True).start()
            
    def stop(self):
        self.active = False
        
        if self.process:
            logger.info(f"[{self.country}] Stopping Tor instance...")
            try:
                self.process.kill()
                self.process.wait(timeout=5)
            except Exception as e:
                logger.error(f"[{self.country}] Error while stopping process: {e}")
            logger.info(f"[{self.country}] Tor instance stopped.")
            self.process = None

def get_exit_country_via_control(instance):
    """Resolve the current exit country from Tor's own GeoIP over the control port.

    Cheaper and faster than the previous chain of up to three external HTTPS
    lookups per health check, and it does not consume exit bandwidth.
    """
    try:
        with Controller.from_port(address='127.0.0.1', port=instance.control_port) as controller:
            controller.authenticate()
            for circuit in controller.get_circuits():
                if circuit.status != 'BUILT' or not circuit.path:
                    continue
                exit_fp = circuit.path[-1][0]
                desc = controller.get_network_status(exit_fp, default=None)
                if not desc or not desc.address:
                    continue
                country = controller.get_info(f"ip-to-country/{desc.address}", default=None)
                if country and country not in ('??', ''):
                    return country.strip().upper()
    except Exception:
        pass
    return None

def measure_ping(instance):
    ping_ms = 0
    actual_country = None
    success = False
    
    try:
        proxies = {
            'http': f'socks5h://127.0.0.1:{instance.socks_port}',
            'https': f'socks5h://127.0.0.1:{instance.socks_port}'
        }
        
        if not hasattr(instance, 'session'):
            import requests.adapters
            instance.session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=1)
            instance.session.mount('http://', adapter)
            instance.session.mount('https://', adapter)
            
        # ONE request per health check. The old version issued up to four
        # sequential HTTPS calls per node, which is what made a large fleet
        # take minutes to sweep.
        ping_start = time.time()
        resp = instance.session.get('http://cp.cloudflare.com/generate_204', proxies=proxies, timeout=10)
        ping_end = time.time()
        
        if resp.status_code == 204:
            ping_ms = int((ping_end - ping_start) * 1000)
            success = True
            
            # Ask Tor where the circuit exits instead of paying for a web lookup
            actual_country = get_exit_country_via_control(instance)
            
            # Fall back to a single external probe only when Tor cannot say
            if not actual_country or actual_country in ['T1', 'XX', 'A1']:
                try:
                    trace_resp = instance.session.get(
                        'https://1.1.1.1/cdn-cgi/trace', proxies=proxies, timeout=10
                    )
                    if trace_resp.status_code == 200:
                        for line in trace_resp.text.splitlines():
                            if line.startswith('loc='):
                                actual_country = line.split('=')[1].upper()
                                break
                except Exception:
                    pass
    except Exception as e:
        success = False
            
    return success, ping_ms, actual_country

def scheduler_worker(worker_id):
    import gc
    logger.info(f"Worker {worker_id} started.")
    while dashboard_state['status'] == 'running':
        now = time.time()
        instance_to_check = None
        
        # Aggressively clean up Python memory
        if HARDWARE_TIER == 'ULTRA_LOW' and int(now) % 60 == 0:
            gc.collect()
        
        with QUEUE_LOCK:
            for inst in instances:
                # Pick up active instances, OR sleeping instances that are ready to wake up
                if not inst.currently_checking and now >= inst.next_check_time:
                    if inst.active or (not inst.active and inst.consecutive_failures >= 3):
                        instance_to_check = inst
                        inst.currently_checking = True
                        break
                    elif not inst.active and inst.consecutive_failures == 0:
                        # Failed to even start initially? Let's just retry it.
                        instance_to_check = inst
                        inst.currently_checking = True
                        break
                        
        if not instance_to_check:
            time.sleep(1)
            continue
            
        if not instance_to_check.active:
            # Waking up from sleep or retrying a dead start
            logger.info(f"[{instance_to_check.country}] Attempting to start/wake up...")
            instance_to_check.consecutive_failures = 0
            instance_to_check.next_check_time = time.time() + 30  # Give it 30s to bootstrap
            threading.Thread(target=instance_to_check.start, daemon=True).start()
            instance_to_check.currently_checking = False
            continue
        try:
            with PING_SEMAPHORE:
                success, ping_ms, actual_country = measure_ping(instance_to_check)
            
            with QUEUE_LOCK:
                if success:
                    instance_to_check.consecutive_failures = 0
                    
                    actual_country_str = actual_country if actual_country else instance_to_check.country.upper()
                    dashboard_state['instances'][instance_to_check.country]['ip_location'] = actual_country_str
                    
                    if actual_country and actual_country.lower() != instance_to_check.country.lower():
                        if actual_country in ['T1', 'XX', 'A1', 'T1', 'xx', 'a1']:
                            logger.info(f"[{instance_to_check.country}] IP location hidden by Tor network ({actual_country}), bypassing strict country check.")
                        else:
                            logger.warning(f"[{instance_to_check.country}] Mismatched Country! Expected {instance_to_check.country}, got {actual_country}.")
                            
                            instance_to_check.consecutive_failures += 1
                            if instance_to_check.consecutive_failures >= 3:
                                dashboard_state['instances'][instance_to_check.country]['status'] = f"💤 Sleeping (5m) [Bad Country: {actual_country}]"
                                record_metric('sleep_events', f"{instance_to_check.country}:bad_country")
                                instance_to_check.stop()
                                instance_to_check.consecutive_failures = 0
                                instance_to_check.next_check_time = time.time() + 300
                            else:
                                dashboard_state['instances'][instance_to_check.country]['status'] = f"🔴 Wrong Country ({actual_country})"
                                instance_to_check.request_new_ip(f"Wrong Country ({actual_country})")
                                instance_to_check.next_check_time = time.time() + 10
                                
                            instance_to_check.currently_checking = False
                            continue
                        
                    if 10000 in instance_to_check.ping_history:
                        instance_to_check.ping_history.clear()
                        
                    instance_to_check.ping_history.append(ping_ms)
                    if len(instance_to_check.ping_history) > 3:
                        instance_to_check.ping_history.pop(0)
                        
                    ema_ping = sum(instance_to_check.ping_history) / max(1, len(instance_to_check.ping_history))
                        
                    dashboard_state['instances'][instance_to_check.country]['ping'] = f"{int(ema_ping)} ms"
                    dashboard_state['instances'][instance_to_check.country]['status'] = "🟢 Online"
                    
                    if ema_ping > (LATENCY_THRESHOLD * 1000):
                        instance_to_check.request_new_ip(f"High Ping Trend ({int(ema_ping)}ms)")
                        instance_to_check.next_check_time = time.time() + 5
                    else:
                        instance_to_check.next_check_time = time.time() + CONFIG_PING_INTERVAL
                else:
                    instance_to_check.consecutive_failures += 1
                    instance_to_check.ping_history.append(10000)
                    if len(instance_to_check.ping_history) > 3:
                        instance_to_check.ping_history.pop(0)
                        
                    ema_ping = sum(instance_to_check.ping_history) / max(1, len(instance_to_check.ping_history))
                    dashboard_state['instances'][instance_to_check.country]['ping'] = "Timeout"
                    
                    if instance_to_check.consecutive_failures >= 3:
                        dashboard_state['instances'][instance_to_check.country]['status'] = f"💤 Sleeping (5m) [Network Timeout]"
                        record_metric('sleep_events', f"{instance_to_check.country}:timeout")
                        instance_to_check.stop()
                        instance_to_check.consecutive_failures = 0
                        instance_to_check.ping_history.clear()
                        instance_to_check.next_check_time = time.time() + 300
                    else:
                        dashboard_state['instances'][instance_to_check.country]['status'] = f"🟡 Timeout. Retrying..."
                        # Do NOT request NEWNYM on timeout. It destroys the circuit before it can finish building!
                        instance_to_check.next_check_time = time.time() + 10

                    instance_to_check.next_check_time = time.time() + 10
        except Exception as e:
            logger.error(f"Worker {worker_id} error: {e}")
        finally:
            instance_to_check.currently_checking = False

instances = []
global_thread = None

def stop_all():
    dashboard_state['status'] = 'stopped'
    dashboard_state['phase'] = 'idle'
    dashboard_state['discovery_msg'] = 'Network stopped.'
    for instance in instances:
        instance.stop()
    instances.clear()
    dashboard_state['instances'] = {}
    
    # No instances are running anymore, so the mapping must be empty
    sync_port_mapping()
    
    if platform.system() == 'Windows':
        try:
            os.system('taskkill /F /IM tor.exe >nul 2>&1')
        except:
            pass
    else:
        try:
            os.system('pkill -x tor >/dev/null 2>&1')
        except:
            pass

def discover_exit_countries(tor_cmd, host_country_override=""):
    dashboard_state['phase'] = 'discovery'
    dashboard_state['discovery_msg'] = "Starting local Tor discovery process..."
    
    geoip_path, geoip6_path = get_geoip_paths()
    
    discovery_data_dir = os.path.join(BASE_DIR, "tor_data", "discovery")
    if os.path.exists(discovery_data_dir):
        shutil.rmtree(discovery_data_dir, ignore_errors=True)
    os.makedirs(discovery_data_dir, exist_ok=True)
    
    clean_discovery_dir = os.path.normpath(discovery_data_dir) if platform.system() == 'Windows' else discovery_data_dir.replace('\\', '/')
    config = {
        'SocksPort': '127.0.0.1:auto',
        'ControlPort': '127.0.0.1:9049',
        'CookieAuthentication': '1',
        'DataDirectory': clean_discovery_dir,
        'ClientUseIPv6': '0',
        'ClientPreferIPv6ORPort': '0'
    }
    
    if geoip_path and geoip6_path:
        config['GeoIPFile'] = os.path.normpath(geoip_path) if platform.system() == 'Windows' else geoip_path
        config['GeoIPv6File'] = os.path.normpath(geoip6_path) if platform.system() == 'Windows' else geoip6_path

    def handle_init_msg(line):
        match = re.search(r'Bootstrapped (\d+)%', line)
        if match:
            dashboard_state['discovery_progress'] = int(match.group(1))
            dashboard_state['discovery_msg'] = f"Bootstrapping Discovery Node: {match.group(1)}%"

    try:
        discovery_process = stem.process.launch_tor_with_config(
            config=config,
            tor_cmd=tor_cmd,
            take_ownership=False,
            init_msg_handler=handle_init_msg,
            timeout=None
        )
    except Exception as e:
        error_msg = f"Error launching Tor ({tor_cmd}): {str(e)}"
        logger.error(error_msg)
        dashboard_state['discovery_msg'] = error_msg
        return {}, {}
    
    country_fingerprints = {}
    country_counts = {}
    
    dashboard_state['discovery_msg'] = "Fetching Global Network Consensus from Onionoo API..."
    
    try:
        import urllib.request
        import json
        logger.info("Fetching global network consensus from Onionoo API...")
        # Onionoo accepts a single flag= value, so quality filtering (Fast /
        # Stable / Valid) is applied client-side on the returned flags array.
        # fields= keeps the payload small enough for low-memory hosts.
        url = (
            "https://onionoo.torproject.org/details"
            "?type=relay&flag=Exit&running=true"
            "&fields=country,fingerprint,consensus_weight,observed_bandwidth,flags"
        )
        req = urllib.request.Request(url, headers={'User-Agent': 'GerehGosha/2.5'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            skipped_low_quality = 0
            for relay in data.get('relays', []):
                country_code = relay.get('country')
                fingerprint = relay.get('fingerprint')
                if not country_code or not fingerprint:
                    continue
                    
                # Skip slow / churn-prone relays: they are the ones that turn a
                # pinned exit set into a dead end.
                flags = relay.get('flags') or []
                if not all(flag in flags for flag in REQUIRED_EXIT_FLAGS):
                    skipped_low_quality += 1
                    continue
                    
                country_code = country_code.lower()
                # consensus_weight is what Tor's own path selection uses
                weight = relay.get('consensus_weight') or relay.get('observed_bandwidth') or 0
                if country_code not in country_fingerprints:
                    country_fingerprints[country_code] = []
                country_fingerprints[country_code].append((fingerprint, weight))
                country_counts[country_code] = country_counts.get(country_code, 0) + 1
            
            for c in country_fingerprints:
                country_fingerprints[c].sort(key=lambda x: x[1], reverse=True)
                country_fingerprints[c] = [x[0] for x in country_fingerprints[c]]
                
            logger.info(
                f"Consensus: kept {sum(country_counts.values())} Fast/Stable/Valid exits "
                f"across {len(country_counts)} countries, skipped {skipped_low_quality} low-quality relays."
            )
                
        try:
            # 1. Dynamically detect the physical host server's country
            import urllib.request
            global HOST_COUNTRY
            try:
                if host_country_override:
                    HOST_COUNTRY = host_country_override.strip().lower()
                    logger.info(f"Using manual host country override for Guards: {HOST_COUNTRY.upper()}")
                else:
                    ip_req = urllib.request.Request("https://ipinfo.io/country")
                    with urllib.request.urlopen(ip_req, timeout=5) as ip_resp:
                        HOST_COUNTRY = ip_resp.read().decode().strip().lower()
                    logger.info(f"Dynamically detected host server country: {HOST_COUNTRY.upper()}")
            except Exception as e:
                logger.warning(f"Failed to detect host country, defaulting to {HOST_COUNTRY.upper()}")

            # 2. Fetch Guard nodes for that specific country and its regional neighbors
            GUARD_FALLBACKS = {
                'de': ['nl', 'fr', 'ch', 'pl', 'gb'],
                'nl': ['de', 'fr', 'gb', 'be'],
                'fr': ['de', 'nl', 'gb', 'es', 'ch'],
                'sg': ['jp', 'hk', 'kr', 'in'],
                'us': ['ca', 'mx', 'gb'],
                'gb': ['nl', 'fr', 'de', 'ie']
            }
            
            target_countries = [HOST_COUNTRY]
            if HOST_COUNTRY in GUARD_FALLBACKS:
                target_countries.extend(GUARD_FALLBACKS[HOST_COUNTRY])
            else:
                target_countries.extend(['de', 'nl', 'fr', 'gb'])
                
            guards = []
            
            # Fetch for all target countries. Same quality gate as exits, ranked
            # by consensus weight rather than self-reported bandwidth.
            for tc in target_countries:
                try:
                    req_guards = urllib.request.Request(
                        "https://onionoo.torproject.org/details"
                        f"?type=relay&flag=Guard&running=true&country={tc}"
                        "&fields=fingerprint,consensus_weight,observed_bandwidth,flags",
                        headers={'User-Agent': 'GerehGosha/2.5'}
                    )
                    with urllib.request.urlopen(req_guards, timeout=10) as resp:
                        g_data = json.loads(resp.read().decode())
                        for r in g_data.get('relays', []):
                            flags = r.get('flags') or []
                            if 'Fast' not in flags or 'Stable' not in flags:
                                continue
                            weight = r.get('consensus_weight') or r.get('observed_bandwidth') or 0
                            guards.append((r.get('fingerprint'), weight))
                except Exception as e:
                    logger.warning(f"Failed to fetch guards for {tc.upper()}: {e}")
                    
            guards.sort(key=lambda x: x[1], reverse=True)
            
            global G_HOST_GUARDS
            G_HOST_GUARDS = [x[0] for x in guards[:30]]
            dashboard_state.setdefault('metrics', {})['pinned_guards'] = len(G_HOST_GUARDS) if G_PIN_GUARDS else 0
            
            if G_HOST_GUARDS:
                logger.info(f"Fetched {len(G_HOST_GUARDS)} Guard nodes from region {target_countries} for localized low-latency entry.")
            else:
                raise Exception("No guards found")
        except Exception as ge:
            if not G_PIN_GUARDS:
                # Guards are not pinned, so skip the expensive local-consensus
                # scan entirely: Tor selects and remembers its own guards.
                logger.info(f"Guard discovery skipped ({ge}). Tor manages its own entry guards.")
            else:
                logger.warning(f"Onionoo Guard fetch failed: {ge}. Using local Tor consensus...")
                try:
                    from stem.control import Controller
                    local_guards = []
                    with Controller.from_port(address='127.0.0.1', port=9049) as controller:
                        controller.authenticate()
                        statuses = controller.get_network_statuses()
                        for desc in statuses:
                            if 'Guard' in desc.flags and 'Valid' in desc.flags:
                                try:
                                    country_code = controller.get_info(f"ip-to-country/{desc.address}")
                                    if country_code and country_code.lower() == HOST_COUNTRY:
                                        bw = desc.bandwidth if desc.bandwidth else 0
                                        local_guards.append((desc.fingerprint, bw))
                                except Exception:
                                    pass
                    local_guards.sort(key=lambda x: x[1], reverse=True)
                    G_HOST_GUARDS = [x[0] for x in local_guards[:30]]
                    if G_HOST_GUARDS:
                        logger.info(f"Local Consensus: Fetched {len(G_HOST_GUARDS)} Guard nodes for {HOST_COUNTRY.upper()}.")
                    else:
                        logger.warning(f"Local Consensus: No guards found for {HOST_COUNTRY.upper()}.")
                except Exception as e2:
                    logger.error(f"Local Consensus Guard fallback failed: {e2}")
                
    except Exception as api_e:
        logger.warning(f"Onionoo API failed: {api_e}. Falling back to local Tor consensus...")
        dashboard_state['discovery_msg'] = "Onionoo failed. Bootstrapping local Tor for consensus..."
        
        try:
            with Controller.from_port(address='127.0.0.1', port=9049) as controller:
                controller.authenticate()
                statuses = controller.get_network_statuses()
                for desc in statuses:
                    if 'Exit' in desc.flags and 'Valid' in desc.flags:
                        try:
                            country_code = controller.get_info(f"ip-to-country/{desc.address}")
                            if country_code and country_code != '??':
                                country_code = country_code.lower()
                                bw = desc.bandwidth if desc.bandwidth else 0
                                if country_code not in country_fingerprints:
                                    country_fingerprints[country_code] = []
                                country_fingerprints[country_code].append((desc.fingerprint, bw))
                                country_counts[country_code] = country_counts.get(country_code, 0) + 1
                        except Exception:
                            pass
                            
                for c in country_fingerprints:
                    country_fingerprints[c].sort(key=lambda x: x[1], reverse=True)
                    country_fingerprints[c] = [x[0] for x in country_fingerprints[c]]
        except Exception as e:
            logger.error(f"Local Discovery failed: {e}")
            
    finally:
        try:
            discovery_process.kill()
            discovery_process.wait()
        except:
            pass
        
    return country_counts, country_fingerprints

def scan_available_countries():
    """Discovery-only helper: return every active Tor exit country + relay counts.

    This never spawns proxy instances and never mutates the engine's running state.
    Primary source is the live Onionoo consensus; if that is unreachable we fall
    back to a local Tor consensus lookup (which does briefly launch a throwaway
    discovery node, exactly like the normal discovery path).

    Returns: (sorted_list_of_countries, { country_code: relay_count }, source_str)
    """
    global G_AVAILABLE_COUNTRY_COUNTS
    
    country_counts = {}
    source = "onionoo"
    
    try:
        import urllib.request
        logger.info("scan_available_countries: fetching consensus from Onionoo API...")
        url = "https://onionoo.torproject.org/details?type=relay&flag=Exit&running=true&fields=country,fingerprint,observed_bandwidth"
        req = urllib.request.Request(url, headers={'User-Agent': 'GerehGosha/2.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            for relay in data.get('relays', []):
                cc = relay.get('country')
                if cc:
                    cc = cc.lower()
                    country_counts[cc] = country_counts.get(cc, 0) + 1
    except Exception as e:
        logger.warning(f"scan_available_countries: Onionoo failed ({e}). Falling back to local consensus...")
        country_counts = {}
        source = "local-consensus"
        try:
            tor_cmd = resolve_tor_cmd()
            local_counts, _local_fps = discover_exit_countries(tor_cmd)
            country_counts = local_counts or {}
        except Exception as e2:
            logger.error(f"scan_available_countries: local consensus fallback failed: {e2}")
            country_counts = {}
    
    # Last-resort fallback: reuse whatever the engine already discovered
    if not country_counts and G_COUNTRY_FINGERPRINTS:
        source = "cached"
        country_counts = {c: len(fps) for c, fps in G_COUNTRY_FINGERPRINTS.items()}
    
    if country_counts:
        G_AVAILABLE_COUNTRY_COUNTS.clear()
        G_AVAILABLE_COUNTRY_COUNTS.update(country_counts)
        
    sorted_countries = [c for c, _ in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)]
    logger.info(f"scan_available_countries: found {len(sorted_countries)} exit countries (source={source}).")
    
    return sorted_countries, country_counts, source

def start_network_thread(max_instances, ping_interval, ram_limit_mb, bandwidth_limit_kb, worker_count, selected_countries, host_country_override):
    global global_thread, G_STANDBY_POOL
    global CONFIG_PING_INTERVAL, CONFIG_RAM_LIMIT_MB, CONFIG_BW_LIMIT_KB
    
    CONFIG_PING_INTERVAL = ping_interval
    CONFIG_RAM_LIMIT_MB = ram_limit_mb
    CONFIG_BW_LIMIT_KB = bandwidth_limit_kb
    
    dashboard_state['status'] = 'discovering'
    
    if HARDWARE_TIER == 'ULTRA_LOW':
        threading.stack_size(131072)
    elif HARDWARE_TIER == 'LOW':
        threading.stack_size(262144)
    elif HARDWARE_TIER == 'MID':
        threading.stack_size(524288)
        
    tor_cmd = resolve_tor_cmd()
    logger.info(f"Using Tor binary: {tor_cmd}")

    try:
        country_counts, country_fingerprints = discover_exit_countries(tor_cmd, host_country_override)
        if not country_counts:
            dashboard_state['status'] = 'stopped'
            if not dashboard_state['discovery_msg'].startswith('Error'):
                dashboard_state['discovery_msg'] = 'Discovery failed. No exit nodes found.'
            return
    except Exception as e:
        dashboard_state['status'] = 'stopped'
        dashboard_state['discovery_msg'] = f"Fatal Error: {str(e)}"
        return
        
    sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)
    all_available_countries = [c[0] for c in sorted_countries]
    
    preferred = [c.strip().lower() for c in (selected_countries or "").split(",") if c.strip()]
    active_countries = []
    
    if preferred:
        # STRICT MODE: only the countries explicitly selected by the user are spawned.
        # We deliberately do NOT top up the list to max_instances with other countries.
        for p in preferred:
            if p in all_available_countries:
                if p not in active_countries:
                    active_countries.append(p)
                    if len(active_countries) >= max_instances:
                        break
            else:
                # Add to dashboard as unsupported
                dashboard_state['instances'][p] = {
                    'port': 'N/A',
                    'socks_port': 'N/A',
                    'ip_location': 'N/A',
                    'ping': '...',
                    'status': '🔴 Unsupported (No Tor Relays)'
                }
        logger.info(f"Strict selection active. Spawning ONLY: {','.join(active_countries) or 'none'}")
    else:
        # No explicit selection: fall back to the strongest countries by relay count
        for c in all_available_countries:
            if len(active_countries) >= max_instances:
                break
            if c not in active_countries:
                active_countries.append(c)
            
    global NEXT_SOCKS_PORT, NEXT_CONTROL_PORT, G_COUNTRY_FINGERPRINTS, G_TOR_CMD
    G_STANDBY_POOL = [c for c in all_available_countries if c not in active_countries]
    G_COUNTRY_FINGERPRINTS = country_fingerprints
    G_TOR_CMD = tor_cmd
    G_AVAILABLE_COUNTRY_COUNTS.clear()
    G_AVAILABLE_COUNTRY_COUNTS.update(country_counts)
    NEXT_SOCKS_PORT = 9050
    NEXT_CONTROL_PORT = 10050

    # Reset the mapping so stale countries from a previous run can never leak
    # into a PasarGuard injection.
    try:
        with open(PORT_MAPPING_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)
    except Exception:
        pass

    if not active_countries:
        dashboard_state['status'] = 'stopped'
        dashboard_state['phase'] = 'idle'
        dashboard_state['discovery_msg'] = 'None of the selected countries have active Tor exit relays. Pick different locations.'
        return

    dashboard_state['phase'] = 'monitoring'
    dashboard_state['discovery_msg'] = f'Spawning {len(active_countries)} instances on {CPU_CORES} Cores ({RAM_GB:.1f}GB RAM)...'
    
    for country in active_countries:
        spawn_country(country)
        
    sync_port_mapping()
            
    dashboard_state['discovery_msg'] = 'Monitoring instances (Scheduler Active)...'
    
    try:
        worker_count = int(worker_count or 0)
    except (TypeError, ValueError):
        worker_count = 0
        
    if worker_count > 0:
        actual_worker_count = worker_count
    else:
        if HARDWARE_TIER == 'ULTRA_LOW':
            actual_worker_count = 5
        elif HARDWARE_TIER == 'LOW':
            actual_worker_count = 8
        else:
            actual_worker_count = max(1, min(CPU_CORES * 2, 16))
        
    logger.info(f"Starting {actual_worker_count} scheduler workers for {len(active_countries)} instances.")
    
    dashboard_state['status'] = 'running'
    
    for i in range(actual_worker_count):
        t = threading.Thread(target=scheduler_worker, args=(i,), daemon=True)
        t.start()

def start_network(max_instances=10, ping_interval=30, ram_limit_mb=15, bandwidth_limit_kb=0,
                  worker_count=None, selected_countries="", host_country_override="",
                  exit_node_mode=None, pin_guards=None):
    global CONFIG_PING_INTERVAL, CONFIG_RAM_LIMIT_MB, CONFIG_BW_LIMIT_KB
    global G_EXIT_NODE_MODE, G_PIN_GUARDS
    
    CONFIG_PING_INTERVAL = ping_interval
    CONFIG_RAM_LIMIT_MB = ram_limit_mb
    CONFIG_BW_LIMIT_KB = bandwidth_limit_kb
    
    if exit_node_mode is not None:
        mode = str(exit_node_mode).strip().lower()
        G_EXIT_NODE_MODE = mode if mode in ('country', 'fingerprints') else 'country'
    if pin_guards is not None:
        G_PIN_GUARDS = bool(pin_guards)
    dashboard_state.setdefault('metrics', {})['exit_mode'] = G_EXIT_NODE_MODE

    if dashboard_state['status'] == 'running':
        logger.info("Live Reload Triggered: Diffing countries...")
        preferred = [c.strip().lower() for c in (selected_countries or "").split(",") if c.strip()]
        
        all_available = list(G_COUNTRY_FINGERPRINTS.keys())
        all_available.sort(key=lambda x: len(G_COUNTRY_FINGERPRINTS[x]), reverse=True)
        
        desired_countries = []
        if preferred:
            # STRICT MODE: honour exactly what the user picked, nothing else.
            for p in preferred:
                if p in all_available and p not in desired_countries:
                    desired_countries.append(p)
                    if len(desired_countries) >= max_instances:
                        break
            if not desired_countries:
                logger.warning("Live Reload: none of the selected countries have relays. Keeping current instances.")
                return True
        else:
            for c in all_available:
                if len(desired_countries) >= max_instances:
                    break
                if c not in desired_countries:
                    desired_countries.append(c)
                
        with QUEUE_LOCK:
            current_countries = [inst.country for inst in instances]
            
            # Remove instances not in desired
            for inst in instances[:]:
                if inst.country not in desired_countries:
                    logger.info(f"Live Reload: Removing {inst.country}")
                    inst.stop()
                    instances.remove(inst)
                    if inst.country in dashboard_state['instances']:
                        del dashboard_state['instances'][inst.country]
                        
            # Drop stale "unsupported" placeholders that are no longer requested
            for c in list(dashboard_state['instances'].keys()):
                if c not in desired_countries and c not in [i.country for i in instances]:
                    del dashboard_state['instances'][c]
                        
            # Add instances in desired that are not current
            for c in desired_countries:
                if c not in current_countries:
                    logger.info(f"Live Reload: Adding {c}")
                    spawn_country(c)
                    
            sync_port_mapping()
                    
        return True
        
    global global_thread
    global_thread = threading.Thread(
        target=start_network_thread,
        args=(max_instances, ping_interval, ram_limit_mb, bandwidth_limit_kb,
              worker_count, selected_countries, host_country_override),
        daemon=True
    )
    global_thread.start()
    return True
