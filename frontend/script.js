// API Base URL
const API_URL = 'http://localhost:5000/api';

// Store images globally
let beforeImage = null;
let afterImage = null;

// Example Locations
const LOCATIONS = {
    dubai: { lat: 25.2048, lon: 55.2708, name: 'Dubai, UAE' },
    amazon: { lat: -3.4653, lon: -62.2159, name: 'Amazon Rainforest' },
    vegas: { lat: 36.1699, lon: -115.1398, name: 'Las Vegas, USA' },
    aral: { lat: 45.0, lon: 60.0, name: 'Aral Sea' }
};

// ==================== TAB SWITCHING ====================
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Highlight active button
    event.target.classList.add('active');
}

// ==================== POKEMON FUNCTIONS ====================
async function uploadPokemon() {
    const fileInput = document.getElementById('pokemon-file');
    const statusDiv = document.getElementById('pokemon-status');

    if (!fileInput.files[0]) {
        showStatus('pokemon-status', 'Please select a file first!', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        showStatus('pokemon-status', 'Uploading...', 'info');

        const response = await fetch(`${API_URL}/pokemon/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showStatus('pokemon-status', data.message, 'success');
        } else {
            showStatus('pokemon-status', data.error, 'error');
        }
    } catch (error) {
        showStatus('pokemon-status', `Error: ${error.message}`, 'error');
    }
}

async function searchPokemon() {
    const query = document.getElementById('pokemon-search').value;
    const resultsDiv = document.getElementById('pokemon-results');

    if (!query) {
        showStatus('pokemon-status', 'Please enter a search query', 'error');
        return;
    }

    try {
        showStatus('pokemon-status', 'Searching...', 'info');

        const response = await fetch(`${API_URL}/pokemon/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        const data = await response.json();

        if (data.success) {
            showStatus('pokemon-status', `Found ${data.count} results!`, 'success');
            displayPokemonResults(data.results);
        } else {
            showStatus('pokemon-status', data.error, 'error');
        }
    } catch (error) {
        showStatus('pokemon-status', `Error: ${error.message}`, 'error');
    }
}

function displayPokemonResults(results) {
    const resultsDiv = document.getElementById('pokemon-results');

    if (results.length === 0) {
        resultsDiv.innerHTML = '<p>No results found</p>';
        return;
    }

    let html = '<h3>Search Results:</h3>';

    results.forEach(pokemon => {
        html += '<div class="result-item">';

        // Display all fields
        for (let [key, value] of Object.entries(pokemon)) {
            html += `<strong>${key}:</strong> ${value}<br>`;
        }

        html += '</div>';
    });

    resultsDiv.innerHTML = html;
}

// ==================== SATELLITE FUNCTIONS ====================
function loadLocation() {
    const select = document.getElementById('location-select');
    const location = LOCATIONS[select.value];

    if (location) {
        document.getElementById('latitude').value = location.lat;
        document.getElementById('longitude').value = location.lon;
    }
}

async function fetchSatelliteImage(type) {
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;
    const date = type === 'before' ?
        document.getElementById('date-before').value :
        document.getElementById('date-after').value;

    const statusDiv = document.getElementById('satellite-status');
    const previewDiv = document.getElementById(`${type}-preview`);

    try {
        showStatus('satellite-status', `Fetching ${type} image from NASA...`, 'info');

        const response = await fetch(`${API_URL}/satellite/fetch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ latitude, longitude, date })
        });

        const data = await response.json();

        if (data.success) {
            // Display image
            previewDiv.innerHTML = `<img src="${data.image}" alt="${type} image">`;

            // Store for comparison
            if (type === 'before') {
                beforeImage = data.image;
            } else {
                afterImage = data.image;
            }

            // Auto-upload to backend for comparison
            await uploadFetchedImage(data.image, type);

            showStatus('satellite-status', `✅ ${type} image fetched successfully!`, 'success');
        } else {
            showStatus('satellite-status', data.error, 'error');
        }
    } catch (error) {
        showStatus('satellite-status', `Error: ${error.message}`, 'error');
    }
}

async function uploadFetchedImage(imageData, type) {
    // Convert base64 to blob
    const blob = await (await fetch(imageData)).blob();

    const formData = new FormData();
    formData.append('image', blob, `${type}_image.jpg`);
    formData.append('type', type);

    await fetch(`${API_URL}/images/upload`, {
        method: 'POST',
        body: formData
    });
}

// ==================== IMAGE UPLOAD FUNCTIONS ====================
async function uploadImage(type) {
    const fileInput = document.getElementById(`upload-${type}`);

    if (!fileInput.files[0]) {
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('type', type);

    try {
        showStatus('comparison-status', `Uploading ${type} image...`, 'info');

        const response = await fetch(`${API_URL}/images/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Store image
            if (type === 'before') {
                beforeImage = data.image;
            } else {
                afterImage = data.image;
            }

            showStatus('comparison-status', `✅ ${type} image uploaded!`, 'success');
        } else {
            showStatus('comparison-status', data.error, 'error');
        }
    } catch (error) {
        showStatus('comparison-status', `Error: ${error.message}`, 'error');
    }
}

// ==================== IMAGE COMPARISON ====================
async function compareImages() {
    const resultsDiv = document.getElementById('comparison-results');
    const statusDiv = document.getElementById('comparison-status');

    try {
        showStatus('comparison-status', 'Analyzing images...', 'info');

        const response = await fetch(`${API_URL}/images/compare`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showStatus('comparison-status', '✅ Analysis complete!', 'success');
            displayComparisonResults(data);
        } else {
            showStatus('comparison-status', data.error, 'error');
        }
    } catch (error) {
        showStatus('comparison-status', `Error: ${error.message}`, 'error');
    }
}

function displayComparisonResults(data) {
    const resultsDiv = document.getElementById('comparison-results');

    // Determine color class based on change level
    let scoreClass = 'high';
    if (data.change_level === 'critical' || data.change_level === 'high') {
        scoreClass = 'low';
    } else if (data.change_level === 'medium') {
        scoreClass = 'medium';
    }

    let html = `
        <div class="comparison-card">
            <h2>📊 Analysis Results</h2>

            <div class="similarity-score ${scoreClass}">
                ${data.similarity_percent.toFixed(1)}% Similar
            </div>

            <div class="result-item">
                <strong>Assessment:</strong> ${data.assessment}
            </div>

            <div class="result-item">
                <strong>Change Level:</strong> ${data.change_level.toUpperCase()}
            </div>

            <div class="result-item">
                <strong>Number of Changed Regions:</strong> ${data.num_changes}
            </div>

            <div class="result-item">
                <strong>Total Changed Area:</strong> ${data.total_changed_area.toLocaleString()} pixels
            </div>
        </div>

        <div class="comparison-card">
            <h3>🔍 Difference Visualization</h3>
            <img src="${data.diff_image}" style="width: 100%; border-radius: 8px; margin-top: 10px;">
            <p style="color: #666; margin-top: 10px; text-align: center;">
                Red areas indicate the most significant changes
            </p>
        </div>
    `;

    if (data.changes && data.changes.length > 0) {
        html += `
            <div class="comparison-card">
                <h3>📍 Top Changed Regions</h3>
        `;

        data.changes.forEach((change, i) => {
            html += `
                <div class="change-item">
                    <strong>Region ${i + 1}:</strong>
                    Position (${change.x}, ${change.y}),
                    Size ${change.width}x${change.height}px,
                    Area: ${change.area.toLocaleString()}px²
                </div>
            `;
        });

        html += '</div>';
    }

    html += `
        <div class="comparison-card">
            <h3>💡 What This Means</h3>
            <p>A similarity score of <strong>${data.similarity_percent.toFixed(1)}%</strong> indicates:</p>
            <ul style="margin-left: 20px; color: #666;">
    `;

    if (data.similarity_percent < 30) {
        html += `
            <li>These images show MAJOR differences</li>
            <li>Could be different locations or extreme transformation</li>
            <li>Significant changes in land use, development, or environment</li>
        `;
    } else if (data.similarity_percent < 60) {
        html += `
            <li>Significant changes detected between the two time periods</li>
            <li>Likely shows urban development, deforestation, or major events</li>
            <li>Changes are clearly visible across multiple regions</li>
        `;
    } else if (data.similarity_percent < 85) {
        html += `
            <li>Moderate changes present</li>
            <li>Could be gradual development or seasonal variations</li>
            <li>Some areas have changed while others remain similar</li>
        `;
    } else {
        html += `
            <li>Images are very similar with only minor differences</li>
            <li>Changes might be seasonal or small-scale modifications</li>
            <li>Overall landscape remains largely unchanged</li>
        `;
    }

    html += `
            </ul>
        </div>
    `;

    resultsDiv.innerHTML = html;
}

// ==================== UTILITY FUNCTIONS ====================
function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message ${type}`;
    element.style.display = 'block';
}

// Initialize dates on load
window.addEventListener('DOMContentLoaded', () => {
    const today = new Date();
    const lastYear = new Date();
    lastYear.setFullYear(today.getFullYear() - 1);

    document.getElementById('date-after').value = today.toISOString().split('T')[0];
    document.getElementById('date-before').value = lastYear.toISOString().split('T')[0];
});
