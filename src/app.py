from flask import Flask, Response, jsonify
import requests
import json
import io
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from .config import Config
from .services.display import DisplayGenerator
from .services.position_api import PositionAPI
from .utils.formatters import format_timestamp, format_coordinates

app = Flask(__name__)

# Initialize services
display_generator = DisplayGenerator(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT)
position_api = PositionAPI(Config.POSITION_API_URL)

def create_ship_display(data):
    """Create a 1-bit bitmap display for TRMNL's e-ink screen"""
    # Create white background (1-bit color)
    img = Image.new('1', (Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT), 1)
    draw = ImageDraw.Draw(img)
    
    # Use default font
    font = ImageFont.load_default()
    
    # Draw header
    draw.text((40, 40), "Ship Tracker - Position Status", font=font, fill=0)
    
    # Format timestamp
    time_str = format_timestamp(data.get('timestamp', 'N/A'))

    # Format coordinates
    lat = float(data.get('lat', 0))
    lon = float(data.get('lon', 0))
    lat_str, lon_str = format_coordinates(lat, lon)

    # Format and draw ship data
    y_pos = 80
    info_lines = [
        f"MMSI: {Config.MMSI}",
        f"Position: {lat_str}, {lon_str}",
        f"Speed: {data.get('speed', 'N/A')} knots",
        f"Course: {data.get('course', 'N/A')}°",
        f"Last Update: {time_str}"
    ]

    for line in info_lines:
        draw.text((40, y_pos), line, font=font, fill=0)
        y_pos += 30

    # Convert to BMP
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='BMP')
    return img_byte_arr.getvalue()

@app.route('/')
def home():
    """Root route that explains the API"""
    return jsonify({
        "name": "TRMNL Ship Tracker",
        "description": "API for tracking ship positions on TRMNL e-ink display",
        "endpoints": {
            "/webhook": "GET - TRMNL webhook endpoint for display updates",
        },
        "status": "running"
    })

@app.route('/webhook', methods=['GET'])
def trmnl_webhook():
    """TRMNL webhook endpoint"""
    try:
        # Fetch vessel position data
        data = position_api.get_vessel_position(Config.MMSI)
        if not data or 'data' not in data:
            return jsonify({
                "error": "Invalid data format received from position API",
                "response": data
            }), 500

        # Format the data
        formatted_data = position_api.format_position_data(data['data'])
        
        # Create the display image
        image_data = create_ship_display(formatted_data)
        
        # Return bitmap with TRMNL headers
        return Response(
            image_data,
            mimetype='image/bmp',
            headers={
                'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL),
                'X-TRMNL-API-Key': Config.TRMNL_API_KEY
            }
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print(f"\nStarting TRMNL Ship Tracker")
    print(f"Position API Base URL: {Config.POSITION_API_URL}")
    print(f"Target MMSI: {Config.MMSI}")
    print(f"Refresh Interval: {Config.REFRESH_INTERVAL} seconds")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )