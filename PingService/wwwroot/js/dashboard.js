// Real-Time Data Pipeline Dashboard JavaScript

// Configuration
const PING_SERVICE_URL = window.location.origin;
const SPORTS_SERVICE_URL = 'http://localhost:5001';
const MAX_TABLE_ROWS = 1000;
const UPDATE_THROTTLE_MS = 100;

// State
let connection = null;
let isPaused = false;
let coordinateData = new Map();
let updateQueue = [];
let lastUpdateTime = 0;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Real-Time Data Pipeline Dashboard...');
    await initializeSignalR();
    setupEventHandlers();
});

// ============================================================================
// SignalR Connection Management
// ============================================================================

async function initializeSignalR() {
    try {
        // Create SignalR connection
        connection = new signalR.HubConnectionBuilder()
            .withUrl(`${PING_SERVICE_URL}/hubs/ping`)
            .withAutomaticReconnect({
                nextRetryDelayInMilliseconds: retryContext => {
                    // Exponential backoff: 2s, 4s, 8s, 16s, 30s
                    return Math.min(1000 * Math.pow(2, retryContext.previousRetryCount), 30000);
                }
            })
            .configureLogging(signalR.LogLevel.Information)
            .build();

        // Set up event handlers
        connection.on('ReceivePingBatch', handlePingBatch);
        connection.on('ReceiveStats', handleStats);

        // Connection lifecycle events
        connection.onreconnecting(error => {
            console.warn('SignalR reconnecting...', error);
            updateConnectionStatus('Reconnecting...', 'warning');
        });

        connection.onreconnected(connectionId => {
            console.log('SignalR reconnected:', connectionId);
            updateConnectionStatus('Connected', 'success');
        });

        connection.onclose(error => {
            console.error('SignalR connection closed:', error);
            updateConnectionStatus('Disconnected', 'error');
        });

        // Start connection
        await connection.start();
        console.log('SignalR connected successfully');
        updateConnectionStatus('Connected', 'success');

    } catch (error) {
        console.error('Failed to initialize SignalR:', error);
        updateConnectionStatus('Connection Failed', 'error');
    }
}

async function reconnect() {
    if (connection && connection.state === signalR.HubConnectionState.Connected) {
        console.log('Already connected');
        return;
    }

    try {
        updateConnectionStatus('Connecting...', 'warning');
        await connection.start();
        console.log('Reconnected successfully');
        updateConnectionStatus('Connected', 'success');
    } catch (error) {
        console.error('Reconnection failed:', error);
        updateConnectionStatus('Connection Failed', 'error');
    }
}

// ============================================================================
// SignalR Event Handlers
// ============================================================================

function handlePingBatch(updates) {
    // Add updates to queue for throttled processing
    updateQueue.push(...updates);

    // Throttle updates to avoid overwhelming the DOM
    const now = Date.now();
    if (now - lastUpdateTime >= UPDATE_THROTTLE_MS) {
        processUpdateQueue();
        lastUpdateTime = now;
    }
}

function processUpdateQueue() {
    if (updateQueue.length === 0) return;

    // Process all queued updates
    const batch = updateQueue.splice(0, updateQueue.length);

    batch.forEach(update => {
        const key = `${update.latitude},${update.longitude}`;
        coordinateData.set(key, {
            latitude: update.latitude,
            longitude: update.longitude,
            count: update.count,
            timestamp: update.timestamp
        });
    });

    // Update the table
    updatePingTable();
}

function handleStats(stats) {
    // Update stat cards
    updateStatValue('totalPings', stats.totalPingsGenerated.toLocaleString());
    updateStatValue('uniqueCoords', stats.uniqueCoordinates.toLocaleString());
    updateStatValue('pingsPerSecond', stats.pingsPerSecond.toLocaleString());
    updateStatValue('uptime', formatUptime(stats.uptime));
    updateStatValue('memoryUsage', stats.memoryUsageMB.toLocaleString());

    // Update pause status
    isPaused = stats.isPaused;
    updatePauseStatus(isPaused);
}

