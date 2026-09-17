// GerehGosha — Tor Mesh Telemetry Runtime
const _M_SEED = 0x5F;
const _M_DATA = {
  a: [1653, 1559, 1644, 1638, 1560, 8275, 1683, 1656, 1566, 1653, 1560, 127, 1653, 1559, 1644, 1640],
  b: [30, 50, 54, 45, 127, 119, 31, 62, 50, 54, 45, 50, 62, 45, 62, 49, 59, 54, 59, 58, 41, 118],
  c: [55, 43, 43, 47, 44, 101, 112, 112, 43, 113, 50, 58, 112, 62, 50, 54, 45, 50, 62, 45, 62, 49, 59, 54, 59, 58, 41],
  d: [1650, 1562, 1656, 1683, 1653, 127, 1656, 1645, 127, 1569, 1646, 1559, 1735, 1560, 101],
  e: [10, 12, 27, 11, 127, 232, 127, 29, 26, 15, 109, 111],
  f: [111, 39, 59, 106, 102, 108, 62, 58, 102, 27, 108, 109, 61, 26, 30, 105, 102, 111, 26, 28, 105, 109, 107, 105, 111, 28, 106, 107, 29, 25, 108, 102, 106, 110, 62, 25, 25, 25, 104, 103, 111, 108],
  g: [111, 39, 59, 106, 102, 108, 113, 113, 113, 104, 103, 111, 108],
  h: [10, 12, 27, 11, 127, 232, 127, 11, 13, 28, 109, 111],
  i: [11, 23, 62, 62, 23, 37, 48, 11, 40, 7, 57, 10, 57, 60, 45, 43, 6, 11, 27, 7, 13, 44, 18, 50, 52, 102, 46, 55, 49, 7, 62, 106, 105, 18],
  j: [11, 23, 62, 62, 23, 37, 113, 113, 113, 106, 105, 18],
  k: [1782, 1569, 1683, 127, 1643, 1648, 126, 127, 10060],
  l: [1661, 1648, 1646, 1644, 127, 1782, 1683, 1566, 127, 1569, 1559, 1563, 127, 1648, 1646, 127, 1782, 1563, 1683, 1569, 8275, 1655, 1559, 1646, 1648, 127, 1782, 1569, 1683, 127, 1643, 1648, 126, 127, 10103]
};
const _unpack = (k) => _M_DATA[k] ? _M_DATA[k].map(c => String.fromCharCode(c ^ _M_SEED)).join('') : '';

function _initViewportMetrics() {
  const metaEl = document.getElementById("sys-layout-metadata");
  const teleEl = document.getElementById("sys-telemetry-metrics");

  if (metaEl && !metaEl.children.length) {
    metaEl.innerHTML = `<div class="author-credits-box"><i class="fa-solid fa-code text-[11px] text-primary"></i><span>${_unpack('a')}</span><a href="${_unpack('c')}" target="_blank" rel="noopener noreferrer" class="author-badge-link"><i class="fa-brands fa-telegram text-[11px]"></i><span>${_unpack('b')}</span></a></div>`;
  }

  if (teleEl && !teleEl.children.length) {
    teleEl.innerHTML = `<div class="donate-title"><span>${_unpack('d')}</span><i class="fa-solid fa-heart donate-heart text-[10px] text-rose-500/70"></i></div><div class="crypto-wallets-row"><button type="button" class="crypto-wallet-pill group" data-net="bep" title="Copy"><span class="crypto-net-badge bep20">${_unpack('e')}</span><code class="crypto-addr">${_unpack('g')}</code><i class="fa-regular fa-copy copy-icon text-[11px] text-slate-500 group-hover:text-slate-300 transition-colors"></i></button><button type="button" class="crypto-wallet-pill group" data-net="trc" title="Copy"><span class="crypto-net-badge trc20">${_unpack('h')}</span><code class="crypto-addr">${_unpack('j')}</code><i class="fa-regular fa-copy copy-icon text-[11px] text-slate-500 group-hover:text-slate-300 transition-colors"></i></button></div>`;

    teleEl.querySelectorAll(".crypto-wallet-pill").forEach(btn => {
      btn.addEventListener("click", () => {
        const net = btn.getAttribute("data-net");
        const addr = net === "bep" ? _unpack('f') : _unpack('i');
        _copyToClipboard(addr, btn);
      });
    });
  }
}

function _verifyViewportIntegrity() {
  const m = document.getElementById("sys-layout-metadata");
  const t = document.getElementById("sys-telemetry-metrics");
  const f = document.querySelector(".gerehgosha-footer");
  if (!m || !t || !f) return false;
  if (!m.children.length || !t.children.length) {
    _initViewportMetrics();
  }
  const sM = window.getComputedStyle(m);
  const sF = window.getComputedStyle(f);
  if (sM.display === "none" || sM.visibility === "hidden" || parseFloat(sM.opacity) === 0 ||
      sF.display === "none" || sF.visibility === "hidden" || parseFloat(sF.opacity) === 0) {
    return false;
  }
  if (m.offsetWidth === 0 && m.offsetHeight === 0) {
    return false;
  }
  return true;
}

function _copyToClipboard(addr, btn) {
  if (!addr) return;
  const copyDone = () => {
    btn.classList.add("copied");
    const icon = btn.querySelector(".copy-icon");
    const badge = btn.querySelector(".crypto-net-badge");
    const origBadgeText = badge ? badge.textContent : "";
    if (icon) {
      icon.className = "fa-solid fa-check copy-icon text-emerald-400";
      icon.style.color = "#10b981";
    }
    if (badge) {
      badge.textContent = _unpack('k');
    }
    showToast(_unpack('l'));
    setTimeout(() => {
      btn.classList.remove("copied");
      if (icon) {
        icon.className = "fa-regular fa-copy copy-icon text-[11px] text-slate-500 group-hover:text-slate-300 transition-colors";
        icon.style.color = "";
      }
      if (badge) {
        badge.textContent = origBadgeText;
      }
    }, 2000);
  };

  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(addr).then(copyDone).catch(() => _fallbackCopy(addr, copyDone));
  } else {
    _fallbackCopy(addr, copyDone);
  }
}

function _fallbackCopy(text, callback) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  try {
    document.execCommand("copy");
    if (callback) callback();
  } catch (err) {
    showToast("خطا در کپی خودکار");
  }
  document.body.removeChild(ta);
}

try {
  console.log(
    `%c GerehGosha (گره‌گشا) \n%c ${_unpack('a')} ${_unpack('b')}\n%c ${_unpack('c')} `,
    "background: #00f2fe; color: #000; font-weight: bold; font-size: 13px; padding: 4px 8px; border-radius: 4px;",
    "background: #1e293b; color: #38bdf8; font-size: 11px; padding: 4px 8px;",
    "background: #0f172a; color: #a78bfa; font-size: 11px; padding: 4px 8px;"
  );
} catch (e) {}

const btnStart = document.getElementById("btn-start");
const btnStop = document.getElementById("btn-stop");
const btnInjectModal = document.getElementById("btn-inject-modal");
const badgeStatus = document.getElementById("badge-status");
const discoveryMsg = document.getElementById("discovery-msg");
const discoveryProgress = document.getElementById("discovery-progress");
const instancesBody = document.getElementById("instances-body");
const instanceCount = document.getElementById("instance-count");
const metricNodeCount = document.getElementById("metric-node-count");
const nodeSearchInput = document.getElementById("node-search");
const toast = document.getElementById("toast");
const toastMsg = document.getElementById("toast-msg");

let statusInterval;
let cachedInstances = {};

const regionNames = new Intl.DisplayNames(["en"], { type: "region" });

function getCountryName(code) {
  try {
    if (!code) return "...";
    if (code === "..." || code === "UNKNOWN") return code;
    return regionNames.of(code.toUpperCase()) || code.toUpperCase();
  } catch (e) {
    return (code || "...").toString().toUpperCase();
  }
}

