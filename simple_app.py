"""
Super Simple Pokemon & Satellite Image Tool
A lightweight web interface that works immediately without heavy dependencies!
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import csv
import urllib.parse
from datetime import datetime

# Store data in memory
pokemon_data = []
image_data = []

class SimpleHandler(SimpleHTTPRequestHandler):
    """Custom handler for our simple web app."""

    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            self.serve_homepage()
        elif self.path == '/api/pokemon':
            self.serve_pokemon_data()
        elif self.path.startswith('/api/search?'):
            self.handle_search()
        else:
            self.send_error(404, "File not found")

    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/pokemon/submit':
            self.handle_pokemon_submit()
        elif self.path == '/api/pokemon/upload':
            self.handle_pokemon_upload()
        else:
            self.send_error(404, "API endpoint not found")

    def serve_homepage(self):
        """Serve the main HTML page."""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Pokemon & Satellite Image Tool 🛰️</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #DAA520 0%, #9370DB 50%, #FFB6C1 100%);
            padding: 30px;
            text-align: center;
            color: white;
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2em;
            opacity: 0.95;
        }

        .tabs {
            display: flex;
            background: #f0f0f0;
            border-bottom: 3px solid #9370DB;
        }

        .tab {
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            background: #f0f0f0;
            border: none;
            font-size: 1.1em;
            font-weight: bold;
            color: #666;
            transition: all 0.3s;
        }

        .tab:hover {
            background: #e0e0e0;
        }

        .tab.active {
            background: white;
            color: #9370DB;
            border-bottom: 3px solid #DAA520;
        }

        .tab-content {
            display: none;
            padding: 30px;
        }

        .tab-content.active {
            display: block;
        }

        .section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f0ff;
            border-radius: 10px;
            border-left: 5px solid #9370DB;
        }

        .section h2 {
            color: #9370DB;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input[type="text"],
        input[type="number"],
        textarea,
        select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }

        input:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #9370DB;
        }

        button {
            background: linear-gradient(135deg, #DAA520 0%, #9370DB 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }

        button:hover {
            transform: scale(1.05);
        }

        button:active {
            transform: scale(0.98);
        }

        .file-upload {
            border: 3px dashed #9370DB;
            padding: 30px;
            text-align: center;
            border-radius: 10px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
        }

        .file-upload:hover {
            background: #f8f0ff;
            border-color: #DAA520;
        }

        .results {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            border: 2px solid #9370DB;
            min-height: 100px;
        }

        .pokemon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .pokemon-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #9370DB;
            transition: transform 0.3s;
        }

        .pokemon-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(147, 112, 219, 0.3);
        }

        .pokemon-card h3 {
            color: #9370DB;
            margin-bottom: 10px;
        }

        .stat-bar {
            background: #f0f0f0;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }

        .stat-fill {
            background: linear-gradient(90deg, #DAA520 0%, #9370DB 100%);
            height: 100%;
            transition: width 0.5s;
        }

        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .info-box {
            background: linear-gradient(135deg, #FFB6C1 0%, #FFC0CB 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            color: #333;
        }

        .info-box h3 {
            margin-bottom: 10px;
        }

        .info-box ul {
            margin-left: 20px;
        }

        .info-box li {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Pokemon & Satellite Image Tool 🛰️</h1>
            <p>Simple, Fast, and Easy to Use!</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('pokemon')">🎮 Pokemon Data</button>
            <button class="tab" onclick="showTab('submit')">➕ Submit Pokemon</button>
            <button class="tab" onclick="showTab('satellite')">🛰️ Satellite Images</button>
            <button class="tab" onclick="showTab('help')">❓ Help</button>
        </div>

        <!-- Pokemon Data Tab -->
        <div id="pokemon" class="tab-content active">
            <div class="section">
                <h2>📊 Browse Pokemon Data</h2>
                <button onclick="loadPokemon()">Load All Pokemon</button>
                <div id="pokemon-results" class="results"></div>
            </div>

            <div class="section">
                <h2>🔍 Search Pokemon</h2>
                <input type="text" id="search-query" placeholder="Search by name, type, or stat...">
                <button onclick="searchPokemon()">Search</button>
                <div id="search-results" class="results"></div>
            </div>
        </div>

        <!-- Submit Pokemon Tab -->
        <div id="submit" class="tab-content">
            <div class="section">
                <h2>➕ Submit Your Own Pokemon Data</h2>
                <p>Add your custom Pokemon to the database!</p>

                <form id="pokemon-form" onsubmit="submitPokemon(event)">
                    <input type="text" name="name" placeholder="Pokemon Name" required>

                    <select name="type1" required>
                        <option value="">Primary Type</option>
                        <option value="Grass">Grass</option>
                        <option value="Fire">Fire</option>
                        <option value="Water">Water</option>
                        <option value="Electric">Electric</option>
                        <option value="Psychic">Psychic</option>
                        <option value="Dragon">Dragon</option>
                        <option value="Normal">Normal</option>
                        <option value="Fighting">Fighting</option>
                        <option value="Flying">Flying</option>
                        <option value="Poison">Poison</option>
                        <option value="Ground">Ground</option>
                        <option value="Rock">Rock</option>
                        <option value="Bug">Bug</option>
                        <option value="Ghost">Ghost</option>
                        <option value="Steel">Steel</option>
                        <option value="Ice">Ice</option>
                        <option value="Dark">Dark</option>
                        <option value="Fairy">Fairy</option>
                    </select>

                    <select name="type2">
                        <option value="">Secondary Type (Optional)</option>
                        <option value="Grass">Grass</option>
                        <option value="Fire">Fire</option>
                        <option value="Water">Water</option>
                        <option value="Electric">Electric</option>
                        <option value="Psychic">Psychic</option>
                        <option value="Dragon">Dragon</option>
                        <option value="Normal">Normal</option>
                        <option value="Fighting">Fighting</option>
                        <option value="Flying">Flying</option>
                        <option value="Poison">Poison</option>
                        <option value="Ground">Ground</option>
                        <option value="Rock">Rock</option>
                        <option value="Bug">Bug</option>
                        <option value="Ghost">Ghost</option>
                        <option value="Steel">Steel</option>
                        <option value="Ice">Ice</option>
                        <option value="Dark">Dark</option>
                        <option value="Fairy">Fairy</option>
                    </select>

                    <input type="number" name="hp" placeholder="HP" min="1" max="255" required>
                    <input type="number" name="attack" placeholder="Attack" min="1" max="255" required>
                    <input type="number" name="defense" placeholder="Defense" min="1" max="255" required>
                    <input type="number" name="sp_atk" placeholder="Special Attack" min="1" max="255" required>
                    <input type="number" name="sp_def" placeholder="Special Defense" min="1" max="255" required>
                    <input type="number" name="speed" placeholder="Speed" min="1" max="255" required>

                    <button type="submit">Submit Pokemon</button>
                </form>

                <div id="submit-result" style="margin-top: 20px;"></div>
            </div>

            <div class="section">
                <h2>📤 Upload Pokemon CSV File</h2>
                <div class="file-upload" onclick="document.getElementById('csv-upload').click()">
                    <p>📁 Click to upload a Pokemon CSV file</p>
                    <input type="file" id="csv-upload" accept=".csv" style="display:none" onchange="uploadCSV(event)">
                </div>
                <div id="upload-result"></div>
            </div>
        </div>

        <!-- Satellite Images Tab -->
        <div id="satellite" class="tab-content">
            <div class="section">
                <h2>🛰️ Satellite Image Analysis</h2>
                <p>Upload and analyze satellite images to detect changes over time</p>

                <div style="margin: 20px 0;">
                    <h3>Before Image</h3>
                    <input type="file" id="image-before" accept="image/*">
                    <img id="preview-before" style="max-width: 100%; margin-top: 10px; display: none;">
                </div>

                <div style="margin: 20px 0;">
                    <h3>After Image</h3>
                    <input type="file" id="image-after" accept="image/*">
                    <img id="preview-after" style="max-width: 100%; margin-top: 10px; display: none;">
                </div>

                <button onclick="analyzeImages()">Analyze Changes</button>

                <div id="image-analysis" class="results"></div>
            </div>
        </div>

        <!-- Help Tab -->
        <div id="help" class="tab-content">
            <div class="info-box">
                <h3>📖 How to Use This Tool</h3>
                <ul>
                    <li><strong>Pokemon Data:</strong> Browse and search through Pokemon information</li>
                    <li><strong>Submit Pokemon:</strong> Add your own custom Pokemon or upload a CSV file</li>
                    <li><strong>Satellite Images:</strong> Upload before/after images to analyze changes</li>
                </ul>
            </div>

            <div class="section">
                <h2>🎮 Pokemon Data Features</h2>
                <p><strong>Browse:</strong> Click "Load All Pokemon" to see all available Pokemon</p>
                <p><strong>Search:</strong> Search by name (e.g., "Pikachu"), type (e.g., "Fire"), or stats</p>
            </div>

            <div class="section">
                <h2>➕ Submitting Pokemon Data</h2>
                <h3>Manual Entry:</h3>
                <ol>
                    <li>Fill in the Pokemon name</li>
                    <li>Select primary and optionally secondary type</li>
                    <li>Enter all stat values (HP, Attack, Defense, etc.)</li>
                    <li>Click "Submit Pokemon"</li>
                </ol>

                <h3>CSV Upload:</h3>
                <p>Your CSV file should have these columns:</p>
                <code>Name,Type1,Type2,HP,Attack,Defense,Sp_Atk,Sp_Def,Speed</code>
                <p>Example:</p>
                <code>Pikachu,Electric,,35,55,40,50,50,90</code>
            </div>

            <div class="section">
                <h2>🛰️ Satellite Image Analysis</h2>
                <p>Upload two images taken at different times of the same location to detect changes:</p>
                <ol>
                    <li>Select a "Before" image</li>
                    <li>Select an "After" image</li>
                    <li>Click "Analyze Changes"</li>
                    <li>View the analysis results</li>
                </ol>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));

            const buttons = document.querySelectorAll('.tab');
            buttons.forEach(btn => btn.classList.remove('active'));

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        async function loadPokemon() {
            const results = document.getElementById('pokemon-results');
            results.innerHTML = '<p>Loading Pokemon data...</p>';

            try {
                const response = await fetch('/api/pokemon');
                const data = await response.json();

                if (data.length === 0) {
                    results.innerHTML = '<p>No Pokemon data available. Upload a CSV file or add Pokemon manually!</p>';
                    return;
                }

                let html = '<div class="pokemon-grid">';
                data.forEach(pokemon => {
                    const total = parseInt(pokemon.HP || 0) + parseInt(pokemon.Attack || 0) +
                                parseInt(pokemon.Defense || 0) + parseInt(pokemon.Sp_Atk || 0) +
                                parseInt(pokemon.Sp_Def || 0) + parseInt(pokemon.Speed || 0);

                    html += `
                        <div class="pokemon-card">
                            <h3>${pokemon.Name}</h3>
                            <p><strong>Type:</strong> ${pokemon.Type1}${pokemon.Type2 ? ' / ' + pokemon.Type2 : ''}</p>
                            <p><strong>Total:</strong> ${total}</p>
                            <p><strong>HP:</strong> ${pokemon.HP}</p>
                            <div class="stat-bar"><div class="stat-fill" style="width: ${(pokemon.HP/255*100)}%"></div></div>
                            <p><strong>Attack:</strong> ${pokemon.Attack}</p>
                            <div class="stat-bar"><div class="stat-fill" style="width: ${(pokemon.Attack/255*100)}%"></div></div>
                            <p><strong>Defense:</strong> ${pokemon.Defense}</p>
                            <div class="stat-bar"><div class="stat-fill" style="width: ${(pokemon.Defense/255*100)}%"></div></div>
                            <p><strong>Speed:</strong> ${pokemon.Speed}</p>
                            <div class="stat-bar"><div class="stat-fill" style="width: ${(pokemon.Speed/255*100)}%"></div></div>
                        </div>
                    `;
                });
                html += '</div>';
                results.innerHTML = html;
            } catch (error) {
                results.innerHTML = '<p class="alert alert-error">Error loading Pokemon data: ' + error.message + '</p>';
            }
        }

        async function searchPokemon() {
            const query = document.getElementById('search-query').value;
            const results = document.getElementById('search-results');

            if (!query) {
                results.innerHTML = '<p class="alert alert-error">Please enter a search query</p>';
                return;
            }

            results.innerHTML = '<p>Searching...</p>';

            try {
                const response = await fetch('/api/search?' + new URLSearchParams({q: query}));
                const data = await response.json();

                if (data.length === 0) {
                    results.innerHTML = '<p>No Pokemon found matching "' + query + '"</p>';
                    return;
                }

                let html = '<div class="pokemon-grid">';
                data.forEach(pokemon => {
                    html += `
                        <div class="pokemon-card">
                            <h3>${pokemon.Name}</h3>
                            <p><strong>Type:</strong> ${pokemon.Type1}${pokemon.Type2 ? ' / ' + pokemon.Type2 : ''}</p>
                            <p><strong>HP:</strong> ${pokemon.HP} | <strong>Attack:</strong> ${pokemon.Attack}</p>
                            <p><strong>Defense:</strong> ${pokemon.Defense} | <strong>Speed:</strong> ${pokemon.Speed}</p>
                        </div>
                    `;
                });
                html += '</div>';
                results.innerHTML = html;
            } catch (error) {
                results.innerHTML = '<p class="alert alert-error">Error searching: ' + error.message + '</p>';
            }
        }

        async function submitPokemon(event) {
            event.preventDefault();
            const form = event.target;
            const formData = new FormData(form);
            const resultDiv = document.getElementById('submit-result');

            const pokemon = {
                Name: formData.get('name'),
                Type1: formData.get('type1'),
                Type2: formData.get('type2'),
                HP: formData.get('hp'),
                Attack: formData.get('attack'),
                Defense: formData.get('defense'),
                Sp_Atk: formData.get('sp_atk'),
                Sp_Def: formData.get('sp_def'),
                Speed: formData.get('speed')
            };

            try {
                const response = await fetch('/api/pokemon/submit', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(pokemon)
                });

                const result = await response.json();

                if (result.success) {
                    resultDiv.innerHTML = '<p class="alert alert-success">✅ Pokemon added successfully!</p>';
                    form.reset();
                } else {
                    resultDiv.innerHTML = '<p class="alert alert-error">❌ Error: ' + result.error + '</p>';
                }
            } catch (error) {
                resultDiv.innerHTML = '<p class="alert alert-error">❌ Error submitting Pokemon: ' + error.message + '</p>';
            }
        }

        async function uploadCSV(event) {
            const file = event.target.files[0];
            const resultDiv = document.getElementById('upload-result');

            if (!file) return;

            resultDiv.innerHTML = '<p>Uploading...</p>';

            const reader = new FileReader();
            reader.onload = async function(e) {
                const text = e.target.result;

                try {
                    const response = await fetch('/api/pokemon/upload', {
                        method: 'POST',
                        headers: {'Content-Type': 'text/csv'},
                        body: text
                    });

                    const result = await response.json();

                    if (result.success) {
                        resultDiv.innerHTML = '<p class="alert alert-success">✅ Uploaded ' + result.count + ' Pokemon successfully!</p>';
                    } else {
                        resultDiv.innerHTML = '<p class="alert alert-error">❌ Error: ' + result.error + '</p>';
                    }
                } catch (error) {
                    resultDiv.innerHTML = '<p class="alert alert-error">❌ Error uploading: ' + error.message + '</p>';
                }
            };
            reader.readAsText(file);
        }

        function analyzeImages() {
            const beforeFile = document.getElementById('image-before').files[0];
            const afterFile = document.getElementById('image-after').files[0];
            const results = document.getElementById('image-analysis');

            if (!beforeFile || !afterFile) {
                results.innerHTML = '<p class="alert alert-error">Please select both before and after images</p>';
                return;
            }

            results.innerHTML = '<p>Analyzing images...</p>';

            // Simple analysis - in a real app, this would call the backend
            setTimeout(() => {
                results.innerHTML = `
                    <h3>Analysis Results</h3>
                    <p><strong>Before Image:</strong> ${beforeFile.name}</p>
                    <p><strong>After Image:</strong> ${afterFile.name}</p>
                    <p><strong>Status:</strong> Images received. For full AI-powered analysis, use the advanced mode with the full app!</p>
                    <div class="info-box">
                        <p>This simple version shows uploaded images. For AI-powered change detection with:</p>
                        <ul>
                            <li>Image captioning</li>
                            <li>Object detection</li>
                            <li>Structural similarity analysis</li>
                            <li>Detailed change reports</li>
                        </ul>
                        <p>Please follow the installation instructions to set up the full version!</p>
                    </div>
                `;
            }, 500);
        }

        // Preview images when selected
        document.getElementById('image-before').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.getElementById('preview-before');
                    img.src = e.target.result;
                    img.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });

        document.getElementById('image-after').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.getElementById('preview-after');
                    img.src = e.target.result;
                    img.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    </script>
</body>
</html>"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_pokemon_data(self):
        """Return Pokemon data as JSON."""
        # Load from CSV if exists
        global pokemon_data
        csv_file = 'data/pokemon/sample_pokemon.csv'

        if os.path.exists(csv_file) and not pokemon_data:
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    pokemon_data = list(reader)
            except Exception as e:
                print(f"Error loading CSV: {e}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(pokemon_data).encode())

    def handle_search(self):
        """Handle Pokemon search."""
        global pokemon_data
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('q', [''])[0].lower()

        results = []
        for pokemon in pokemon_data:
            # Search in name, types, and stats
            search_text = f"{pokemon.get('Name', '')} {pokemon.get('Type1', '')} {pokemon.get('Type2', '')}".lower()
            if query in search_text:
                results.append(pokemon)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(results).encode())

    def handle_pokemon_submit(self):
        """Handle Pokemon submission."""
        global pokemon_data

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            new_pokemon = json.loads(post_data.decode('utf-8'))
            pokemon_data.append(new_pokemon)

            # Also save to CSV
            csv_file = 'data/pokemon/user_submitted.csv'
            os.makedirs('data/pokemon', exist_ok=True)

            file_exists = os.path.exists(csv_file)
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=new_pokemon.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(new_pokemon)

            response = {'success': True, 'message': 'Pokemon added successfully'}
        except Exception as e:
            response = {'success': False, 'error': str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_pokemon_upload(self):
        """Handle CSV upload."""
        global pokemon_data

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            # Parse CSV
            lines = post_data.strip().split('\n')
            reader = csv.DictReader(lines)
            new_pokemon = list(reader)

            pokemon_data.extend(new_pokemon)

            response = {'success': True, 'count': len(new_pokemon)}
        except Exception as e:
            response = {'success': False, 'error': str(e)}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

def run_server(port=8000):
    """Run the simple web server."""
    print("\n" + "=" * 70)
    print("  🎮 SUPER SIMPLE POKEMON & SATELLITE IMAGE TOOL 🛰️")
    print("=" * 70)
    print(f"\n✅ Server starting on http://localhost:{port}")
    print(f"\n📖 Instructions:")
    print(f"  1. Open your browser to: http://localhost:{port}")
    print(f"  2. Use the tabs to navigate between features")
    print(f"  3. Have fun exploring Pokemon data!")
    print(f"\n💡 Tips:")
    print(f"  - Default Pokemon data loads automatically")
    print(f"  - Submit your own Pokemon using the form")
    print(f"  - Upload CSV files for bulk imports")
    print(f"  - Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")

    server = HTTPServer(('localhost', port), SimpleHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thanks for using the tool!")
        server.shutdown()

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs('data/pokemon', exist_ok=True)
    os.makedirs('data/images', exist_ok=True)

    # Run the server
    run_server(port=8000)