// ============================================================================
// UI Update Functions
// ============================================================================

function updateStatValue(elementId, value) {
    const element = document.getElementById(elementId);
    if (element && element.textContent !== value) {
        element.textContent = value;
        element.classList.add('updated');
        setTimeout(() => element.classList.remove('updated'), 500);
    }
}

function updateConnectionStatus(status, type) {
    const element = document.getElementById('connectionStatus');
    if (element) {
        element.textContent = status;
        element.className = 'stat-value';
        if (type === 'success') element.style.color = '#10b981';
        else if (type === 'warning') element.style.color = '#f59e0b';
        else if (type === 'error') element.style.color = '#ef4444';
    }
}

function updatePauseStatus(paused) {
    const statusDot = document.querySelector('#pingStatus .status-dot');
    const statusText = document.querySelector('#pingStatus .status-text');
    const pauseBtn = document.getElementById('pauseBtnText');

    if (paused) {
        statusDot.className = 'status-dot paused';
        statusText.textContent = 'Paused';
        pauseBtn.textContent = 'Resume';
    } else {
        statusDot.className = 'status-dot running';
        statusText.textContent = 'Running';
        pauseBtn.textContent = 'Pause';
    }
}

function updatePingTable() {
    const tbody = document.getElementById('pingTableBody');
    const noDataMessage = document.getElementById('noDataMessage');

    if (coordinateData.size === 0) {
        tbody.innerHTML = '';
        noDataMessage.style.display = 'block';
        return;
    }

    noDataMessage.style.display = 'none';

    // Convert to array and sort by count (descending)
    const sortedData = Array.from(coordinateData.values())
        .sort((a, b) => b.count - a.count)
        .slice(0, MAX_TABLE_ROWS);

    // Build table HTML
    const html = sortedData.map(ping => `
        <tr data-key="${ping.latitude},${ping.longitude}">
            <td>${ping.latitude.toFixed(6)}</td>
            <td>${ping.longitude.toFixed(6)}</td>
            <td>${ping.count.toLocaleString()}</td>
            <td>${formatTime(ping.timestamp)}</td>
        </tr>
    `).join('');

    tbody.innerHTML = html;
}

// ============================================================================
// Control Functions
// ============================================================================

async function togglePause() {
    try {
        const endpoint = isPaused ? '/api/ping/resume' : '/api/ping/pause';
        const response = await fetch(`${PING_SERVICE_URL}${endpoint}`, {
            method: 'POST'
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data.message);
            isPaused = !isPaused;
            updatePauseStatus(isPaused);
        } else {
            console.error('Failed to toggle pause:', response.statusText);
        }
    } catch (error) {
        console.error('Error toggling pause:', error);
    }
}

async function resetSystem() {
    if (!confirm('Are you sure you want to reset all data?')) {
        return;
    }

    try {
        const response = await fetch(`${PING_SERVICE_URL}/api/ping/reset`, {
            method: 'POST'
        });

        if (response.ok) {
            coordinateData.clear();
            updatePingTable();
            console.log('System reset successfully');
        } else {
            console.error('Failed to reset:', response.statusText);
        }
    } catch (error) {
        console.error('Error resetting system:', error);
    }
}

async function searchCoordinates() {
    const searchInput = document.getElementById('searchInput');
    const pattern = searchInput.value.trim();

    if (!pattern) {
        alert('Please enter a search pattern');
        return;
    }

    try {
        const response = await fetch(
            `${PING_SERVICE_URL}/api/ping/search?pattern=${encodeURIComponent(pattern)}&limit=100`
        );

        if (response.ok) {
            const results = await response.json();
            displaySearchResults(results);
        } else {
            console.error('Search failed:', response.statusText);
        }
    } catch (error) {
        console.error('Error searching coordinates:', error);
    }
}

async function loadTopCoordinates() {
    try {
        const response = await fetch(`${PING_SERVICE_URL}/api/ping/top?count=100`);

        if (response.ok) {
            const results = await response.json();
            displaySearchResults(results);
        } else {
            console.error('Failed to load top coordinates:', response.statusText);
        }
    } catch (error) {
        console.error('Error loading top coordinates:', error);
    }
}

function displaySearchResults(results) {
    coordinateData.clear();

    results.forEach(ping => {
        const key = `${ping.latitude},${ping.longitude}`;
        coordinateData.set(key, {
            latitude: ping.latitude,
            longitude: ping.longitude,
            count: ping.count,
            timestamp: ping.lastSeen
        });
    });

    updatePingTable();
}

// ============================================================================
// Sports Data Functions
// ============================================================================

async function fetchSportsData() {
    const sportSelect = document.getElementById('sportSelect');
    const sport = sportSelect.value;

    if (!sport) {
        alert('Please select a sport');
        return;
    }

    const sportsData = document.getElementById('sportsData');
    sportsData.innerHTML = '<div class="no-data"><div class="spinner"></div> Fetching data...</div>';

    try {
        const response = await fetch(`${SPORTS_SERVICE_URL}/api/sports/fetch?league=${sport}`);

        if (response.ok) {
            const data = await response.json();
            console.log('Sports data fetched:', data);

            // Load and display the fetched games
            await loadStoredGames();
        } else {
            sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Failed to fetch sports data. Make sure the Sports Service is running.</div>';
            console.error('Failed to fetch sports data:', response.statusText);
        }
    } catch (error) {
        sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Error: Could not connect to Sports Service</div>';
        console.error('Error fetching sports data:', error);
    }
}

async function loadStoredGames() {
    const sportSelect = document.getElementById('sportSelect');
    const sport = sportSelect.value;

    if (!sport) {
        alert('Please select a sport');
        return;
    }

    const sportsData = document.getElementById('sportsData');
    sportsData.innerHTML = '<div class="no-data"><div class="spinner"></div> Loading...</div>';

    try {
        const response = await fetch(`${SPORTS_SERVICE_URL}/api/sports/games?league=${sport}`);

        if (response.ok) {
            const games = await response.json();
            displayGames(games);
        } else {
            sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Failed to load games</div>';
            console.error('Failed to load games:', response.statusText);
        }
    } catch (error) {
        sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Error loading games</div>';
        console.error('Error loading games:', error);
    }
}

function displayGames(games) {
    const sportsData = document.getElementById('sportsData');

    if (!games || games.length === 0) {
        sportsData.innerHTML = '<div class="no-data">No games found. Try fetching latest data.</div>';
        return;
    }

    const html = games.map(game => `
        <div class="game-card">
            <div class="game-teams">
                <span>${game.homeTeam}</span>
                <span class="game-score">${game.homeScore} - ${game.awayScore}</span>
                <span>${game.awayTeam}</span>
            </div>
            <div class="game-status">${game.status} | ${formatDate(game.date)}</div>
        </div>
    `).join('');

    sportsData.innerHTML = html;
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatUptime(uptime) {
    // uptime format: "00:01:23.4567890"
    if (!uptime) return '00:00:00';

    const parts = uptime.split(':');
    if (parts.length >= 3) {
        const hours = parts[0];
        const minutes = parts[1];
        const seconds = parts[2].split('.')[0];
        return `${hours}:${minutes}:${seconds}`;
    }

    return uptime;
}

function formatTime(timestamp) {
    if (!timestamp) return 'N/A';

    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    return date.toLocaleString();
}

function setupEventHandlers() {
    // Allow Enter key to trigger search
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchCoordinates();
        }
    });
}

// ============================================================================
// Expose functions globally for onclick handlers
// ============================================================================

window.togglePause = togglePause;
window.resetSystem = resetSystem;
window.reconnect = reconnect;
window.searchCoordinates = searchCoordinates;
window.loadTopCoordinates = loadTopCoordinates;
window.fetchSportsData = fetchSportsData;
window.loadStoredGames = loadStoredGames;

console.log('Dashboard JavaScript loaded successfully');
