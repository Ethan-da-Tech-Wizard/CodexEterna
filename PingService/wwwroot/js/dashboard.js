// Real-Time Data Pipeline Dashboard JavaScript

// Configuration
const PING_SERVICE_URL = window.location.origin;
const SPORTS_SERVICE_URL = 'http://localhost:5001';
const MAX_TABLE_ROWS = 1000;
const UPDATE_THROTTLE_MS = 100;

// State
let connection = null;
let isPaused = true; // Start paused
let coordinateData = new Map();
let updateQueue = [];
let lastUpdateTime = 0;
let pingGeneratorInterval = null;
let currentSortMode = 'count-desc';

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Real-Time Data Pipeline Dashboard...');

    // Load saved ping data from localStorage
    loadSavedPingData();

    // Initialize SignalR (optional - for real backend connection)
    // await initializeSignalR();

    // Setup event handlers and start ping generator
    setupEventHandlers();

    // Start generating random pings
    startPingGenerator();

    console.log('Dashboard initialized with local ping generation');
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

    // Initialize customization features
    loadSavedSettings();

    // Update pause button initial state
    updatePauseButtonState();

    // Save data before page unload
    window.addEventListener('beforeunload', () => {
        savePingDataToStorage();
    });

    // Auto-save every 10 seconds
    setInterval(() => {
        savePingDataToStorage();
    }, 10000);
}

// ============================================================================
// Random Ping Generation System
// ============================================================================

function startPingGenerator() {
    if (pingGeneratorInterval) {
        clearInterval(pingGeneratorInterval);
    }

    // Generate random pings every second
    pingGeneratorInterval = setInterval(() => {
        if (!isPaused) {
            generateRandomPings();
        }
    }, 1000);

    console.log('Ping generator started');
}

function generateRandomPings() {
    // Generate 5-15 random coordinates per second
    const numPings = Math.floor(Math.random() * 11) + 5;

    for (let i = 0; i < numPings; i++) {
        // Generate random latitude (-90 to 90) and longitude (-180 to 180)
        const latitude = (Math.random() * 180 - 90).toFixed(6);
        const longitude = (Math.random() * 360 - 180).toFixed(6);

        // Create coordinate key
        const key = `${latitude},${longitude}`;

        // Get or create coordinate entry
        if (coordinateData.has(key)) {
            const existing = coordinateData.get(key);
            existing.count++;
            existing.timestamp = new Date().toISOString();
        } else {
            coordinateData.set(key, {
                latitude: parseFloat(latitude),
                longitude: parseFloat(longitude),
                count: 1,
                timestamp: new Date().toISOString()
            });
        }
    }

    // Update the table display
    updatePingTable();

    // Update stats
    document.getElementById('uniqueCoords').textContent = coordinateData.size.toLocaleString();
    const totalPings = Array.from(coordinateData.values()).reduce((sum, coord) => sum + coord.count, 0);
    document.getElementById('totalPings').textContent = totalPings.toLocaleString();
}

// ============================================================================
// Table Sorting Functions
// ============================================================================

function sortTable(mode) {
    currentSortMode = mode;

    const sortedData = Array.from(coordinateData.values()).sort((a, b) => {
        switch (mode) {
            case 'count-desc':
                return b.count - a.count;
            case 'count-asc':
                return a.count - b.count;
            case 'time-desc':
                return new Date(b.timestamp) - new Date(a.timestamp);
            case 'time-asc':
                return new Date(a.timestamp) - new Date(b.timestamp);
            case 'lat-asc':
                return a.latitude - b.latitude;
            case 'lat-desc':
                return b.latitude - a.latitude;
            case 'lng-asc':
                return a.longitude - b.longitude;
            case 'lng-desc':
                return b.longitude - a.longitude;
            default:
                return b.count - a.count;
        }
    });

    updatePingTableWithData(sortedData);
}

function updatePingTable() {
    sortTable(currentSortMode);
}

function updatePingTableWithData(sortedData) {
    const tbody = document.getElementById('pingTableBody');
    const noDataMessage = document.getElementById('noDataMessage');

    if (sortedData.length === 0) {
        tbody.innerHTML = '';
        noDataMessage.style.display = 'block';
        return;
    }

    noDataMessage.style.display = 'none';

    // Limit to MAX_TABLE_ROWS
    const displayData = sortedData.slice(0, MAX_TABLE_ROWS);

    // Build table HTML
    const html = displayData.map(ping => `
        <tr data-key="${ping.latitude},${ping.longitude}">
            <td>${ping.latitude.toFixed(6)}</td>
            <td>${ping.longitude.toFixed(6)}</td>
            <td><strong>${ping.count.toLocaleString()}</strong></td>
            <td>${formatTime(ping.timestamp)}</td>
        </tr>
    `).join('');

    tbody.innerHTML = html;
}

