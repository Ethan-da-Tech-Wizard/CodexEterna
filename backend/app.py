"""
Simple Flask Backend for Pokemon & Satellite Image Tool
Python 3.10+
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import cv2
import numpy as np
from PIL import Image
import requests
from datetime import datetime
from skimage.metrics import structural_similarity as ssim
import io
import base64

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global storage (simple - no database needed)
pokemon_data = None


# ==================== SERVE FRONTEND ====================
@app.route('/')
def serve_frontend():
    """Serve the main HTML page"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('../frontend', path)


# ==================== POKEMON ENDPOINTS ====================
@app.route('/api/pokemon/upload', methods=['POST'])
def upload_pokemon():
    """Upload Pokemon CSV/Excel file"""
    global pokemon_data

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save file
        filename = os.path.join(app.config['UPLOAD_FOLDER'], 'pokemon_data.csv')
        file.save(filename)

        # Load data
        if filename.endswith('.csv'):
            pokemon_data = pd.read_csv(filename)
        else:
            pokemon_data = pd.read_excel(filename)

        return jsonify({
            'success': True,
            'message': f'Loaded {len(pokemon_data)} Pokemon!',
            'columns': list(pokemon_data.columns),
            'count': len(pokemon_data)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pokemon/search', methods=['POST'])
def search_pokemon():
    """Search Pokemon data"""
    global pokemon_data

    if pokemon_data is None:
        return jsonify({'error': 'Please upload Pokemon data first'}), 400

    try:
        data = request.json
        query = data.get('query', '').lower()

        if not query:
            return jsonify({'error': 'No search query provided'}), 400

        # Simple search across all columns
        mask = pokemon_data.astype(str).apply(
            lambda x: x.str.contains(query, case=False, na=False)
        ).any(axis=1)

        results = pokemon_data[mask].head(10).to_dict('records')

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pokemon/stats', methods=['GET'])
def pokemon_stats():
    """Get Pokemon dataset statistics"""
    global pokemon_data

    if pokemon_data is None:
        return jsonify({'error': 'No data loaded'}), 400

    try:
        stats = {
            'total_pokemon': len(pokemon_data),
            'columns': list(pokemon_data.columns),
            'sample': pokemon_data.head(5).to_dict('records')
        }

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SATELLITE IMAGE ENDPOINTS ====================
@app.route('/api/satellite/fetch', methods=['POST'])
def fetch_satellite_image():
    """Fetch satellite image from NASA GIBS (FREE - no API key!)"""
    try:
        data = request.json
        latitude = float(data.get('latitude', 0))
        longitude = float(data.get('longitude', 0))
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # NASA GIBS WMS endpoint
        delta = 0.5  # Degrees of coverage
        bbox = f"{longitude-delta},{latitude-delta},{longitude+delta},{latitude+delta}"

        url = (
            f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?"
            f"SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&"
            f"LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&"
            f"CRS=EPSG:4326&"
            f"BBOX={bbox}&"
            f"WIDTH=512&HEIGHT=512&"
            f"FORMAT=image/jpeg&"
            f"TIME={date}"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save image
        img_filename = f"satellite_{date}_{latitude}_{longitude}.jpg"
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_filename)

        with open(img_path, 'wb') as f:
            f.write(response.content)

        # Convert to base64 for frontend
        img_base64 = base64.b64encode(response.content).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_base64}',
            'filename': img_filename,
            'message': 'Image fetched successfully!'
        })

    except Exception as e:
        return jsonify({'error': f'Failed to fetch image: {str(e)}'}), 500


# ==================== IMAGE COMPARISON ENDPOINTS ====================
@app.route('/api/images/upload', methods=['POST'])
def upload_image():
    """Upload an image for comparison"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400

        file = request.files['image']
        image_type = request.form.get('type', 'before')  # before or after

        # Save image
        filename = f"{image_type}_image.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Read and encode as base64
        with open(filepath, 'rb') as f:
            img_data = f.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')

        return jsonify({
            'success': True,
            'filename': filename,
            'image': f'data:image/jpeg;base64,{img_base64}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/images/compare', methods=['POST'])
def compare_images():
    """Compare two images and detect changes"""
    try:
        # Get image paths
        before_path = os.path.join(app.config['UPLOAD_FOLDER'], 'before_image.jpg')
        after_path = os.path.join(app.config['UPLOAD_FOLDER'], 'after_image.jpg')

        if not os.path.exists(before_path) or not os.path.exists(after_path):
            return jsonify({'error': 'Please upload both images first'}), 400

        # Load images
        img1 = cv2.imread(before_path)
        img2 = cv2.imread(after_path)

        # Convert to grayscale
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Resize if needed
        if gray1.shape != gray2.shape:
            height = min(gray1.shape[0], gray2.shape[0])
            width = min(gray1.shape[1], gray2.shape[1])
            gray1 = cv2.resize(gray1, (width, height))
            gray2 = cv2.resize(gray2, (width, height))

        # Compute SSIM
        score, diff = ssim(gray1, gray2, full=True)
        diff = (diff * 255).astype("uint8")

        # Threshold difference
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Find changed regions
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        changes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                changes.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': int(area)
                })

        # Create difference visualization
        diff_color = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
        _, buffer = cv2.imencode('.jpg', diff_color)
        diff_base64 = base64.b64encode(buffer).decode('utf-8')

        # Generate analysis
        similarity_pct = score * 100

        if score < 0.3:
            assessment = "MAJOR CHANGES: Very different images - possibly different locations or extreme transformation"
            change_level = "critical"
        elif score < 0.6:
            assessment = "SIGNIFICANT CHANGES: Notable differences detected between images"
            change_level = "high"
        elif score < 0.85:
            assessment = "MODERATE CHANGES: Some differences present"
            change_level = "medium"
        else:
            assessment = "MINOR CHANGES: Images are very similar"
            change_level = "low"

        return jsonify({
            'success': True,
            'similarity_score': float(score),
            'similarity_percent': float(similarity_pct),
            'assessment': assessment,
            'change_level': change_level,
            'num_changes': len(changes),
            'changes': changes[:10],  # Top 10 changes
            'total_changed_area': sum(c['area'] for c in changes),
            'diff_image': f'data:image/jpeg;base64,{diff_base64}'
        })

    except Exception as e:
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500


# ==================== HEALTH CHECK ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify({
        'status': 'healthy',
        'pokemon_loaded': pokemon_data is not None,
        'pokemon_count': len(pokemon_data) if pokemon_data is not None else 0
    })


if __name__ == '__main__':
    print("=" * 70)
    print("  🎮🛰️ Pokemon & Satellite Image Comparison Tool")
    print("=" * 70)
    print("\n✅ Starting server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("\n💡 Features:")
    print("  - Upload Pokemon data (CSV/Excel)")
    print("  - Fetch satellite images (NASA - FREE, no API key!)")
    print("  - Compare images and detect changes")
    print("\n" + "=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