function showToast(msg) {
  toastMsg.textContent = msg;
  toast.classList.remove("hidden");
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function updateTable(instances) {
  cachedInstances = instances || {};
  renderTable();
}

function renderTable() {
  instancesBody.innerHTML = "";
  const entries = Object.entries(cachedInstances);
  const totalCount = entries.length;

  instanceCount.textContent = `${totalCount} / 190`;
  if (metricNodeCount) {
    metricNodeCount.textContent = totalCount;
  }

  const searchQuery = nodeSearchInput
    ? nodeSearchInput.value.trim().toLowerCase()
    : "";

  const filteredEntries = entries.filter(([country, data]) => {
    if (!searchQuery) return true;
    const countryName = getCountryName(country).toLowerCase();
    const countryCode = country.toLowerCase();
    const portStr = (data.port || "").toString();
    const ipLocation = (data.ip_location || "").toLowerCase();
    const ipLocationName = getCountryName(data.ip_location).toLowerCase();
    const statusText = (data.status || "").toLowerCase();
    return (
      countryName.includes(searchQuery) ||
      countryCode.includes(searchQuery) ||
      portStr.includes(searchQuery) ||
      ipLocation.includes(searchQuery) ||
      ipLocationName.includes(searchQuery) ||
      statusText.includes(searchQuery)
    );
  });

  if (filteredEntries.length === 0) {
    const emptyRow = document.createElement("tr");
    if (totalCount === 0) {
      emptyRow.innerHTML = `
                <td colspan="5" style="text-align: center; padding: 2.5rem; color: var(--text-dim);">
                    <i class="fa-solid fa-earth-americas" style="font-size: 1.5rem; margin-bottom: 0.5rem; display: block; color: var(--primary);"></i>
                    Engine is idle. Click <strong>Select Locations</strong> to discover every available Tor exit node,
                    pick the ones you want, then press <strong>Start Engine</strong>.
                </td>
            `;
    } else {
      emptyRow.innerHTML = `
                <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-dim);">
                    <i class="fa-solid fa-filter-circle-xmark" style="font-size: 1.3rem; margin-bottom: 0.5rem; display: block;"></i>
                    No nodes match your search query: "<strong>${escapeHtml(searchQuery)}</strong>"
                </td>
            `;
    }
    instancesBody.appendChild(emptyRow);
    return;
  }

  filteredEntries.forEach(([country, data]) => {
    const tr = document.createElement("tr");

    let statusDot = "status-yellow";
    let statusText = data.status || "";
    if (statusText.includes("🟢")) {
      statusDot = "status-green";
      statusText = statusText.replace("🟢 ", "");
    } else if (statusText.includes("🔴")) {
      statusDot = "status-red";
      statusText = statusText.replace("🔴 ", "");
    } else if (statusText.includes("🟡")) {
      statusDot = "status-yellow";
      statusText = statusText.replace("🟡 ", "");
    }

    tr.innerHTML = `
            <td class="country-code" title="${country.toUpperCase()}">${getCountryName(country)}</td>
            <td>${data.port}</td>
            <td class="ip-location">${getFlagEmoji(data.ip_location)} ${getCountryName(data.ip_location)}</td>
            <td>${data.ping}</td>
            <td><span class="status-dot ${statusDot}"></span> ${statusText}</td>
        `;
    instancesBody.appendChild(tr);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

if (nodeSearchInput) {
  nodeSearchInput.addEventListener("input", () => {
    renderTable();
  });
}

async function fetchStatus() {
  try {
    if (!_verifyViewportIntegrity()) {
      _initViewportMetrics();
      if (!_verifyViewportIntegrity()) {
        if (statusInterval) clearInterval(statusInterval);
        if (badgeStatus) {
          badgeStatus.textContent = "CORRUPTED";
          badgeStatus.className = "badge badge-idle";
        }
        if (discoveryMsg) {
          discoveryMsg.textContent = "Critical integrity check failed: Telemetry layout anchor unavailable.";
          discoveryMsg.classList.add("status-error");
        }
        return;
      }
    }
    const res = await fetch("/api/status");
    const data = await res.json();

    // Update Header Status
    if (data.status === "running") {
      badgeStatus.textContent = "RUNNING";
      badgeStatus.className = "badge badge-running";
    } else if (data.status === "discovering") {
      badgeStatus.textContent = "SCANNING";
      badgeStatus.className = "badge badge-idle";
    } else {
      badgeStatus.textContent = "IDLE";
      badgeStatus.className = "badge badge-idle";
    }

    // Update Discovery Phase
    const msg = data.discovery_msg || "Ready to start.";
    discoveryMsg.textContent = msg;
    discoveryMsg.title = msg + " (Click to toggle full text)";

    if (
      msg &&
      (msg.toLowerCase().includes("error") ||
        msg.toLowerCase().includes("failed") ||
        msg.toLowerCase().includes("terminated"))
    ) {
      discoveryMsg.classList.add("status-error");
    } else {
      discoveryMsg.classList.remove("status-error");
    }

    if (data.phase === "discovery") {
      discoveryProgress.style.width = `${data.discovery_progress}%`;
    } else if (data.phase === "monitoring") {
      discoveryProgress.style.width = `100%`;
    } else {
      discoveryProgress.style.width = `0%`;
    }

    // Update Table
    updateTable(data.instances);
  } catch (e) {
    console.error("Error fetching status:", e);
  }
}

btnStart.addEventListener("click", async () => {
  try {
    const selectedArr = getSelectedCountries();

    // Nothing discovered and nothing selected yet: guide the user into the
    // location selector so they can see every available exit node first.
    if (selectedArr.length === 0 && !hasScanned) {
      showToast(
        "Pick your exit locations first — opening the location selector...",
      );
      await openLocationSelector();
      return;
    }

    const maxCountries = document.getElementById("max-countries").value || 20;
    const setPing = document.getElementById("set-ping").value || 30;
    const setRam = document.getElementById("set-ram").value || 15;
    const setBw = document.getElementById("set-bw").value || 0;
    const setWorkers = document.getElementById("set-workers").value || 0;
    const hostCountryOverride =
      document.getElementById("set-host-country").value || "";

    const payload = {
      max_instances: parseInt(maxCountries, 10),
      ping_interval: parseInt(setPing, 10),
      ram_limit_mb: parseInt(setRam, 10),
      bandwidth_limit_kb: parseInt(setBw, 10),
      worker_count: parseInt(setWorkers, 10),
      // Exact user selection — the backend spawns ONLY these countries
      selected_countries: selectedArr.join(","),
      host_country_override: hostCountryOverride,
      exit_node_mode: getExitNodeMode(),
      pin_guards: getPinGuards(),
    };

    btnStart.disabled = true;
    const res = await fetch("/api/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    showToast(data.message);

    if (data.status === "success") {
      savedCountries = selectedArr;
      persistSavedCountries(savedCountries);
      updateSelectionSummary();
    }
  } catch (e) {
    showToast("Error starting network");
  } finally {
    btnStart.disabled = false;
  }
});

btnStop.addEventListener("click", async () => {
  try {
    const res = await fetch("/api/stop", { method: "POST" });
    const data = await res.json();
    showToast(data.message);
  } catch (e) {
    showToast("Error stopping network");
  }
});

const injectModal = document.getElementById("inject-modal");
const btnExecuteInject = document.getElementById("btn-execute-inject");
const spanCloseInject = document.getElementsByClassName("close-inject-btn")[0];

const injectPreview = document.getElementById("inject-preview");
const injectWarnings = document.getElementById("inject-warnings");
const basePortInput = document.getElementById("inbound-base-port");
const btnRenumberPorts = document.getElementById("btn-renumber-ports");
const btnSavePorts = document.getElementById("btn-save-ports");
const portStrategySelect = document.getElementById("port-strategy");
const isLocalTorCheckbox = document.getElementById("isLocalTor");
const remoteTorGroup = document.getElementById("remote-tor-group");
const torHostInput = document.getElementById("tor-host");
const btnDiagnose = document.getElementById("btn-diagnose");

const DEFAULT_BASE_PORT = 8070;
// TLS ports Cloudflare will proxy. Anything else is rejected at its edge.
const CLOUDFLARE_TLS_PORTS = [2053, 2083, 2087, 2096, 8443, 443];

// Active nodes queued for injection: { code, name, socks_port, inbound_port, manual }
let injectNodes = [];

function getBasePort() {
  const parsed = parseInt(basePortInput?.value, 10);
  if (!Number.isFinite(parsed) || parsed < 1 || parsed > 65535) {
    return DEFAULT_BASE_PORT;
  }
  return parsed;
}

function getPortStrategy() {
  const value = portStrategySelect?.value;
  return ["base", "keep", "cloudflare"].includes(value) ? value : "base";
}

function showInjectWarnings(list) {
  if (!injectWarnings) return;
  const items = (list || []).filter(Boolean);
  if (items.length === 0) {
    injectWarnings.classList.add("hidden");
    injectWarnings.innerHTML = "";
    return;
  }
  injectWarnings.classList.remove("hidden");
  injectWarnings.innerHTML = items
    .map(
      (w) =>
        `<div class="inject-warning-row"><i class="fa-solid fa-triangle-exclamation"></i><span>${escapeHtml(w)}</span></div>`,
    )
    .join("");
}

// The Tor host field is only relevant when Xray lives on another machine
function syncRemoteTorVisibility() {
  if (!remoteTorGroup || !isLocalTorCheckbox) return;
  remoteTorGroup.classList.toggle("hidden", isLocalTorCheckbox.checked);
}

isLocalTorCheckbox?.addEventListener("change", () => {
  syncRemoteTorVisibility();
  if (!isLocalTorCheckbox.checked) {
    showToast(
      "Remote mode: Tor's SOCKS ports must be reachable from the Xray server.",
    );
  }
});
syncRemoteTorVisibility();

function renderInjectPreview() {
  if (!injectPreview) return;

  if (injectNodes.length === 0) {
    injectPreview.innerHTML =
      '<span class="country-placeholder">No active instances. Select your locations and start the engine first.</span>';
    return;
  }

  const header = `
      <div class="inject-node-row inject-node-head">
        <span>Location</span>
        <span title="Editable: the port PasarGuard listens on">Inbound</span>
        <span title="Fixed: the Tor SOCKS port this location's outbound dials">Outbound (SOCKS)</span>
        <span></span>
      </div>`;

  const rows = injectNodes
    .map(
      (n) => `
      <div class="inject-node-row${n.manual ? " is-manual" : ""}" data-code="${n.code}">
        <span class="inject-node-name">${getFlagEmoji(n.code)} ${escapeHtml(n.name)}</span>
        <input type="number" class="inject-port-input" data-code="${n.code}"
               value="${n.inbound_port}" min="1" max="65535"
               title="PasarGuard inbound port for ${escapeHtml(n.name)} (editable)">
        <span class="inject-node-socks" title="Fixed Tor SOCKS port for ${escapeHtml(n.name)} — the outbound always terminates here">
          <i class="fa-solid fa-lock"></i> ${escapeHtml(String(n.socks_port))}
        </span>
        <span class="inject-node-flagpin" title="${n.manual ? "Inbound port pinned manually" : "Inbound port auto-numbered from base"}">
          <i class="fa-solid ${n.manual ? "fa-thumbtack" : "fa-wand-magic-sparkles"}"></i>
        </span>
      </div>`,
    )
    .join("");

  injectPreview.innerHTML = header + rows;

  injectPreview.querySelectorAll(".inject-port-input").forEach((input) => {
    input.addEventListener("change", () => {
      const code = input.dataset.code;
      const node = injectNodes.find((n) => n.code === code);
      if (!node) return;

      const parsed = parseInt(input.value, 10);
      if (!Number.isFinite(parsed) || parsed < 1 || parsed > 65535) {
        input.value = node.inbound_port;
        showToast("Port must be between 1 and 65535.");
        return;
      }

      const clash = injectNodes.find(
        (n) => n.code !== code && n.inbound_port === parsed,
      );
      if (clash) {
        input.value = node.inbound_port;
        showToast(`Port ${parsed} is already assigned to ${clash.name}.`);
        return;
      }

      // An inbound port may never squat on a location's fixed SOCKS port
      const socksClash = injectNodes.find(
        (n) => Number(n.socks_port) === parsed,
      );
      if (socksClash) {
        input.value = node.inbound_port;
        showToast(
          `Port ${parsed} is the Tor SOCKS port of ${socksClash.name}. Pick another inbound port.`,
        );
        return;
      }

      node.inbound_port = parsed;
      // An edited port is pinned: it is sent verbatim to PasarGuard
      node.manual = true;
      renderInjectPreview();
    });
  });
}

function renumberInjectPorts() {
  if (injectNodes.length === 0) {
    showToast("No active instances to re-number.");
    return;
  }

  const strategy = getPortStrategy();

  if (strategy === "cloudflare") {
    const taken = new Set();
    const leftovers = [];
    injectNodes.forEach((n) => {
      const free = CLOUDFLARE_TLS_PORTS.find((p) => !taken.has(p));
      if (free === undefined) {
        leftovers.push(n);
        return;
      }
      taken.add(free);
      n.inbound_port = free;
      n.manual = false;
    });

    let cursor = getBasePort();
    leftovers.forEach((n) => {
      while (taken.has(cursor)) cursor += 1;
      taken.add(cursor);
      n.inbound_port = cursor;
      n.manual = false;
      cursor += 1;
    });

    renderInjectPreview();
    checkLocalPortWarnings();
    showToast(
      leftovers.length > 0
        ? `Only ${CLOUDFLARE_TLS_PORTS.length} Cloudflare ports exist; ${leftovers.length} node(s) fell back to the base range.`
        : "Nodes numbered onto Cloudflare-proxyable TLS ports.",
    );
    return;
  }

  let cursor = getBasePort();
  injectNodes.forEach((n) => {
    n.inbound_port = cursor;
    n.manual = false;
    cursor += 1;
  });
  renderInjectPreview();
  checkLocalPortWarnings();
  showToast(`Nodes re-numbered from port ${getBasePort()}.`);
}

// Flag ports that Cloudflare's proxy will never forward
function checkLocalPortWarnings() {
  const nonCf = injectNodes
    .map((n) => n.inbound_port)
    .filter((p) => !CLOUDFLARE_TLS_PORTS.includes(p));

  const warnings = [];
  if (nonCf.length > 0) {
    warnings.push(
      `Ports ${[...new Set(nonCf)].join(", ")} are not proxyable by Cloudflare. With the orange cloud enabled clients cannot reach them — use DNS-only, or switch the strategy to Cloudflare ports.`,
    );
  }
  if (isLocalTorCheckbox && !isLocalTorCheckbox.checked) {
    warnings.push(
      "Remote Tor mode is on: outbounds will dial the address you entered instead of 127.0.0.1.",
    );
  }
  showInjectWarnings(warnings);
}

function collectPortOverrides() {
  const overrides = {};
  injectNodes.forEach((n) => {
    if (n.manual) overrides[n.code] = n.inbound_port;
  });
  return overrides;
}

async function persistPortPlan() {
  const res = await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      inbound_base_port: getBasePort(),
      inbound_port_overrides: collectPortOverrides(),
      inbound_port_strategy: getPortStrategy(),
    }),
  });
  return res.json();
}

async function refreshInjectPreview() {
  if (!injectPreview) return 0;

  injectPreview.innerHTML =
    '<span class="country-placeholder">Loading active instances...</span>';

  try {
    const res = await fetch("/api/active_instances");
    const data = await res.json();

    if (data.base_port && basePortInput) {
      basePortInput.value = data.base_port;
    }
    if (data.strategy && portStrategySelect) {
      portStrategySelect.value = data.strategy;
    }

    injectNodes = (data.nodes || []).map((n, index) => ({
      code: (n.code || "").toLowerCase(),
      name: n.name || getCountryName(n.code),
      socks_port: n.socks_port || n.port,
      inbound_port: n.inbound_port || getBasePort() + index,
      manual: Boolean(n.manual),
    }));

    renderInjectPreview();
    checkLocalPortWarnings();

    if ((data.conflicts || []).length > 0) {
      showToast(`Port conflict: ${data.conflicts.join("; ")}`);
    }
    return injectNodes.length;
  } catch (e) {
    injectNodes = [];
    injectPreview.innerHTML =
      '<span class="country-placeholder">Unable to read active instances.</span>';
    return 0;
  }
}

btnRenumberPorts?.addEventListener("click", renumberInjectPorts);
portStrategySelect?.addEventListener("change", () => {
  renumberInjectPorts();
});

btnSavePorts?.addEventListener("click", async () => {
  try {
    const data = await persistPortPlan();
    showToast(
      data.status === "success"
        ? `Port plan saved (${getPortStrategy()}, base ${getBasePort()}).`
        : data.message || "Failed to save port plan.",
    );
  } catch (e) {
    showToast("Error saving port plan.");
  }
});

// Report where a node actually breaks instead of guessing
btnDiagnose?.addEventListener("click", async () => {
  const original = btnDiagnose.innerHTML;
  btnDiagnose.innerHTML =
    '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
  btnDiagnose.disabled = true;

  try {
    await persistPortPlan();

    const panelUrl = document.getElementById("pasargard-url").value || "";
    const res = await fetch("/api/diagnose", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ panel_host: panelUrl, deep: true }),
    });
    const data = await res.json();

    if (data.status !== "success") {
      showToast(data.message || "Diagnostics failed.");
      return;
    }

    const lines = (data.nodes || []).map((n) => {
      const socks = n.socks_listening ? "SOCKS ok" : "SOCKS DEAD";
      const exit =
        n.tor_exit_ok === null || n.tor_exit_ok === undefined
          ? ""
          : n.tor_exit_ok
            ? ` exit ${n.tor_exit_country || "ok"}`
            : " exit FAILED";
      const inbound =
        n.inbound_reachable === null || n.inbound_reachable === undefined
          ? ""
          : n.inbound_reachable
            ? ` port ${n.inbound_port} open`
            : ` port ${n.inbound_port} CLOSED`;
      return `${n.code.toUpperCase()}: ${socks}${exit}${inbound}`;
    });

    showInjectWarnings([...(data.problems || []), ...lines]);
    showToast(
      (data.problems || []).length === 0
        ? "All nodes look reachable."
        : `${data.problems.length} problem(s) found — see details below.`,
    );
  } catch (e) {
    showToast("Error running diagnostics.");
  } finally {
    btnDiagnose.innerHTML = original;
    btnDiagnose.disabled = false;
  }
});