// ============================================================================
// LocalStorage Persistence
// ============================================================================

function savePingDataToStorage() {
    try {
        const dataArray = Array.from(coordinateData.entries());
        localStorage.setItem('codexeterna_ping_data', JSON.stringify(dataArray));
        console.log(`Saved ${dataArray.length} coordinates to localStorage`);
    } catch (error) {
        console.error('Error saving ping data:', error);
    }
}

function loadSavedPingData() {
    try {
        const saved = localStorage.getItem('codexeterna_ping_data');
        if (saved) {
            const dataArray = JSON.parse(saved);
            coordinateData = new Map(dataArray);
            console.log(`Loaded ${coordinateData.size} saved coordinates from localStorage`);

            // Update display
            updatePingTable();

            // Update stats
            document.getElementById('uniqueCoords').textContent = coordinateData.size.toLocaleString();
            const totalPings = Array.from(coordinateData.values()).reduce((sum, coord) => sum + coord.count, 0);
            document.getElementById('totalPings').textContent = totalPings.toLocaleString();
        }
    } catch (error) {
        console.error('Error loading saved ping data:', error);
    }
}

function clearSavedData() {
    if (!confirm('Clear all saved ping data? This cannot be undone.')) {
        return;
    }

    localStorage.removeItem('codexeterna_ping_data');
    coordinateData.clear();
    updatePingTable();

    document.getElementById('uniqueCoords').textContent = '0';
    document.getElementById('totalPings').textContent = '0';

    console.log('Cleared all saved ping data');
}

// ============================================================================
// Updated Control Functions
// ============================================================================

function togglePause() {
    isPaused = !isPaused;
    updatePauseButtonState();
    console.log(isPaused ? 'Paused' : 'Resumed');
}

function updatePauseButtonState() {
    const btn = document.getElementById('pauseBtn');
    const btnText = document.getElementById('pauseBtnText');

    if (isPaused) {
        btn.className = 'btn btn-success';
        btnText.textContent = '▶ Resume';
    } else {
        btn.className = 'btn btn-warning';
        btnText.textContent = '⏸ Pause';
    }
}

function resetSystem() {
    if (!confirm('Reset all ping data? This will clear the current session but keep saved data.')) {
        return;
    }

    // Only clear current data, not localStorage
    coordinateData.clear();
    updatePingTable();

    document.getElementById('uniqueCoords').textContent = '0';
    document.getElementById('totalPings').textContent = '0';

    console.log('Reset current session data');
}

// ============================================================================
// Fixed Sports Data Functions
// ============================================================================

async function fetchSportsData() {
    const sportSelect = document.getElementById('sportSelect');
    const sport = sportSelect.value;

    if (!sport) {
        alert('Please select a sport');
        return;
    }

    const sportsData = document.getElementById('sportsData');
    sportsData.innerHTML = '<div class="no-data"><div class="spinner"></div> Fetching live sports data...</div>';

    try {
        // Try the sports service first
        const response = await fetch(`${SPORTS_SERVICE_URL}/api/sports/fetch?league=${sport}`);

        if (response.ok) {
            const data = await response.json();
            console.log('Sports data fetched:', data);

            // Wait a moment then load stored games
            setTimeout(() => loadStoredGames(), 1000);
        } else {
            // Fallback: Use ESPN API directly if service is down
            await fetchFromESPNDirectly(sport);
        }
    } catch (error) {
        console.error('Sports service unavailable, using ESPN API directly:', error);
        await fetchFromESPNDirectly(sport);
    }
}

async function fetchFromESPNDirectly(sport) {
    const sportsData = document.getElementById('sportsData');

    try {
        // ESPN API endpoint
        const espnUrl = `https://site.api.espn.com/apis/site/v2/sports/${sport}/scoreboard`;
        const response = await fetch(espnUrl);

        if (response.ok) {
            const data = await response.json();
            displayESPNGames(data);
        } else {
            sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Failed to fetch sports data. ESPN API may be unavailable.</div>';
        }
    } catch (error) {
        sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Error: Could not connect to ESPN API. Check your internet connection.</div>';
        console.error('Error fetching from ESPN:', error);
    }
}

