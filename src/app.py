from flask import Flask, Response, jsonify
import requests
import json
import io
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from .config import Config

app = Flask(__name__)

def create_ship_display(data):
    """Create a 1-bit bitmap display for TRMNL's e-ink screen"""
    # Create white background (1-bit color)
    img = Image.new('1', (800, 480), 1)
    draw = ImageDraw.Draw(img)
    
    # Use default font
    font = ImageFont.load_default()
    
    # Draw header
    draw.text((40, 40), "Ship Tracker - Docked Status", font=font, fill=0)
    
    # Format timestamp
    try:
        timestamp = datetime.fromisoformat(data.get('timestamp', '').replace('Z', '+00:00'))
        time_str = timestamp.strftime('%Y-%m-%d %H:%M UTC')
    except:
        time_str = data.get('timestamp', 'N/A')

    # Format and draw ship data
    y_pos = 80
    info_lines = [
        f"MMSI: {Config.MMSI}",
        "Status: Vessel Docked",
        f"Speed: {data.get('speed', 'N/A')} knots",
        f"Course: {data.get('course', 'N/A')}°",
        f"Last Update: {time_str}"
    ]

    for line in info_lines:
        draw.text((40, y_pos), line, font=font, fill=0)
        y_pos += 30

    # Draw bottom info
    draw.text((40, 400), "Note: Position data not available while vessel is docked", font=font, fill=0)

    # Convert to BMP
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='BMP')
    return img_byte_arr.getvalue()

@app.route('/webhook', methods=['GET'])
def trmnl_webhook():
    """TRMNL webhook endpoint"""
    try:
        # Fetch from vessel finder endpoint
        url = f"{Config.POSITION_API_URL}/{Config.MMSI}"
        print(f"\nFetching data from: {url}")
        
        response = requests.get(url)
        print(f"Response Status: {response.status_code}")
        print(f"Response Content: {response.text}")
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Position API returned status {response.status_code}",
                "details": response.text
            }), response.status_code

        data = response.json()
        if not data or 'data' not in data:
            return jsonify({
                "error": "Invalid data format received",
                "response": data
            }), 500

        # Create the display image
        image_data = create_ship_display(data['data'])
        
        # Return bitmap with TRMNL headers
        return Response(
            image_data,
            mimetype='image/bmp',
            headers={
                'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL)
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