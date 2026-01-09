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

    // Initialize customization features
    loadSavedSettings();
    initializeParticles();
}

// ============================================================================
// Theme & Customization Features
// ============================================================================

// Theme Presets
const THEME_PRESETS = {
    'cozy-cafe': {
        color1: '#2c1810',
        color2: '#1a0f0a',
        primaryColor: '#d4a574',
        successColor: '#7fc8a9',
        warningColor: '#f0b67f',
        dangerColor: '#e17b77',
        infoColor: '#89b4f8'
    },
    'midnight-coder': {
        color1: '#0f0f23',
        color2: '#1a1a2e',
        primaryColor: '#64b5f6',
        successColor: '#81c784',
        warningColor: '#ffb74d',
        dangerColor: '#e57373',
        infoColor: '#ba68c8'
    },
    'forest-retreat': {
        color1: '#1a2f1a',
        color2: '#0d1f0d',
        primaryColor: '#8bc34a',
        successColor: '#4caf50',
        warningColor: '#ffb300',
        dangerColor: '#f4511e',
        infoColor: '#26c6da'
    },
    'sunset-lounge': {
        color1: '#2d1b2e',
        color2: '#1f0d1f',
        primaryColor: '#ff7043',
        successColor: '#66bb6a',
        warningColor: '#ffca28',
        dangerColor: '#ef5350',
        infoColor: '#ab47bc'
    },
    'ocean-breeze': {
        color1: '#0d1f2d',
        color2: '#081220',
        primaryColor: '#4dd0e1',
        successColor: '#26a69a',
        warningColor: '#ffa726',
        dangerColor: '#ef5350',
        infoColor: '#5c6bc0'
    },
    'lavender-dreams': {
        color1: '#2d1f3f',
        color2: '#1a0f2e',
        primaryColor: '#ce93d8',
        successColor: '#81c784',
        warningColor: '#ffb74d',
        dangerColor: '#ef5350',
        infoColor: '#7986cb'
    },
    'retro-synthwave': {
        color1: '#1a0033',
        color2: '#2d0052',
        primaryColor: '#ff00ff',
        successColor: '#00ff00',
        warningColor: '#ffff00',
        dangerColor: '#ff0055',
        infoColor: '#00ffff'
    },
    'minimal-zen': {
        color1: '#2b2d2f',
        color2: '#1a1c1e',
        primaryColor: '#a8a8a8',
        successColor: '#7a9d96',
        warningColor: '#c4a57b',
        dangerColor: '#b47f7f',
        infoColor: '#8b9bb3'
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

// Toggle Particles
let particlesInterval = null;
function toggleParticles() {
    const enabled = document.getElementById('particlesEnabled').checked;
    const container = document.getElementById('particlesContainer');

    if (enabled) {
        container.classList.add('active');
        startParticles();
    } else {
        container.classList.remove('active');
        stopParticles();
    }

    saveSettings();
}

// Initialize Particles
function initializeParticles() {
    // Particles will start if enabled in saved settings
    const enabled = document.getElementById('particlesEnabled').checked;
    if (enabled) {
        startParticles();
    }
}

// Start Particles Animation
function startParticles() {
    if (particlesInterval) return;

    const container = document.getElementById('particlesContainer');

    particlesInterval = setInterval(() => {
        const particle = document.createElement('div');
        particle.className = 'particle';

        // Random position
        particle.style.left = Math.random() * 100 + '%';

        // Random animation duration (10-20 seconds)
        const duration = 10 + Math.random() * 10;
        particle.style.animationDuration = duration + 's';

        // Random size (2-6px)
        const size = 2 + Math.random() * 4;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';

        container.appendChild(particle);

        // Remove particle after animation
        setTimeout(() => {
            particle.remove();
        }, duration * 1000);
    }, 300);
}

// Stop Particles Animation
function stopParticles() {
    if (particlesInterval) {
        clearInterval(particlesInterval);
        particlesInterval = null;
    }

    const container = document.getElementById('particlesContainer');
    container.innerHTML = '';
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
        particlesEnabled: document.getElementById('particlesEnabled').checked,
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

        document.getElementById('particlesEnabled').checked = settings.particlesEnabled || false;
        document.getElementById('blurEnabled').checked = settings.blurEnabled !== false;
        document.getElementById('animationsEnabled').checked = settings.animationsEnabled !== false;

        // Apply settings
        applyCustomGradient();

        if (settings.particlesEnabled) {
            toggleParticles();
        }

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

    // Reset to Cozy Café theme
    applyPreset('cozy-cafe');

    // Reset controls
    document.getElementById('gradientAngle').value = 135;
    document.getElementById('angleValue').textContent = 135;
    document.getElementById('panelOpacity').value = 95;
    document.getElementById('opacityValue').textContent = 95;
    document.getElementById('particlesEnabled').checked = false;
    document.getElementById('blurEnabled').checked = true;
    document.getElementById('animationsEnabled').checked = true;

    // Disable particles
    if (particlesInterval) {
        toggleParticles();
    }

    // Reset effects
    document.body.classList.remove('blur-disabled', 'animations-disabled');
    document.documentElement.style.setProperty('--blur-amount', '12px');
    document.documentElement.style.setProperty('--animation-enabled', '1');

    updateOpacity();

    console.log('Settings reset to default');
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

// Customization functions
window.toggleSettings = toggleSettings;
window.applyPreset = applyPreset;
window.applyCustomGradient = applyCustomGradient;
window.toggleParticles = toggleParticles;
window.toggleBlur = toggleBlur;
window.toggleAnimations = toggleAnimations;
window.updateOpacity = updateOpacity;
window.resetSettings = resetSettings;

console.log('Dashboard JavaScript with Customization loaded successfully');