function displayESPNGames(data) {
    const sportsData = document.getElementById('sportsData');

    if (!data.events || data.events.length === 0) {
        sportsData.innerHTML = '<div class="no-data">No games found. Try a different sport or check back later.</div>';
        return;
    }

    // Store data with timestamp
    const sportSelect = document.getElementById('sportSelect');
    const sport = sportSelect.value;
    storeSportsDataWithTimestamp(sport, data);

    const html = data.events.map(event => {
        const competition = event.competitions[0];
        const homeTeam = competition.competitors.find(c => c.homeAway === 'home');
        const awayTeam = competition.competitors.find(c => c.homeAway === 'away');

        return `
            <div class="game-card">
                <div class="game-teams">
                    <span>${awayTeam.team.displayName || 'Away Team'}</span>
                    <span class="game-score">${awayTeam.score || '0'} - ${homeTeam.score || '0'}</span>
                    <span>${homeTeam.team.displayName || 'Home Team'}</span>
                </div>
                <div class="game-status">${competition.status.type.detail || 'Status Unknown'}</div>
                <div class="game-date">Fetched: ${new Date().toLocaleString()}</div>
            </div>
        `;
    }).join('');

    sportsData.innerHTML = html;
    updateHistorySummary();
}

// ============================================================================
// Historical Sports Data Management
// ============================================================================

function storeSportsDataWithTimestamp(sport, data) {
    try {
        // Get existing sports history
        let sportsHistory = JSON.parse(localStorage.getItem('codexeterna_sports_history')) || {};

        // Create entry with timestamp
        const timestamp = new Date().toISOString();
        const dateKey = new Date().toISOString().split('T')[0]; // YYYY-MM-DD

        if (!sportsHistory[sport]) {
            sportsHistory[sport] = {};
        }

        if (!sportsHistory[sport][dateKey]) {
            sportsHistory[sport][dateKey] = [];
        }

        // Store the data with timestamp
        sportsHistory[sport][dateKey].push({
            timestamp: timestamp,
            data: data
        });

        // Save back to localStorage
        localStorage.setItem('codexeterna_sports_history', JSON.stringify(sportsHistory));
        console.log(`Stored sports data for ${sport} on ${dateKey}`);
    } catch (error) {
        console.error('Error storing sports data:', error);
    }
}

function filterSportsByDate() {
    const dateFilter = document.getElementById('dateFilter').value;
    const sportSelect = document.getElementById('sportSelect');
    const sport = sportSelect.value;

    if (!dateFilter || !sport) {
        alert('Please select both a sport and a date');
        return;
    }

    try {
        const sportsHistory = JSON.parse(localStorage.getItem('codexeterna_sports_history')) || {};

        if (!sportsHistory[sport] || !sportsHistory[sport][dateFilter]) {
            alert(`No data found for ${sport} on ${dateFilter}`);
            return;
        }

        const dayData = sportsHistory[sport][dateFilter];
        const sportsData = document.getElementById('sportsData');

        // Display all entries for that date
        const html = dayData.map((entry, index) => {
            return `
                <div style="margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color);">
                    <h3 style="color: var(--primary-color); margin-bottom: 15px;">
                        Fetch #${index + 1} - ${new Date(entry.timestamp).toLocaleTimeString()}
                    </h3>
                    ${entry.data.events.map(event => {
                        const competition = event.competitions[0];
                        const homeTeam = competition.competitors.find(c => c.homeAway === 'home');
                        const awayTeam = competition.competitors.find(c => c.homeAway === 'away');

                        return `
                            <div class="game-card">
                                <div class="game-teams">
                                    <span>${awayTeam.team.displayName || 'Away Team'}</span>
                                    <span class="game-score">${awayTeam.score || '0'} - ${homeTeam.score || '0'}</span>
                                    <span>${homeTeam.team.displayName || 'Home Team'}</span>
                                </div>
                                <div class="game-status">${competition.status.type.detail || 'Status Unknown'}</div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
        }).join('');

        sportsData.innerHTML = html || '<div class="no-data">No games found in historical data</div>';
    } catch (error) {
        console.error('Error filtering sports data:', error);
        alert('Error loading historical data');
    }
}

function showAllSportsData() {
    // Clear date filter
    document.getElementById('dateFilter').value = '';

    // Reload current data
    loadStoredGames();
}

function clearSportsHistory() {
    if (!confirm('Clear all historical sports data? This cannot be undone.')) {
        return;
    }

    localStorage.removeItem('codexeterna_sports_history');
    updateHistorySummary();
    document.getElementById('sportsData').innerHTML = '<div class="no-data">Historical data cleared. Fetch new data to begin.</div>';
    console.log('Cleared sports history');
}

function updateHistorySummary() {
    try {
        const sportsHistory = JSON.parse(localStorage.getItem('codexeterna_sports_history')) || {};
        let totalRecords = 0;

        for (const sport in sportsHistory) {
            for (const date in sportsHistory[sport]) {
                totalRecords += sportsHistory[sport][date].length;
            }
        }

        document.getElementById('historyCount').textContent = `${totalRecords} record${totalRecords !== 1 ? 's' : ''}`;
    } catch (error) {
        console.error('Error updating history summary:', error);
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
            // If service is down, try ESPN API directly
            const espnUrl = `https://site.api.espn.com/apis/site/v2/sports/${sport}/scoreboard`;
            const espnResponse = await fetch(espnUrl);
            if (espnResponse.ok) {
                const data = await espnResponse.json();
                displayESPNGames(data);
            } else {
                sportsData.innerHTML = '<div class="no-data" style="color: #ef4444;">Failed to load games</div>';
            }
        }
    } catch (error) {
        console.error('Error loading games:', error);
        // Try ESPN API as fallback
        await fetchFromESPNDirectly(sport);
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
                <span>${game.awayTeam || 'Away Team'}</span>
                <span class="game-score">${game.awayScore || '0'} - ${game.homeScore || '0'}</span>
                <span>${game.homeTeam || 'Home Team'}</span>
            </div>
            <div class="game-status">${game.status || 'Status Unknown'} | ${formatDate(game.date)}</div>
        </div>
    `).join('');

    sportsData.innerHTML = html;
}

async function searchCoordinates() {
    const searchInput = document.getElementById('searchInput');
    const pattern = searchInput.value.trim();

    if (!pattern) {
        // If empty, show all data sorted
        sortTable(currentSortMode);
        return;
    }

    // Filter coordinates that match the search pattern
    const filtered = Array.from(coordinateData.values()).filter(ping => {
        const coordString = `${ping.latitude},${ping.longitude}`;
        return coordString.includes(pattern);
    });

    if (filtered.length === 0) {
        alert(`No coordinates found matching "${pattern}"`);
        return;
    }

    // Sort filtered results
    filtered.sort((a, b) => b.count - a.count);

    updatePingTableWithData(filtered);
    console.log(`Found ${filtered.length} coordinates matching "${pattern}"`);
}

// ============================================================================
// Tab Switching Functionality
// ============================================================================

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Update tab panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    // Activate selected tab
    if (tabName === 'ping') {
        document.getElementById('pingTab').classList.add('active');
        document.getElementById('pingPanel').classList.add('active');
    } else if (tabName === 'sports') {
        document.getElementById('sportsTab').classList.add('active');
        document.getElementById('sportsPanel').classList.add('active');
        updateHistorySummary();
    }
}

// ============================================================================
// Theme & Customization Features
// ============================================================================

// Professional Theme Presets
const THEME_PRESETS = {
    'executive-dark': {
        color1: '#1a1d29',
        color2: '#0f1117',
        primaryColor: '#5b9bd5',
        successColor: '#70ad47',
        warningColor: '#ffc000',
        dangerColor: '#e74c3c',
        infoColor: '#7986cb'
    },
    'corporate-blue': {
        color1: '#1e3a5f',
        color2: '#0f1e3a',
        primaryColor: '#4a90e2',
        successColor: '#7cb342',
        warningColor: '#fb8c00',
        dangerColor: '#e53935',
        infoColor: '#5c6bc0'
    },
    'clean-light': {
        color1: '#e8eaf6',
        color2: '#c5cae9',
        primaryColor: '#3f51b5',
        successColor: '#43a047',
        warningColor: '#fb8c00',
        dangerColor: '#e53935',
        infoColor: '#5c6bc0'
    },
    'minimalist-slate': {
        color1: '#37474f',
        color2: '#263238',
        primaryColor: '#78909c',
        successColor: '#66bb6a',
        warningColor: '#ffb74d',
        dangerColor: '#ef5350',
        infoColor: '#90a4ae'
    },
    'professional-navy': {
        color1: '#0d1b2a',
        color2: '#1b263b',
        primaryColor: '#4a7ba7',
        successColor: '#52b788',
        warningColor: '#f77f00',
        dangerColor: '#d62828',
        infoColor: '#6c757d'
    },
    'modern-charcoal': {
        color1: '#2d3436',
        color2: '#1e272e',
        primaryColor: '#74b9ff',
        successColor: '#55efc4',
        warningColor: '#fdcb6e',
        dangerColor: '#ff7675',
        infoColor: '#a29bfe'
    }
};

// Settings Panel Toggle
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('active');
}

// Apply Theme Preset
function applyPreset(presetName) {
    const preset = THEME_PRESETS[presetName];
    if (!preset) return;

    const root = document.documentElement;
    root.style.setProperty('--bg-color-1', preset.color1);
    root.style.setProperty('--bg-color-2', preset.color2);
    root.style.setProperty('--primary-color', preset.primaryColor);
    root.style.setProperty('--success-color', preset.successColor);
    root.style.setProperty('--warning-color', preset.warningColor);
    root.style.setProperty('--danger-color', preset.dangerColor);
    root.style.setProperty('--info-color', preset.infoColor);

    // Update color pickers
    document.getElementById('customColor1').value = preset.color1;
    document.getElementById('customColor2').value = preset.color2;

    // Update panel backgrounds
    updatePanelColors();

    // Save settings
    saveSettings();

    console.log(`Applied theme: ${presetName}`);
}

// Apply Custom Gradient
function applyCustomGradient() {
    const color1 = document.getElementById('customColor1').value;
    const color2 = document.getElementById('customColor2').value;
    const angle = document.getElementById('gradientAngle').value;

    const root = document.documentElement;
    root.style.setProperty('--bg-color-1', color1);
    root.style.setProperty('--bg-color-2', color2);
    root.style.setProperty('--bg-gradient-angle', `${angle}deg`);

    document.getElementById('angleValue').textContent = angle;

    // Update panel backgrounds
    updatePanelColors();

    // Save settings
    saveSettings();
}

// Update Panel Colors
function updatePanelColors() {
    const color1 = getComputedStyle(document.documentElement).getPropertyValue('--bg-color-1').trim();
    const opacity = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--panel-bg').split(',')[3]) || 0.95;

    // Convert hex to RGB and apply opacity
    const rgb = hexToRgb(color1);
    if (rgb) {
        const root = document.documentElement;
        root.style.setProperty('--panel-bg', `rgba(${rgb.r + 10}, ${rgb.g + 8}, ${rgb.b + 8}, ${opacity})`);
        root.style.setProperty('--card-bg', `rgba(${rgb.r + 20}, ${rgb.g + 16}, ${rgb.b + 12}, ${opacity - 0.15})`);
        root.style.setProperty('--darker-bg', `rgba(${Math.max(0, rgb.r - 10)}, ${Math.max(0, rgb.g - 8)}, ${Math.max(0, rgb.b - 8)}, ${opacity})`);
    }
}

// Hex to RGB Conversion
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}


// Toggle Blur Effect
function toggleBlur() {
    const enabled = document.getElementById('blurEnabled').checked;

    if (enabled) {
        document.body.classList.remove('blur-disabled');
        document.documentElement.style.setProperty('--blur-amount', '12px');
    } else {
        document.body.classList.add('blur-disabled');
        document.documentElement.style.setProperty('--blur-amount', '0px');
    }

    saveSettings();
}

// Toggle Animations
function toggleAnimations() {
    const enabled = document.getElementById('animationsEnabled').checked;

    if (enabled) {
        document.body.classList.remove('animations-disabled');
        document.documentElement.style.setProperty('--animation-enabled', '1');
    } else {
        document.body.classList.add('animations-disabled');
        document.documentElement.style.setProperty('--animation-enabled', '0');
    }

    saveSettings();
}

// Update Opacity
function updateOpacity() {
    const opacity = document.getElementById('panelOpacity').value;
    document.getElementById('opacityValue').textContent = opacity;

    const opacityDecimal = opacity / 100;
    const color1 = getComputedStyle(document.documentElement).getPropertyValue('--bg-color-1').trim();
    const rgb = hexToRgb(color1);

    if (rgb) {
        const root = document.documentElement;
        root.style.setProperty('--panel-bg', `rgba(${rgb.r + 10}, ${rgb.g + 8}, ${rgb.b + 8}, ${opacityDecimal})`);
        root.style.setProperty('--card-bg', `rgba(${rgb.r + 20}, ${rgb.g + 16}, ${rgb.b + 12}, ${opacityDecimal - 0.15})`);
        root.style.setProperty('--darker-bg', `rgba(${Math.max(0, rgb.r - 10)}, ${Math.max(0, rgb.g - 8)}, ${Math.max(0, rgb.b - 8)}, ${opacityDecimal})`);
    }

    saveSettings();
}

// Save Settings to LocalStorage
function saveSettings() {
    const settings = {
        bgColor1: document.getElementById('customColor1').value,
        bgColor2: document.getElementById('customColor2').value,
        gradientAngle: document.getElementById('gradientAngle').value,
        blurEnabled: document.getElementById('blurEnabled').checked,
        animationsEnabled: document.getElementById('animationsEnabled').checked,
        panelOpacity: document.getElementById('panelOpacity').value
    };

    localStorage.setItem('codexeterna_settings', JSON.stringify(settings));
}

// Load Saved Settings
function loadSavedSettings() {
    const saved = localStorage.getItem('codexeterna_settings');
    if (!saved) return;

    try {
        const settings = JSON.parse(saved);

        // Apply saved values
        if (settings.bgColor1) document.getElementById('customColor1').value = settings.bgColor1;
        if (settings.bgColor2) document.getElementById('customColor2').value = settings.bgColor2;
        if (settings.gradientAngle) {
            document.getElementById('gradientAngle').value = settings.gradientAngle;
            document.getElementById('angleValue').textContent = settings.gradientAngle;
        }
        if (settings.panelOpacity) {
            document.getElementById('panelOpacity').value = settings.panelOpacity;
            document.getElementById('opacityValue').textContent = settings.panelOpacity;
        }

        document.getElementById('blurEnabled').checked = settings.blurEnabled !== false;
        document.getElementById('animationsEnabled').checked = settings.animationsEnabled !== false;

        // Apply settings
        applyCustomGradient();

        if (settings.blurEnabled === false) {
            toggleBlur();
        }

        if (settings.animationsEnabled === false) {
            toggleAnimations();
        }

        console.log('Loaded saved settings');
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Reset Settings to Default
function resetSettings() {
    if (!confirm('Reset all customizations to default?')) {
        return;
    }

    // Clear localStorage
    localStorage.removeItem('codexeterna_settings');

    // Reset to Executive Dark theme
    applyPreset('executive-dark');

    // Reset controls
    document.getElementById('gradientAngle').value = 135;
    document.getElementById('angleValue').textContent = 135;
    document.getElementById('panelOpacity').value = 95;
    document.getElementById('opacityValue').textContent = 95;
    document.getElementById('blurEnabled').checked = true;
    document.getElementById('animationsEnabled').checked = true;

    // Reset effects
    document.body.classList.remove('blur-disabled', 'animations-disabled');
    document.documentElement.style.setProperty('--blur-amount', '10px');
    document.documentElement.style.setProperty('--animation-enabled', '1');

    updateOpacity();

    console.log('Settings reset to default');
}

// ============================================================================
// Expose functions globally for onclick handlers
// ============================================================================

// Core functions
window.togglePause = togglePause;
window.resetSystem = resetSystem;
window.reconnect = reconnect;
window.searchCoordinates = searchCoordinates;
window.fetchSportsData = fetchSportsData;
window.loadStoredGames = loadStoredGames;

// Ping data functions
window.sortTable = sortTable;
window.clearSavedData = clearSavedData;

// Tab navigation
window.switchTab = switchTab;

// Sports history functions
window.filterSportsByDate = filterSportsByDate;
window.showAllSportsData = showAllSportsData;
window.clearSportsHistory = clearSportsHistory;
window.updateHistorySummary = updateHistorySummary;

// Customization functions
window.toggleSettings = toggleSettings;
window.applyPreset = applyPreset;
window.applyCustomGradient = applyCustomGradient;
window.toggleBlur = toggleBlur;
window.toggleAnimations = toggleAnimations;
window.updateOpacity = updateOpacity;
window.resetSettings = resetSettings;

console.log('Dashboard JavaScript - Professional Edition Loaded Successfully');
