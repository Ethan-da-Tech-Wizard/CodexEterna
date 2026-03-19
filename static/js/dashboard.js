// ── Socket.IO connection ────────────────────────────────────────────────────
const socket = io();

const elStatus   = document.getElementById('connection-status');
const elTotal    = document.getElementById('total-pings');
const elUnique   = document.getElementById('unique-coords');
const elRate     = document.getElementById('pings-per-sec');
const elUptime   = document.getElementById('uptime');
const pingTbody  = document.getElementById('ping-tbody');
const sportsTbody = document.getElementById('sports-tbody');

socket.on('connect',    () => setStatus(true));
socket.on('disconnect', () => setStatus(false));

function setStatus(online) {
  elStatus.textContent  = online ? 'Live' : 'Disconnected';
  elStatus.className    = 'badge ' + (online ? 'badge-online' : 'badge-offline');
}

// ── Ping stats stream ───────────────────────────────────────────────────────
socket.on('stats', (s) => {
  elTotal.textContent  = s.total.toLocaleString();
  elUnique.textContent = s.unique.toLocaleString();
  elRate.textContent   = s.rate.toLocaleString();
  elUptime.textContent = formatUptime(s.uptime);
});

// ── Ping batch — only update table when not filtered ───────────────────────
let filterActive = false;

socket.on('batch', (rows) => {
  if (filterActive) return;
  renderPingRows(rows);
});

function renderPingRows(rows) {
  // rows: [{key, count, lat, lon}]
  const frag = document.createDocumentFragment();
  rows.slice(0, 100).forEach((r, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${i+1}</td><td>${r.key}</td><td>${r.count.toLocaleString()}</td><td>${hemisphere(r.lat, r.lon)}</td>`;
    frag.appendChild(tr);
  });
  pingTbody.innerHTML = '';
  pingTbody.appendChild(frag);
}

function hemisphere(lat, lon) {
  const ns = lat >= 0 ? 'N' : 'S';
  const ew = lon >= 0 ? 'E' : 'W';
  return ns + ew;
}

// ── Ping controls ───────────────────────────────────────────────────────────
document.getElementById('btn-pause').addEventListener('click', async () => {
  await api('/api/ping/pause', 'POST');
  document.getElementById('btn-pause').disabled  = true;
  document.getElementById('btn-resume').disabled = false;
});

document.getElementById('btn-resume').addEventListener('click', async () => {
  await api('/api/ping/resume', 'POST');
  document.getElementById('btn-pause').disabled  = false;
  document.getElementById('btn-resume').disabled = true;
});

document.getElementById('btn-reset').addEventListener('click', async () => {
  if (!confirm('Reset all ping data?')) return;
  await api('/api/ping/reset', 'POST');
  pingTbody.innerHTML = '';
});

// ── Ping filters ────────────────────────────────────────────────────────────
document.getElementById('btn-apply-ping-filter').addEventListener('click', applyPingFilter);
document.getElementById('btn-clear-ping-filter').addEventListener('click', clearPingFilter);

async function applyPingFilter() {
  const params = new URLSearchParams();
  const hemisphere = document.getElementById('f-hemisphere').value;
  const minCount   = document.getElementById('f-min-count').value;
  const maxCount   = document.getElementById('f-max-count').value;
  const limit      = document.getElementById('f-limit').value;
  const minLat     = document.getElementById('f-min-lat').value;
  const maxLat     = document.getElementById('f-max-lat').value;
  const minLon     = document.getElementById('f-min-lon').value;
  const maxLon     = document.getElementById('f-max-lon').value;

  if (hemisphere) params.set('hemisphere', hemisphere);
  if (minCount)   params.set('min_count', minCount);
  if (maxCount)   params.set('max_count', maxCount);
  if (limit)      params.set('limit', limit);
  if (minLat)     params.set('min_lat', minLat);
  if (maxLat)     params.set('max_lat', maxLat);
  if (minLon)     params.set('min_lon', minLon);
  if (maxLon)     params.set('max_lon', maxLon);

  const data = await api(`/api/ping/filter?${params}`);
  if (data) {
    filterActive = true;
    renderPingRows(data.results || []);
  }
}

function clearPingFilter() {
  filterActive = false;
  ['f-hemisphere','f-min-count','f-max-count','f-min-lat','f-max-lat','f-min-lon','f-max-lon'].forEach(id => {
    const el = document.getElementById(id);
    if (el.tagName === 'SELECT') el.value = '';
    else el.value = '';
  });
  document.getElementById('f-limit').value = '100';
}

// ── Ping aggregate ──────────────────────────────────────────────────────────
async function loadPingAggregate(groupBy) {
  const data = await api(`/api/ping/aggregate?group_by=${groupBy}`);
  if (data) showModal(`Ping Aggregate — ${groupBy}`, data);
}

// ── Sports: fetch ───────────────────────────────────────────────────────────
document.getElementById('btn-fetch-sports').addEventListener('click', async () => {
  const league = document.getElementById('sport-league').value;
  const status = document.getElementById('sports-status');
  status.textContent = 'Fetching…';
  status.className   = 'status-msg';

  const data = await api(`/api/sports/fetch?league=${encodeURIComponent(league)}`, 'POST');
  if (data) {
    status.textContent = `✓ ${data.created} new, ${data.updated} updated`;
    status.className   = 'status-msg ok';
    loadSportsGames();
  } else {
    status.textContent = 'Fetch failed';
    status.className   = 'status-msg err';
  }
});

// ── Sports: load games ──────────────────────────────────────────────────────
async function loadSportsGames(extraParams = '') {
  const league = document.getElementById('sport-league').value;
  const data = await api(`/api/sports/games?league=${encodeURIComponent(league)}${extraParams}`);
  if (data) renderSportsRows(data.games || []);
}

// Load on league change
document.getElementById('sport-league').addEventListener('change', () => loadSportsGames());

function renderSportsRows(games) {
  const frag = document.createDocumentFragment();
  games.forEach(g => {
    const tr = document.createElement('tr');
    const homeScore = g.home_score != null ? g.home_score : '–';
    const awayScore = g.away_score != null ? g.away_score : '–';
    const date = g.game_date ? new Date(g.game_date).toLocaleDateString() : '–';
    tr.innerHTML = `
      <td>${g.league || '–'}</td>
      <td>${g.home_team || '–'}</td>
      <td class="score">${homeScore} – ${awayScore}</td>
      <td>${g.away_team || '–'}</td>
      <td><span class="badge ${statusClass(g.status)}">${g.status || '–'}</span></td>
      <td>${date}</td>
    `;
    frag.appendChild(tr);
  });
  sportsTbody.innerHTML = '';
  sportsTbody.appendChild(frag);
}

function statusClass(s) {
  if (!s) return '';
  const l = s.toLowerCase();
  if (l === 'live' || l === 'in progress') return 'badge-live';
  if (l === 'final') return 'badge-final';
  return 'badge-sched';
}

// ── Sports filters ──────────────────────────────────────────────────────────
document.getElementById('btn-apply-sports-filter').addEventListener('click', applySportsFilter);
document.getElementById('btn-clear-sports-filter').addEventListener('click', () => {
  ['sf-status','sf-min-score','sf-max-score','sf-close-margin'].forEach(id => {
    document.getElementById(id).value = '';
  });
  loadSportsGames();
});

async function applySportsFilter() {
  const params = new URLSearchParams();
  const league    = document.getElementById('sport-league').value;
  const status    = document.getElementById('sf-status').value;
  const minScore  = document.getElementById('sf-min-score').value;
  const maxScore  = document.getElementById('sf-max-score').value;
  const margin    = document.getElementById('sf-close-margin').value;

  params.set('league', league);
  if (status)   params.set('status', status);
  if (minScore) params.set('min_score', minScore);
  if (maxScore) params.set('max_score', maxScore);
  if (margin)   params.set('close_game_threshold', margin);

  const data = await api(`/api/sports/filter?${params}`);
  if (data) renderSportsRows(data.games || []);
}

// ── Sports quick views ──────────────────────────────────────────────────────
document.getElementById('btn-high-scoring').addEventListener('click', async () => {
  const league = document.getElementById('sport-league').value;
  const data = await api(`/api/sports/high-scoring?league=${encodeURIComponent(league)}`);
  if (data) renderSportsRows(data.games || []);
});

document.getElementById('btn-close-games').addEventListener('click', async () => {
  const league = document.getElementById('sport-league').value;
  const data = await api(`/api/sports/close-games?league=${encodeURIComponent(league)}`);
  if (data) renderSportsRows(data.games || []);
});

async function loadSportsAggregate() {
  const league = document.getElementById('sport-league').value;
  const data = await api(`/api/sports/aggregate?league=${encodeURIComponent(league)}`);
  if (data) showModal('Sports Summary', data);
}

// ── Helpers ─────────────────────────────────────────────────────────────────
async function api(url, method = 'GET') {
  try {
    const res = await fetch(url, { method });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

function formatUptime(seconds) {
  if (seconds < 60)   return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds/60)}m ${Math.round(seconds%60)}s`;
  return `${Math.floor(seconds/3600)}h ${Math.floor((seconds%3600)/60)}m`;
}

// ── Modal ───────────────────────────────────────────────────────────────────
function showModal(title, data) {
  document.getElementById('agg-title').textContent   = title;
  document.getElementById('agg-content').textContent = JSON.stringify(data, null, 2);
  document.getElementById('agg-modal').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('agg-modal').classList.add('hidden');
}

document.getElementById('agg-modal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeModal();
});

// ── Init ─────────────────────────────────────────────────────────────────────
loadSportsGames();