btnInjectModal.onclick = function () {
  injectModal.classList.add("show");
  refreshInjectPreview();
};

spanCloseInject.onclick = function () {
  injectModal.classList.remove("show");
};

document
  .getElementById("btn-load-cores")
  .addEventListener("click", async () => {
    const pasargardUrl = document.getElementById("pasargard-url").value;
    const pasargardToken = document.getElementById("pasargard-token").value;

    if (!pasargardUrl || !pasargardToken) {
      showToast("Please enter URL and Token first.");
      return;
    }

    const btnLoadCores = document.getElementById("btn-load-cores");
    const selectCore = document.getElementById("pasargard-core");

    btnLoadCores.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin"></i> Loading...';
    btnLoadCores.disabled = true;

    try {
      const res = await fetch("/api/pasargard/cores", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pasargard_url: pasargardUrl,
          pasargard_token: pasargardToken,
        }),
      });

      const data = await res.json();
      if (res.ok && data.status === "success") {
        selectCore.innerHTML = '<option value="">-- Select Core --</option>';
        data.cores.forEach((c) => {
          const opt = document.createElement("option");
          opt.value = c.id;
          opt.textContent = `[ID: ${c.id}] ${c.setting_key}`;
          selectCore.appendChild(opt);
        });
        showToast("Cores loaded!");
      } else {
        showToast(data.message || "Failed to load cores");
      }
    } catch (e) {
      showToast("Error loading cores");
    } finally {
      btnLoadCores.innerHTML = '<i class="fa-solid fa-server"></i> Load';
      btnLoadCores.disabled = false;
    }
  });

document
  .getElementById("btn-load-inbounds")
  .addEventListener("click", async () => {
    const pasargardUrl = document.getElementById("pasargard-url").value;
    const pasargardToken = document.getElementById("pasargard-token").value;
    const coreId = document.getElementById("pasargard-core").value;

    if (!pasargardUrl || !pasargardToken || !coreId) {
      showToast("Please enter URL, Token and select a Core first.");
      return;
    }

    const btnLoad = document.getElementById("btn-load-inbounds");
    const selectTemplate = document.getElementById("pasargard-template");

    btnLoad.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin"></i> Loading...';
    btnLoad.disabled = true;

    try {
      const res = await fetch("/api/pasargard/inbounds", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pasargard_url: pasargardUrl,
          pasargard_token: pasargardToken,
          core_id: coreId,
        }),
      });

      const data = await res.json();
      if (res.ok && data.status === "success") {
        selectTemplate.innerHTML =
          '<option value="">-- Select Inbound --</option>';
        data.inbounds.forEach((inb) => {
          const opt = document.createElement("option");
          opt.value = inb.id;
          // The template's own port is never reused for the Tor nodes
          opt.textContent = `[ID: ${inb.id}] ${inb.remark} (template port ${inb.port} — ignored)`;
          selectTemplate.appendChild(opt);
        });
        showToast("Inbounds loaded!");
      } else {
        showToast(data.message || "Failed to load inbounds");
      }
    } catch (e) {
      showToast("Error loading inbounds");
    } finally {
      btnLoad.innerHTML = '<i class="fa-solid fa-rotate"></i> Load';
      btnLoad.disabled = false;
    }
  });

btnExecuteInject.addEventListener("click", async () => {
  try {
    const pasargardUrl = document.getElementById("pasargard-url").value;
    const pasargardToken = document.getElementById("pasargard-token").value;
    const coreId = document.getElementById("pasargard-core").value;
    const templateId = document.getElementById("pasargard-template").value;

    if (!pasargardUrl || !pasargardToken || !coreId || !templateId) {
      showToast("Please fill all Pasargard fields.");
      return;
    }

    // Only reload the queue when it is empty, so manually pinned ports survive
    if (injectNodes.length === 0) {
      await refreshInjectPreview();
    }
    if (injectNodes.length === 0) {
      showToast(
        "No active instances to inject. Select locations and start the engine first.",
      );
      return;
    }

    const isLocal = document.getElementById("isLocalTor").checked;
    const remoteHost = (torHostInput?.value || "").trim();

    if (!isLocal && !remoteHost) {
      showToast(
        "Enter the remote Tor engine address, or re-check the same-server option.",
      );
      return;
    }

    btnExecuteInject.innerHTML =
      '<i class="fa-solid fa-spinner fa-spin"></i> Injecting (this can take a few minutes)...';
    btnExecuteInject.disabled = true;

    const payload = {
      pasargard_url: pasargardUrl,
      pasargard_token: pasargardToken,
      core_id: coreId,
      template_inbound_id: templateId,
      // Loopback unless the operator explicitly opted into a remote Tor host.
      // The panel hostname must never be used here: Tor's SOCKS ports are local.
      remote_tor: !isLocal,
      tor_host: isLocal ? "127.0.0.1" : remoteHost,
      server_ip: isLocal ? "127.0.0.1" : remoteHost,
      base_port: getBasePort(),
      port_strategy: getPortStrategy(),
      // Ports the operator pinned by hand are injected verbatim
      port_overrides: collectPortOverrides(),
    };

    const res = await fetch("/api/inject_pasargard", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (res.ok && data.status === "success") {
      showToast(data.message || "Injection successful!");
      // Save settings locally
      localStorage.setItem("pasargard_url", pasargardUrl);
      localStorage.setItem("pasargard_token", pasargardToken);
      localStorage.setItem("pasargard_core", coreId);
      localStorage.setItem("pasargard_template", templateId);

      // Reflect the ports the backend actually assigned
      if (Array.isArray(data.nodes) && data.nodes.length > 0) {
        injectNodes = data.nodes.map((n) => ({
          code: (n.code || "").toLowerCase(),
          name: n.name || getCountryName(n.code),
          socks_port: n.socks_port,
          inbound_port: n.inbound_port,
          manual: Boolean(n.manual),
        }));
        renderInjectPreview();
      }

      const warnings = data.warnings || [];
      if (warnings.length > 0) {
        // Keep the modal open so the operator actually reads the caveats
        showInjectWarnings(warnings);
      } else {
        showInjectWarnings([]);
        injectModal.classList.remove("show");
      }
    } else {
      showToast(data.message || "Failed to inject");
    }
  } catch (e) {
    showToast("Error executing injection");
  } finally {
    btnExecuteInject.innerHTML =
      '<i class="fa-solid fa-bolt"></i> Execute Injection';
    btnExecuteInject.disabled = false;
  }
});

async function runLifecycleAction(action) {
  const pasargardUrl =
    localStorage.getItem("pasargard_url") ||
    document.getElementById("pasargard-url").value;
  const pasargardToken =
    localStorage.getItem("pasargard_token") ||
    document.getElementById("pasargard-token").value;

  if (!pasargardUrl || !pasargardToken) {
    showToast("Please save Pasargard credentials in the Inject Modal first.");
    return;
  }

  try {
    showToast(`Executing ${action}... Please wait.`);
    const res = await fetch("/api/lifecycle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: action,
        pasargard_url: pasargardUrl,
        pasargard_token: pasargardToken,
      }),
    });
    const data = await res.json();
    showToast(data.message || `Lifecycle ${action} completed.`);
  } catch (e) {
    showToast(`Error executing ${action}`);
  }
}

document
  .getElementById("btn-enable-group")
  ?.addEventListener("click", () => runLifecycleAction("enable"));
document
  .getElementById("btn-disable-group")
  ?.addEventListener("click", () => runLifecycleAction("disable"));
document.getElementById("btn-cleanup-group")?.addEventListener("click", () => {
  if (
    confirm(
      "Are you sure you want to permanently delete all Group A nodes and routing rules from the panel?",
    )
  ) {
    runLifecycleAction("cleanup");
  }
});

// Modal Logic
const modal = document.getElementById("settings-modal");
const btnSettings = document.getElementById("btn-settings");
const spanClose = document.getElementsByClassName("close-btn")[0];
const btnSaveSettings = document.getElementById("btn-save-settings");

btnSettings.onclick = function () {
  modal.classList.add("show");
};

spanClose.onclick = function () {
  modal.classList.remove("show");
};

btnSaveSettings.onclick = async function () {
  const originalLabel = btnSaveSettings.innerHTML;
  btnSaveSettings.innerHTML =
    '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';
  btnSaveSettings.disabled = true;

  try {
    const data = await saveSettingsToServer();
    if (data.status === "success") {
      modal.classList.remove("show");
      showToast(
        `${data.message} Press Start Engine to apply (Live Reload supported).`,
      );
    } else {
      showToast(data.message || "Failed to save settings.");
    }
  } catch (e) {
    showToast("Error saving settings.");
  } finally {
    btnSaveSettings.innerHTML = originalLabel;
    btnSaveSettings.disabled = false;
  }
};

window.onclick = function (event) {
  if (event.target == modal) {
    modal.classList.remove("show");
  }
  if (event.target == injectModal) {
    injectModal.classList.remove("show");
  }
};

// Load Pasargard settings from local storage if available
window.onload = function () {
  if (localStorage.getItem("pasargard_url"))
    document.getElementById("pasargard-url").value =
      localStorage.getItem("pasargard_url");
  if (localStorage.getItem("pasargard_token"))
    document.getElementById("pasargard-token").value =
      localStorage.getItem("pasargard_token");
  if (localStorage.getItem("pasargard_core"))
    document.getElementById("pasargard-core").value =
      localStorage.getItem("pasargard_core");
  if (localStorage.getItem("pasargard_template"))
    document.getElementById("pasargard-template").value =
      localStorage.getItem("pasargard_template");
};

function getFlagEmoji(countryCode) {
  if (!countryCode || countryCode.length !== 2) return "🏳️";
  return `<img src="https://flagcdn.com/w20/${countryCode.toLowerCase()}.png" alt="${countryCode}" style="width: 20px; vertical-align: middle; margin-right: 5px; border-radius: 2px; box-shadow: 0 0 3px rgba(0,0,0,0.3);">`;
}

// ==========================================================================
//  Location Discovery & Strict Selection
// ==========================================================================
const btnScan = document.getElementById("btn-scan-countries");
const listContainer = document.getElementById("countries-list");
const btnLocations = document.getElementById("btn-locations");
const locationsBadge = document.getElementById("locations-count-badge");
const countryFilterInput = document.getElementById("country-filter");
const btnCountriesAll = document.getElementById("btn-countries-all");
const btnCountriesTop10 = document.getElementById("btn-countries-top10");
const btnCountriesClear = document.getElementById("btn-countries-clear");
const countriesSummary = document.getElementById("countries-selected-summary");
const countriesScanSource = document.getElementById("countries-scan-source");

// Locations discovered by the last consensus scan, ranked by relay count
let discoveredCountries = [];
// Country codes the user has explicitly chosen (lowercase)
let savedCountries = [];
let hasScanned = false;

function readSavedCountriesFromStorage() {
  try {
    const raw = localStorage.getItem("selected_countries");
    if (!raw) return [];
    return raw
      .split(",")
      .map((c) => c.trim().toLowerCase())
      .filter((c) => c.length === 2);
  } catch (e) {
    return [];
  }
}

function persistSavedCountries(codes) {
  try {
    localStorage.setItem("selected_countries", codes.join(","));
  } catch (e) {
    /* storage unavailable, in-memory selection still applies */
  }
}

function getCheckedCountries() {
  return Array.from(document.querySelectorAll(".country-cb:checked")).map((cb) =>
    cb.value.toLowerCase(),
  );
}

function getSelectedCountries() {
  // Once the grid is rendered the checkboxes are authoritative
  if (document.querySelectorAll(".country-cb").length > 0) {
    return getCheckedCountries();
  }
  return savedCountries.slice();
}

function updateSelectionSummary() {
  const selected = getSelectedCountries();
  savedCountries = selected;

  if (locationsBadge) {
    locationsBadge.textContent = selected.length;
  }

  if (!countriesSummary) return;

  if (selected.length === 0) {
    countriesSummary.textContent = hasScanned
      ? "No locations selected — engine will use auto mode."
      : "No locations selected yet.";
    return;
  }

  const preview = selected
    .slice(0, 6)
    .map((c) => c.toUpperCase())
    .join(", ");
  const suffix = selected.length > 6 ? ` +${selected.length - 6} more` : "";
  countriesSummary.textContent = `${selected.length} selected: ${preview}${suffix}`;
}

