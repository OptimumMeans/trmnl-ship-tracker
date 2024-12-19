from flask import Flask, Response, jsonify, request
import requests
from PIL import Image
import io
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

class Config:
    MMSI = os.getenv('MMSI', '235103357')
    POSITION_API_URL = os.getenv('POSITION_API_URL')
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '900'))  # 15 minutes default

def validate_trmnl_request():
    """Validate the incoming request is from a TRMNL device"""
    api_key = request.headers.get('X-TRMNL-ApiKey')
    if not api_key:
        return False
    # In production, validate the API key against your allowed devices
    return True

def fetch_ship_data():
    """Fetch ship position data from the API"""
    try:
        response = requests.get(f"{Config.POSITION_API_URL}/{Config.MMSI}")
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant data
        ship_data = data.get('data', {})
        return {
            'shipName': ship_data.get('name', 'Unknown Vessel'),
            'mmsi': Config.MMSI,
            'status': 'Docked' if ship_data.get('speed', 0) < 1 else 'Underway',
            'speed': f"{ship_data.get('speed', 0):.1f}",
            'course': str(ship_data.get('course', 'N/A')),
            'timestamp': datetime.fromisoformat(
                ship_data.get('timestamp', '').replace('Z', '+00:00')
            ).strftime('%Y-%m-%d %H:%M UTC')
        }
    except Exception as e:
        print(f"Error fetching ship data: {str(e)}")
        return None

def generate_error_image():
    """Generate an error display image"""
    # Create a blank image with error message
    img = Image.new('1', (800, 480), 1)  # White background
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='BMP')
    return img_byte_arr.getvalue()

@app.route('/webhook', methods=['GET'])
def trmnl_webhook():
    """TRMNL webhook endpoint"""
    # Validate request
    if not validate_trmnl_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Fetch ship data
        ship_data = fetch_ship_data()
        if not ship_data:
            return Response(
                generate_error_image(),
                mimetype='image/bmp',
                headers={'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL)}
            )

        # TODO: Generate display image using TRMNL React component
        # This will be implemented in the next step
        
        return Response(
            generate_error_image(),  # Placeholder until we implement proper rendering
            mimetype='image/bmp',
            headers={'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL)}
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return Response(
            generate_error_image(),
            mimetype='image/bmp',
            headers={'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL)}
        )

if __name__ == "__main__":
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )