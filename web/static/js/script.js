
let dadosGlobais = null;
let lastUpdateTime = Date.now();
let refreshTimerInterval = null;

// ── Refresh Timer ──
function startRefreshTimer() {
  if (refreshTimerInterval) clearInterval(refreshTimerInterval);
  lastUpdateTime = Date.now();

  refreshTimerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - lastUpdateTime) / 1000);
    const timerEl = document.getElementById('refresh-timer');
    if (timerEl) {
      if (elapsed < 60) {
        timerEl.textContent = `Atualizado há ${elapsed}s`;
      } else {
        const min = Math.floor(elapsed / 60);
        const sec = elapsed % 60;
        timerEl.textContent = `Atualizado há ${min}m ${sec}s`;
      }
    }
  }, 1000);
}

// ── Fetch Status ──
async function atualizarStatus() {
  try {
    const response = await fetch('/status');
    const data = await response.json();
    dadosGlobais = data;

    let totalOn = 0;
    let totalOff = 0;

    for (const condominioData of Object.values(data)) {
      const cameras = condominioData.cameras || condominioData;
      totalOn += cameras.filter(c => c.status === 'ON').length;
      totalOff += cameras.filter(c => c.status === 'OFF').length;
    }

    const total = totalOn + totalOff;
    const percentOnline = total > 0 ? ((totalOn / total) * 100).toFixed(1) : '0.0';

    // Update summary stat cards
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-online').textContent = totalOn;
    document.getElementById('stat-offline').textContent = totalOff;
    document.getElementById('stat-percent').textContent = percentOnline + '%';

    // Render cards
    renderizarCondominios();

    // Reset refresh timer
    startRefreshTimer();
  } catch (err) {
    console.error('Erro ao buscar status:', err);
    const container = document.getElementById('container-condominios');
    container.innerHTML = '<div style="text-align:center;color:#666;padding:40px;">Erro ao carregar dados.</div>';
    container.classList.remove('loading');
  }
}



// ── Severity classification ──
function getSeverity(offPercent) {
  if (offPercent >= 15) return 'critical';
  if (offPercent >= 10) return 'high';
  if (offPercent >= 5) return 'warning';
  return 'ok';
}

function getOfflineColor(off) {
  if (off >= 15) return 'red';
  if (off >= 8) return 'orange';
  if (off >= 4) return 'yellow';
  if (off > 0) return 'green';
  return 'gray';
}

// ── Sort functions ──
function sortCondominios(entries, sortType) {
  return entries.sort(([nameA, dataA], [nameB, dataB]) => {
    const camerasA = dataA.cameras || dataA;
    const camerasB = dataB.cameras || dataB;
    const offA = camerasA.filter(c => c.status === 'OFF').length;
    const offB = camerasB.filter(c => c.status === 'OFF').length;

    if (sortType === 'alpha') {
      return nameA.localeCompare(nameB);
    }

    if (sortType === 'percent') {
      const pctA = camerasA.length > 0 ? (camerasA.filter(c => c.status === 'ON').length / camerasA.length) : 1;
      const pctB = camerasB.length > 0 ? (camerasB.filter(c => c.status === 'ON').length / camerasB.length) : 1;
      return pctA - pctB;
    }

    // Default: most offline first
    if (offA > 0 && offB === 0) return -1;
    if (offA === 0 && offB > 0) return 1;
    if (offA > 0 && offB > 0) return offB - offA;
    return nameA.localeCompare(nameB);
  });
}

// ── Render Cards ──
function renderizarCondominios() {
  if (!dadosGlobais) return;

  const container = document.getElementById('container-condominios');
  container.innerHTML = '';
  container.classList.remove('loading');

  // Get filter values
  const statusFilter = document.getElementById('status-filter')?.value || 'offline';
  const typeFilter = document.getElementById('type-filter')?.value || 'all';
  const orderFilter = document.getElementById('order-filter')?.value || 'most-offline';

  // Filter entries
  let entries = Object.entries(dadosGlobais);

  // Type filter
  if (typeFilter !== 'all') {
    entries = entries.filter(([, condData]) => {
      const metadata = condData.metadata || {};
      return metadata.empresa?.toString() === typeFilter;
    });
  }

  // Status filter
  if (statusFilter === 'offline') {
    entries = entries.filter(([, condData]) => {
      const cameras = condData.cameras || condData;
      const off = cameras.filter(c => c.status === 'OFF').length;
      return off > 0;
    });
  }

  // Sort
  entries = sortCondominios(entries, orderFilter);

  // Render
  entries.forEach(([name, condData]) => {
    const cameras = condData.cameras || condData;
    const total = cameras.length;
    const on = cameras.filter(c => c.status === 'ON').length;
    const off = total - on;
    const percentOnline = total > 0 ? ((on / total) * 100).toFixed(1) : '100.0';
    const offPercent = total > 0 ? (off / total) * 100 : 0;

    const severity = getSeverity(offPercent);
    const offColor = getOfflineColor(off);

    const card = document.createElement('div');
    card.className = `site-card severity-${severity}`;
    card.addEventListener('click', () => {
      window.location.href = `/condominio/${encodeURIComponent(name)}?condominio=${encodeURIComponent(name)}`;
    });

    // Camera icon SVG
    const cameraIcon = `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>`;

    const offlineText = off > 0
      ? `<span class="card-offline-count color-${offColor}">${off} offline</span>`
      : `<span class="card-offline-count color-green">Tudo online</span>`;

    card.innerHTML = `
      <div class="card-header">
        <div class="card-icon">${cameraIcon}</div>
        <div class="card-title-block">
          <span class="card-name" title="${name}">${name}</span>
          ${offlineText}
        </div>
      </div>
      <div class="card-stats">
        <span class="card-stat-item">
          <span class="card-stat-dot orange"></span>
          Total: ${total}
        </span>
        <span class="card-percent">${percentOnline}%</span>
      </div>
      <span class="card-link">Ver detalhes →</span>
    `;

    container.appendChild(card);
  });

  // Empty state
  if (entries.length === 0) {
    container.innerHTML = '<div style="text-align:center;color:#555;padding:40px;grid-column:1/-1;">Nenhum resultado encontrado para os filtros selecionados.</div>';
  }
}

// ── Event Listeners ──
document.addEventListener('DOMContentLoaded', () => {
  const filters = ['status-filter', 'type-filter', 'ufv-filter', 'order-filter'];

  filters.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('change', () => {
        // When selecting a type, auto-set status to "Todos"
        if (id === 'type-filter' && el.value !== 'all') {
          const statusEl = document.getElementById('status-filter');
          if (statusEl) statusEl.value = 'all';
        }
        renderizarCondominios();
      });
    }
  });
});

// ── Start ──
atualizarStatus();
setInterval(atualizarStatus, 600000); // 10 minutes