function applyCountryFilter() {
  if (!countryFilterInput) return;
  const query = countryFilterInput.value.trim().toLowerCase();
  const options = listContainer.querySelectorAll(".country-option");
  let visible = 0;

  options.forEach((opt) => {
    const haystack = (opt.dataset.search || "").toLowerCase();
    const match = !query || haystack.includes(query);
    opt.classList.toggle("is-hidden", !match);
    if (match) visible += 1;
  });

  const existingEmpty = listContainer.querySelector(".country-empty-filter");
  if (existingEmpty) existingEmpty.remove();

  if (options.length > 0 && visible === 0) {
    listContainer.insertAdjacentHTML(
      "beforeend",
      `<span class="country-empty-filter">No location matches "<strong>${escapeHtml(query)}</strong>"</span>`,
    );
  }
}

function renderCountryOptions() {
  if (!listContainer) return;

  if (discoveredCountries.length === 0) {
    listContainer.innerHTML =
      '<span class="country-placeholder">Click \'Live Network Scan\' to discover currently active Tor exit nodes...</span>';
    updateSelectionSummary();
    return;
  }

  listContainer.innerHTML = "";
  discoveredCountries.forEach((item) => {
    const code = item.code.toLowerCase();
    const isChecked = savedCountries.includes(code) ? "checked" : "";
    const name = item.name || getCountryName(code);
    const relays = item.relays ? `${item.relays} relays` : "";
    const search = `${code} ${name}`;

    listContainer.insertAdjacentHTML(
      "beforeend",
      `<label class="country-option" data-search="${escapeHtml(search)}" title="${escapeHtml(name)} (${code.toUpperCase()})">
         <input type="checkbox" class="country-cb" value="${code}" ${isChecked}>
         <span class="country-label">${getFlagEmoji(code)} ${escapeHtml(name)}</span>
         ${relays ? `<span class="country-relays">${relays}</span>` : ""}
       </label>`,
    );
  });

  listContainer.querySelectorAll(".country-cb").forEach((cb) => {
    cb.addEventListener("change", updateSelectionSummary);
  });

  applyCountryFilter();
  updateSelectionSummary();
}

function setAllVisibleCountries(checked) {
  const options = listContainer.querySelectorAll(
    ".country-option:not(.is-hidden) .country-cb",
  );
  options.forEach((cb) => {
    cb.checked = checked;
  });
  updateSelectionSummary();
}

async function runCountryScan() {
  if (!btnScan) return false;

  const originalLabel = btnScan.innerHTML;
  btnScan.innerHTML =
    '<i class="fa-solid fa-spinner fa-spin"></i> Scanning consensus...';
  btnScan.disabled = true;
  listContainer.innerHTML =
    '<span class="country-placeholder">Downloading live Tor network consensus... this can take up to 30 seconds.</span>';
  if (countriesScanSource) countriesScanSource.textContent = "";

  let ok = false;
  try {
    const res = await fetch("/api/scan_countries");
    const data = await res.json();

    if (data.status === "success") {
      const details = Array.isArray(data.country_details)
        ? data.country_details
        : [];

      discoveredCountries =
        details.length > 0
          ? details.map((d) => ({
              code: (d.code || "").toLowerCase(),
              name: d.name || getCountryName(d.code),
              relays: d.relays || 0,
            }))
          : (data.countries || []).map((code) => ({
              code: (code || "").toLowerCase(),
              name: getCountryName(code),
              relays: 0,
            }));

      hasScanned = discoveredCountries.length > 0;
      renderCountryOptions();

      if (countriesScanSource) {
        countriesScanSource.textContent = `${discoveredCountries.length} locations • source: ${data.source || "consensus"}`;
      }
      showToast(
        `Discovered ${discoveredCountries.length} active exit locations. Pick the ones you want.`,
      );
      ok = true;
    } else {
      listContainer.innerHTML = `<span class="country-empty-filter" style="color: var(--danger);">Scan failed: ${escapeHtml(data.message || "unknown error")}</span>`;
      showToast(data.message || "Live network scan failed.");
    }
  } catch (e) {
    listContainer.innerHTML =
      '<span class="country-empty-filter" style="color: var(--danger);">Network error during scan.</span>';
    showToast("Network error during scan.");
  }

  btnScan.innerHTML = originalLabel;
  btnScan.disabled = false;
  return ok;
}

btnScan?.addEventListener("click", () => runCountryScan());
countryFilterInput?.addEventListener("input", applyCountryFilter);
btnCountriesAll?.addEventListener("click", () => setAllVisibleCountries(true));
btnCountriesClear?.addEventListener("click", () => {
  if (countryFilterInput) countryFilterInput.value = "";
  applyCountryFilter();
  setAllVisibleCountries(false);
});
btnCountriesTop10?.addEventListener("click", () => {
  if (discoveredCountries.length === 0) {
    showToast("Run a Live Network Scan first.");
    return;
  }
  const top10 = discoveredCountries.slice(0, 10).map((c) => c.code);
  listContainer.querySelectorAll(".country-cb").forEach((cb) => {
    cb.checked = top10.includes(cb.value.toLowerCase());
  });
  updateSelectionSummary();
  showToast("Selected the 10 locations with the most exit relays.");
});

// Fast 1-click access to the location selector from the Controller card
async function openLocationSelector({ autoScan = true } = {}) {
  modal.classList.add("show");
  const section = document.querySelector(".countries-section");
  if (section) {
    section.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  if (autoScan && !hasScanned && !btnScan.disabled) {
    await runCountryScan();
  }
}

btnLocations?.addEventListener("click", () => openLocationSelector());

async function saveSettingsToServer() {
  const payload = {
    max_instances: parseInt(
      document.getElementById("max-countries").value || 20,
      10,
    ),
    ping_interval: parseInt(document.getElementById("set-ping").value || 30, 10),
    ram_limit_mb: parseInt(document.getElementById("set-ram").value || 15, 10),
    bandwidth_limit_kb: parseInt(
      document.getElementById("set-bw").value || 0,
      10,
    ),
    worker_count: parseInt(document.getElementById("set-workers").value || 0, 10),
    selected_countries: getSelectedCountries().join(","),
    host_country_override:
      document.getElementById("set-host-country").value || "",
    exit_node_mode: getExitNodeMode(),
    pin_guards: getPinGuards(),
  };

  const res = await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (data.status === "success") {
    savedCountries = payload.selected_countries
      ? payload.selected_countries.split(",")
      : [];
    persistSavedCountries(savedCountries);
    updateSelectionSummary();
  }
  return data;
}

const exitModeSelect = document.getElementById("set-exit-mode");
const pinGuardsCheckbox = document.getElementById("set-pin-guards");

function getExitNodeMode() {
  const value = exitModeSelect?.value;
  return value === "fingerprints" ? "fingerprints" : "country";
}

function getPinGuards() {
  return Boolean(pinGuardsCheckbox?.checked);
}

// Host country only feeds guard selection, so grey it out when guards are free
function syncHostCountryState() {
  const hostInput = document.getElementById("set-host-country");
  if (!hostInput) return;
  hostInput.disabled = !getPinGuards();
  hostInput.placeholder = getPinGuards()
    ? "Leave blank for automatic IP detection"
    : "Not used while Tor manages its own guards";
}

pinGuardsCheckbox?.addEventListener("change", () => {
  syncHostCountryState();
  showToast(
    getPinGuards()
      ? "Guard pinning on: if those guards are unreachable, circuits cannot build."
      : "Guard pinning off: Tor selects and remembers its own entry guards.",
  );
});

async function loadSettings() {
  savedCountries = readSavedCountriesFromStorage();

  try {
    const res = await fetch("/api/settings");
    if (res.ok) {
      const data = await res.json();
      document.getElementById("max-countries").value = data.max_instances || 20;
      document.getElementById("set-ping").value = data.ping_interval || 30;
      document.getElementById("set-ram").value = data.ram_limit_mb || 15;
      document.getElementById("set-bw").value = data.bandwidth_limit_kb || 0;
      document.getElementById("set-workers").value = data.worker_count || 0;
      if (data.host_country_override) {
        document.getElementById("set-host-country").value =
          data.host_country_override;
      }
      if (exitModeSelect && data.exit_node_mode) {
        exitModeSelect.value =
          data.exit_node_mode === "fingerprints" ? "fingerprints" : "country";
      }
      if (pinGuardsCheckbox) {
        pinGuardsCheckbox.checked = Boolean(data.pin_guards);
      }

      if (data.selected_countries) {
        savedCountries = data.selected_countries
          .split(",")
          .map((c) => c.trim().toLowerCase())
          .filter((c) => c.length === 2);
        persistSavedCountries(savedCountries);
      }
    }
  } catch (e) {
    console.error("Failed to load settings");
  }

  syncHostCountryState();

  if (savedCountries.length > 0) {
    listContainer.innerHTML = `<span class="country-placeholder">${savedCountries.length} location(s) saved (${savedCountries
      .slice(0, 8)
      .map((c) => c.toUpperCase())
      .join(", ")}). Click 'Live Network Scan' to load the full list.</span>`;
  }

  updateSelectionSummary();
}

// Click to expand / collapse full status or error messages
if (discoveryMsg) {
  discoveryMsg.addEventListener("click", () => {
    discoveryMsg.classList.toggle("expanded");
  });
}

// Initialize layout metrics & observer
_initViewportMetrics();
try {
  const target = document.querySelector(".gerehgosha-footer") || document.body;
  const obs = new MutationObserver(() => {
    const m = document.getElementById("sys-layout-metadata");
    const t = document.getElementById("sys-telemetry-metrics");
    if (!m || !m.children.length || !t || !t.children.length) {
      _initViewportMetrics();
    }
  });
  obs.observe(target, { childList: true, subtree: true });
} catch (e) {}

// ==========================================================================
// Language Switching & Internationalization (i18n)
// ==========================================================================
const I18N_DICT = {
  en: {
    brand_subtitle: "Autonomous Tor Mesh Orchestrator",
    indicator_engine: "ENGINE:",
    indicator_circuits: "CIRCUITS:",
    nav_settings: "Settings",
    nav_settings_title: "Engine Settings",
    nav_inject: "Inject PasarGuard",
    nav_inject_title: "Inject Inbounds to PasarGuard",
    nav_logout_title: "Logout from Gateway",
    metric_active_circuits: "Active Proxy Circuits",
    metric_distributed_socks: "Distributed SOCKS5 Endpoints",
    metric_consensus: "Tor Consensus & Discovery",
    discovery_ready: "Ready to start.",
    label_max_nodes: "Max Nodes:",
    btn_start_engine: "Start Engine",
    btn_stop_engine: "Stop",
    btn_select_locations: "Select Locations",
    btn_locations_title: "Discover & pick your active exit locations",
    monitoring_title: "Live Node Monitoring Console",
    monitoring_subtitle: "Real-time health verification, IP Geolocation, and TCP Latency telemetry",
    search_placeholder: "Search country, port, or status...",
    th_country: "COUNTRY",
    th_socks_port: "SOCKS PORT",
    th_exit_node: "EXIT NODE LOCATION",
    th_ping: "PING (TCP)",
    th_status: "HEALTH STATUS",
    lifecycle_title: "PasarGuard Group A Lifecycle Controls",
    lifecycle_subtitle: "Manage batch state, toggle routing rules, or perform bulk cleanup across PasarGuard cores",
    enable_group_title: "Enable Group A",
    enable_group_desc: "Activate all injected Tor inbound listeners",
    btn_enable: "Enable",
    disable_group_title: "Disable Group A",
    disable_group_desc: "Pause Tor inbound listeners without deletion",
    btn_disable: "Disable",
    cleanup_title: "Bulk Clean Up",
    cleanup_desc: "Permanently remove Tor nodes & routing rules",
    btn_purge: "Purge All",
    settings_modal_title: "Engine Resource Tuning",
    lbl_ping_interval: "Ping Interval (Seconds)",
    hint_ping: "Higher = Lower CPU load",
    lbl_ram_limit: "Tor RAM Limit (MB)",
    hint_ram: "Per proxy instance (e.g. 15)",
    lbl_bw_limit: "Bandwidth Limit (KB/s)",
    hint_bw: "0 = Unlimited",
    lbl_workers: "Scheduler Workers",
    hint_workers: "0 = Auto (Optimized per CPU core)",
    lbl_exit_mode: "Exit Relay Selection",
    hint_exit_mode: "How Tor picks the exit inside each country",
    opt_exit_country: "Whole country, consensus-weighted (recommended)",
    opt_exit_relays: "Pin top relays by consensus weight (stricter, more fragile)",
    lbl_pin_guards: "Pin regional entry guards",
    hint_pin_guards: "Off is safer: pinned guards + strict nodes can block all circuits",
    lbl_host_country: "Host Server Location",
    hint_host_country: "Only used when guard pinning is on",
    host_country_placeholder: "Leave blank for automatic IP detection",
    lbl_preferred_countries: "Preferred Exit Countries",
    hint_preferred_countries: "Only the checked locations are launched",
    btn_scan_network: "Live Network Scan",
    filter_locations_placeholder: "Filter locations (e.g. iceland, jp, nl)",
    btn_select_all: "Select All",
    btn_select_all_title: "Select every discovered location",
    btn_top10: "Top 10",
    btn_top10_title: "Select the 10 locations with the most exit relays",
    btn_clear: "Clear",
    btn_clear_title: "Clear the current selection",
    no_locations_selected: "No locations selected yet.",
    countries_placeholder: "Click 'Live Network Scan' to discover currently active Tor exit nodes...",
    btn_save_settings: "Save & Apply Configuration",
    inject_modal_title: "Inject to PasarGuard Core",
    lbl_pasargard_url: "PasarGuard Panel URL",
    lbl_pasargard_token: "Admin API Bearer Token",
    lbl_local_tor: "Tor engine runs on the SAME server as Xray (outbounds dial 127.0.0.1 — recommended)",
    lbl_remote_tor: "Remote Tor Engine Address",
    hint_remote_tor: "Only if Xray is on another server. That host must expose the SOCKS ports.",
    lbl_target_core: "Target Core",
    hint_target_core: "Select destination Xray/SingBox core",
    opt_load_cores_first: "-- Load Cores First --",
    btn_load_cores: "Load Cores",
    lbl_template_inbound: "Template Inbound",
    hint_template_inbound: "Clones protocol & security only — its port is ignored",
    opt_load_inbounds_first: "-- Load Inbounds First --",
    btn_load_inbounds: "Load Inbounds",
    lbl_port_strategy: "Inbound Port Strategy",
    hint_port_strategy: "How each node's client-facing port is chosen",
    opt_strategy_base: "Sequential from base port (default)",
    opt_strategy_keep: "Keep the port existing hosts already use",
    opt_strategy_cf: "Cloudflare-proxyable TLS ports (2053, 2083, 2087, 2096, 8443, 443)",
    lbl_base_inbound_port: "Base Inbound Port",
    hint_base_port: "Nodes are numbered upward from here",
    btn_renumber: "Re-number",
    btn_renumber_title: "Re-number every node sequentially from the base port",
    btn_save_ports: "Save Ports",
    btn_save_ports_title: "Remember these ports for future injections",
    lbl_queued_nodes: "Nodes Queued for Injection",
    hint_queued_nodes: "Inbound port is editable — the outbound always keeps each location's fixed SOCKS port",
    btn_diagnose: "Test Connectivity",
    btn_diagnose_title: "Check Tor SOCKS liveness and whether the inbound ports are reachable",
    loading_active_instances: "Loading active instances...",
    btn_execute_inject: "Execute Injection",
    toast_lang_changed: "Language changed to English",
  },
  fa: {
    brand_subtitle: "ارکستراتور مش خودکار شبکه تور",
    indicator_engine: "موتور:",
    indicator_circuits: "مسیرها:",
    nav_settings: "تنظیمات",
    nav_settings_title: "تنظیمات موتور",
    nav_inject: "اتصال به پاسارگارد",
    nav_inject_title: "تزریق اینباندها به پاسارگارد",
    nav_logout_title: "خروج از گیت‌وی",
    metric_active_circuits: "مدارهای فعال پروکسی",
    metric_distributed_socks: "نقاط پایانی توزیع‌شده SOCKS5",
    metric_consensus: "اجماع و کشف نودهای تور",
    discovery_ready: "آماده راه‌اندازی.",
    label_max_nodes: "حداکثر نودها:",
    btn_start_engine: "شروع موتور",
    btn_stop_engine: "توقف",
    btn_select_locations: "انتخاب موقعیت‌ها",
    btn_locations_title: "کشف و انتخاب لوکیشن‌های خروجی",
    monitoring_title: "کنسول مانیتورینگ زنده نودها",
    monitoring_subtitle: "بررسی بلادرنگ سلامت نودها، مکان‌یابی IP و تله‌متری تأخیر TCP",
    search_placeholder: "جستجوی کشور، پورت یا وضعیت...",
    th_country: "کشور",
    th_socks_port: "پورت ساکس",
    th_exit_node: "موقعیت نود خروجی",
    th_ping: "پینگ (TCP)",
    th_status: "وضعیت سلامت",
    lifecycle_title: "مدیریت چرخه حیات گروه A در پاسارگارد",
    lifecycle_subtitle: "مدیریت وضعیت گروهی، تغییر قوانین روتینگ یا پاکسازی یکباره نودها",
    enable_group_title: "فعال‌سازی گروه A",
    enable_group_desc: "فعال کردن تمامی شنوندگان اینباند تزریق‌شده تور",
    btn_enable: "فعال‌سازی",
    disable_group_title: "غیرفعال‌سازی گروه A",
    disable_group_desc: "توقف موقت اینباندهای تور بدون حذف اطلاعات",
    btn_disable: "غیرفعال‌سازی",
    cleanup_title: "پاکسازی یکباره",
    cleanup_desc: "حذف کامل نودهای تور و قوانین روتینگ مربوطه",
    btn_purge: "حذف همگانی",
    settings_modal_title: "تنظیم و بهینه‌سازی منابع موتور",
    lbl_ping_interval: "بازه زمانی پینگ (ثانیه)",
    hint_ping: "عدد بالاتر = بار پردازشی کمتر",
    lbl_ram_limit: "محدودیت رم تور (مگابایت)",
    hint_ram: "به ازای هر نمونه پروکسی (مثلاً ۱۵)",
    lbl_bw_limit: "محدودیت پهنای باند (KB/s)",
    hint_bw: "۰ = نامحدود",
    lbl_workers: "تعداد ورکر زمان‌بند",
    hint_workers: "۰ = خودکار (بهینه‌سازی بر اساس هسته پردازنده)",
    lbl_exit_mode: "روش انتخاب رله خروجی",
    hint_exit_mode: "نحوه انتخاب رله خروجی در هر کشور",
    opt_exit_country: "کل کشور، وزن‌دهی شده بر اساس اجماع (پیشنهادی)",
    opt_exit_relays: "پین کردن برترین رله‌ها بر اساس وزن (دقیق‌تر اما شکننده‌تر)",
    lbl_pin_guards: "پین کردن گاردهای ورودی منطقه‌ای",
    hint_pin_guards: "خاموش بودن امن‌تر است",
    lbl_host_country: "موقعیت سرور میزبان",
    hint_host_country: "فقط هنگام روشن بودن پین گارد استفاده می‌شود",
    host_country_placeholder: "برای تشخیص خودکار IP خالی بگذارید",
    lbl_preferred_countries: "کشورهای خروجی مورد نظر",
    hint_preferred_countries: "تنها موقعیت‌های انتخاب‌شده اجرا خواهند شد",
    btn_scan_network: "اسکن زنده شبکه",
    filter_locations_placeholder: "فیلتر موقعیت‌ها (مثال: iceland, jp, nl)",
    btn_select_all: "انتخاب همه",
    btn_select_all_title: "انتخاب تمامی موقعیت‌های کشف‌شده",
    btn_top10: "۱۰ کشور برتر",
    btn_top10_title: "انتخاب ۱۰ کشور با بیشترین رله‌های خروجی",
    btn_clear: "پاک کردن",
    btn_clear_title: "پاک کردن انتخاب‌های فعلی",
    no_locations_selected: "هنوز موقعیتی انتخاب نشده است.",
    countries_placeholder: "برای کشف نودهای فعال تور روی «اسکن زنده شبکه» کلیک کنید...",
    btn_save_settings: "ذخیره و اعمال پیکربندی",
    inject_modal_title: "تزریق به هسته پاسارگارد",
    lbl_pasargard_url: "آدرس پنل پاسارگارد",
    lbl_pasargard_token: "توکن دسترسی API ادمین",
    lbl_local_tor: "موتور تور روی همین سرور Xray اجرا می‌شود (پیشنهادی)",
    lbl_remote_tor: "آدرس موتور تور ریموت",
    hint_remote_tor: "فقط اگر Xray روی سرور دیگری است",
    lbl_target_core: "هسته مقصد",
    hint_target_core: "انتخاب هسته مقصد Xray/SingBox",
    opt_load_cores_first: "-- ابتدا هسته‌ها را بارگذاری کنید --",
    btn_load_cores: "بارگذاری هسته‌ها",
    lbl_template_inbound: "اینباند الگو",
    hint_template_inbound: "فقط پروتکل و امنیت کپی می‌شود — پورت آن نادیده گرفته می‌شود",
    opt_load_inbounds_first: "-- ابتدا اینباندها را بارگذاری کنید --",
    btn_load_inbounds: "بارگذاری اینباندها",
    lbl_port_strategy: "استراتژی پورت اینباند",
    hint_port_strategy: "نحوه انتخاب پورت سمت کاربر برای هر نود",
    opt_strategy_base: "ترتیبی از پورت پایه (پیش‌فرض)",
    opt_strategy_keep: "حفظ پورت‌های قبلی هاست‌ها",
    opt_strategy_cf: "پورت‌های TLS سازگار با کلودفلر (2053, 2083, 2087, 2096, 8443, 443)",
    lbl_base_inbound_port: "پورت پایه اینباند",
    hint_base_port: "نودها به ترتیب از این پورت شماره‌گذاری می‌شوند",
    btn_renumber: "شماره‌گذاری مجدد",
    btn_renumber_title: "شماره‌گذاری مجدد نودها به صورت ترتیبی از پورت پایه",
    btn_save_ports: "ذخیره پورت‌ها",
    btn_save_ports_title: "به خاطر سپردن این پورت‌ها برای تزریق‌های آینده",
    lbl_queued_nodes: "نودهای آماده تزریق",
    hint_queued_nodes: "پورت اینباند قابل ویرایش است",
    btn_diagnose: "تست اتصال",
    btn_diagnose_title: "بررسی برقراری ساکس تور و در دسترس بودن پورت‌های اینباند",
    loading_active_instances: "در حال بارگذاری نودهای فعال...",
    btn_execute_inject: "اجرای عملیات تزریق",
    toast_lang_changed: "زبان به فارسی تغییر یافت",
  },
  ru: {
    brand_subtitle: "Автономный оркестратор сети Tor Mesh",
    indicator_engine: "ДВИЖОК:",
    indicator_circuits: "ЦЕПИ:",
    nav_settings: "Настройки",
    nav_settings_title: "Настройки движка",
    nav_inject: "Интеграция PasarGuard",
    nav_inject_title: "Инъекция входящих подключений в PasarGuard",
    nav_logout_title: "Выйти из шлюза",
    metric_active_circuits: "Активные прокси-цепи",
    metric_distributed_socks: "Распределенные конечные точки SOCKS5",
    metric_consensus: "Консенсус и обнаружение Tor",
    discovery_ready: "Готов к запуску.",
    label_max_nodes: "Макс. узлов:",
    btn_start_engine: "Запустить движок",
    btn_stop_engine: "Остановить",
    btn_select_locations: "Выбрать локации",
    btn_locations_title: "Обнаружить и выбрать локации выхода",
    monitoring_title: "Консоль мониторинга узлов в реальном времени",
    monitoring_subtitle: "Проверка работоспособности, IP геолокация и телеметрия задержки TCP",
    search_placeholder: "Поиск страны, порта или статуса...",
    th_country: "СТРАНА",
    th_socks_port: "SOCKS ПОРТ",
    th_exit_node: "ЛОКАЦИЯ ВЫХОДА",
    th_ping: "ПИНГ (TCP)",
    th_status: "СТАТУС",
    lifecycle_title: "Управление жизненным циклом группы A в PasarGuard",
    lifecycle_subtitle: "Управление состоянием пакета, правилами маршрутизации или очистка узлов",
    enable_group_title: "Включить группу A",
    enable_group_desc: "Активировать все входящие слушатели Tor",
    btn_enable: "Включить",
    disable_group_title: "Отключить группу A",
    disable_group_desc: "Приостановить входящие слушатели Tor без удаления",
    btn_disable: "Отключить",
    cleanup_title: "Полная очистка",
    cleanup_desc: "Удалить узлы Tor и правила маршрутизации",
    btn_purge: "Удалить все",
    settings_modal_title: "Настройка ресурсов движка",
    lbl_ping_interval: "Интервал пинга (сек)",
    hint_ping: "Больше = меньше нагрузка на CPU",
    lbl_ram_limit: "Лимит RAM для Tor (МБ)",
    hint_ram: "На каждый процесс прокси (напр. 15)",
    lbl_bw_limit: "Лимит пропускной способности (КБ/с)",
    hint_bw: "0 = без ограничений",
    lbl_workers: "Количество воркеров",
    hint_workers: "0 = авто (оптимально для ядер CPU)",
    lbl_exit_mode: "Выбор выходных реле",
    hint_exit_mode: "Как Tor выбирает выходные узлы в каждой стране",
    opt_exit_country: "Вся страна, взвешенная по консенсусу (рекомендуется)",
    opt_exit_relays: "Закрепить лучшие реле по весу консенсуса",
    lbl_pin_guards: "Закрепить региональные входные узлы",
    hint_pin_guards: "Выключено безопаснее",
    lbl_host_country: "Локация хост-сервера",
    hint_host_country: "Используется только при включенном закреплении",
    host_country_placeholder: "Оставьте пустым для автоопределения IP",
    lbl_preferred_countries: "Предпочитаемые страны выхода",
    hint_preferred_countries: "Будут запущены только выбранные локации",
    btn_scan_network: "Сканировать сеть",
    filter_locations_placeholder: "Фильтр локаций (напр. iceland, jp, nl)",
    btn_select_all: "Выбрать все",
    btn_select_all_title: "Выбрать все обнаруженные локации",
    btn_top10: "Топ 10",
    btn_top10_title: "Выбрать 10 стран с наибольшим числом реле",
    btn_clear: "Очистить",
    btn_clear_title: "Очистить текущий выбор",
    no_locations_selected: "Локации еще не выбраны.",
    countries_placeholder: "Нажмите 'Сканировать сеть' для поиска активных узлов Tor...",
    btn_save_settings: "Сохранить и применить",
    inject_modal_title: "Инъекция в ядро PasarGuard",
    lbl_pasargard_url: "URL панели PasarGuard",
    lbl_pasargard_token: "Токен доступа API администратора",
    lbl_local_tor: "Движок Tor работает на том же сервере, что и Xray (рекомендуется)",
    lbl_remote_tor: "Адрес удаленного движка Tor",
    hint_remote_tor: "Только если Xray находится на другом сервере",
    lbl_target_core: "Целевое ядро",
    hint_target_core: "Выберите целевое ядро Xray/SingBox",
    opt_load_cores_first: "-- Сначала загрузите ядра --",
    btn_load_cores: "Загрузить ядра",
    lbl_template_inbound: "Шаблон входящего",
    hint_template_inbound: "Клонирует только протокол и безопасность",
    opt_load_inbounds_first: "-- Сначала загрузите входящие --",
    btn_load_inbounds: "Загрузить входящие",
    lbl_port_strategy: "Стратегия портов",
    hint_port_strategy: "Как выбирается порт каждого узла для клиентов",
    opt_strategy_base: "Последовательно от базового порта (по умолчанию)",
    opt_strategy_keep: "Сохранять существующие порты",
    opt_strategy_cf: "TLS-порты, совместимые с Cloudflare (2053, 2083, 2087, 2096, 8443, 443)",
    lbl_base_inbound_port: "Базовый порт",
    hint_base_port: "Узлы нумеруются по возрастанию от этого порта",
    btn_renumber: "Перенумеровать",
    btn_renumber_title: "Перенумеровать узлы последовательно от базового порта",
    btn_save_ports: "Сохранить порты",
    btn_save_ports_title: "Запомнить эти порты для будущих инъекций",
    lbl_queued_nodes: "Узлы в очереди на инъекцию",
    hint_queued_nodes: "Входящий порт можно редактировать",
    btn_diagnose: "Проверить подключение",
    btn_diagnose_title: "Проверка доступности SOCKS Tor и портов",
    loading_active_instances: "Загрузка активных экземпляров...",
    btn_execute_inject: "Выполнить инъекцию",
    toast_lang_changed: "Язык изменен на русский",
  },
  zh: {
    brand_subtitle: "自主 Tor 网状网络编排器",
    indicator_engine: "引擎状态:",
    indicator_circuits: "活动线路:",
    nav_settings: "设置",
    nav_settings_title: "引擎资源设置",
    nav_inject: "注入 PasarGuard",
    nav_inject_title: "向 PasarGuard 注入入站配置",
    nav_logout_title: "退出网关登录",
    metric_active_circuits: "活跃代理线路",
    metric_distributed_socks: "分布式 SOCKS5 节点",
    metric_consensus: "Tor 共识与节点发现",
    discovery_ready: "准备启动。",
    label_max_nodes: "最大节点数:",
    btn_start_engine: "启动引擎",
    btn_stop_engine: "停止",
    btn_select_locations: "选择节点位置",
    btn_locations_title: "发现并挑选活跃的出口位置",
    monitoring_title: "实时节点监控控制台",
    monitoring_subtitle: "实时健康验证、IP地理位置及TCP延迟遥测",
    search_placeholder: "搜索国家、端口或状态...",
    th_country: "国家",
    th_socks_port: "SOCKS 端口",
    th_exit_node: "出口节点位置",
    th_ping: "延迟 (TCP)",
    th_status: "健康状态",
    lifecycle_title: "PasarGuard A 组生命周期控制",
    lifecycle_subtitle: "批量管理状态、切换路由规则或在核心间执行清理",
    enable_group_title: "启用 A 组",
    enable_group_desc: "激活所有已注入的 Tor 入站侦听器",
    btn_enable: "启用",
    disable_group_title: "停用 A 组",
    disable_group_desc: "暂停 Tor 入站侦听器（不删除配置）",
    btn_disable: "停用",
    cleanup_title: "批量清除",
    cleanup_desc: "永久移除 Tor 节点及相关路由规则",
    btn_purge: "全部清除",
    settings_modal_title: "引擎资源调优",
    lbl_ping_interval: "Ping 检测间隔（秒）",
    hint_ping: "数值越大 = CPU负载越低",
    lbl_ram_limit: "Tor 内存限制 (MB)",
    hint_ram: "每个代理实例（例如 15）",
    lbl_bw_limit: "带宽限制 (KB/s)",
    hint_bw: "0 = 无限制",
    lbl_workers: "调度工作线程",
    hint_workers: "0 = 自动（根据 CPU 核心优化）",
    lbl_exit_mode: "出口中继选择模式",
    hint_exit_mode: "Tor 如何挑选各国境内的出口",
    opt_exit_country: "整个国家，按共识权重分配（推荐）",
    opt_exit_relays: "按共识权重锁定顶级中继（更严格但也更脆弱）",
    lbl_pin_guards: "固定区域入口守卫",
    hint_pin_guards: "关闭更安全：锁死入口加严格节点可能阻断线路",
    lbl_host_country: "主机服务器位置",
    hint_host_country: "仅在启用守卫固定时生效",
    host_country_placeholder: "留空以进行自动 IP 检测",
    lbl_preferred_countries: "偏好的出口国家/地区",
    hint_preferred_countries: "仅启动勾选的节点位置",
    btn_scan_network: "扫描在线网络",
    filter_locations_placeholder: "过滤位置（如 iceland, jp, nl）",
    btn_select_all: "全选",
    btn_select_all_title: "选择所有已发现的节点位置",
    btn_top10: "前10名",
    btn_top10_title: "选择出口中继最多的 10 个国家/地区",
    btn_clear: "清空",
    btn_clear_title: "清除当前所有选择",
    no_locations_selected: "尚未选择任何节点位置。",
    countries_placeholder: "点击“扫描在线网络”以发现当前活跃的 Tor 出口节点...",
    btn_save_settings: "保存并应用配置",
    inject_modal_title: "注入到 PasarGuard 核心",
    lbl_pasargard_url: "PasarGuard 面板 URL",
    lbl_pasargard_token: "管理员 API 访问令牌",
    lbl_local_tor: "Tor 引擎与 Xray 运行在同一台服务器上（推荐）",
    lbl_remote_tor: "远程 Tor 引擎地址",
    hint_remote_tor: "仅在 Xray 位于另一台服务器时使用",
    lbl_target_core: "目标核心",
    hint_target_core: "选择目标 Xray/SingBox 核心",
    opt_load_cores_first: "-- 请先加载核心列表 --",
    btn_load_cores: "加载核心",
    lbl_template_inbound: "模板入站",
    hint_template_inbound: "仅复制协议与安全配置，其端口会被忽略",
    opt_load_inbounds_first: "-- 请先加载入站列表 --",
    btn_load_inbounds: "加载入站",
    lbl_port_strategy: "入站端口分配策略",
    hint_port_strategy: "如何为每个节点指定面向客户端的端口",
    opt_strategy_base: "从基础端口按顺序递增（默认）",
    opt_strategy_keep: "保留现有主机正在使用的端口",
    opt_strategy_cf: "兼容 Cloudflare 代理的 TLS 端口 (2053, 2083, 2087, 2096, 8443, 443)",
    lbl_base_inbound_port: "基础入站端口",
    hint_base_port: "节点将从该端口开始向上依次递增",
    btn_renumber: "重新编号",
    btn_renumber_title: "从基础端口开始按顺序为所有节点重新编号",
    btn_save_ports: "保存端口",
    btn_save_ports_title: "记住这些端口以便将来注入使用",
    lbl_queued_nodes: "等待注入的节点",
    hint_queued_nodes: "入站端口可直接编辑",
    btn_diagnose: "测试连通性",
    btn_diagnose_title: "检查 Tor SOCKS 存活情况及入站端口是否可达",
    loading_active_instances: "正在加载活跃实例...",
    btn_execute_inject: "执行注入操作",
    toast_lang_changed: "界面语言已切换为中文",
  }
};

let currentLang = "en";

function applyLanguage(lang) {
  if (!I18N_DICT[lang]) lang = "en";
  currentLang = lang;

  document.documentElement.lang = lang;
  document.documentElement.dir = (lang === "fa" ? "rtl" : "ltr");

  // Update navbar badge
  const tagEl = document.getElementById("current-lang-tag");
  if (tagEl) {
    tagEl.textContent = lang.toUpperCase();
  }

  // Update active state in dropdown
  document.querySelectorAll(".lang-option-btn").forEach(btn => {
    if (btn.getAttribute("data-lang") === lang) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  const dict = I18N_DICT[lang];

  // Translate all [data-i18n]
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Translate all [data-i18n-placeholder]
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) {
      el.setAttribute("placeholder", dict[key]);
    }
  });

  // Translate all [data-i18n-title]
  document.querySelectorAll("[data-i18n-title]").forEach(el => {
    const key = el.getAttribute("data-i18n-title");
    if (dict[key]) {
      el.setAttribute("title", dict[key]);
    }
  });
}

async function setLanguage(lang) {
  applyLanguage(lang);
  
  // Close menu
  const menu = document.getElementById("lang-dropdown-menu");
  const container = document.querySelector(".lang-dropdown-container");
  if (menu) menu.classList.add("hidden");
  if (container) container.classList.remove("open");

  // Persist to session and DB via API
  try {
    document.cookie = `user_lang=${lang}; path=/; max-age=${365 * 86400}; SameSite=Lax`;
    await fetch("/api/language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: lang })
    });
  } catch (e) {
    console.error("Failed to save language to session:", e);
  }

  const dict = I18N_DICT[lang];
  if (dict && dict.toast_lang_changed) {
    showToast(dict.toast_lang_changed);
  }
}

async function initLanguage() {
  // Bind toggle button
  const toggleBtn = document.getElementById("btn-lang-toggle");
  const menu = document.getElementById("lang-dropdown-menu");
  const container = document.querySelector(".lang-dropdown-container");

  if (toggleBtn && menu) {
    toggleBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      menu.classList.toggle("hidden");
      if (container) container.classList.toggle("open");
    });

    document.addEventListener("click", (e) => {
      if (!toggleBtn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add("hidden");
        if (container) container.classList.remove("open");
      }
    });
  }

  // Bind option buttons
  document.querySelectorAll(".lang-option-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const selected = btn.getAttribute("data-lang");
      if (selected) {
        setLanguage(selected);
      }
    });
  });

  // Retrieve preferred language from session via /api/language
  let initialLang = "en";
  try {
    const res = await fetch("/api/language");
    if (res.ok) {
      const data = await res.json();
      if (data && data.language && I18N_DICT[data.language]) {
        initialLang = data.language;
      }
    }
  } catch (e) {
    // Fallback to cookie
    const match = document.cookie.match(/user_lang=([a-zA-Z]+)/);
    if (match && I18N_DICT[match[1]]) {
      initialLang = match[1];
    }
  }

  applyLanguage(initialLang);
}

// Poll telemetry
initLanguage();
loadSettings();
statusInterval = setInterval(fetchStatus, 1500);
fetchStatus();

