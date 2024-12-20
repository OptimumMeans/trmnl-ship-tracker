from flask import Flask, Response, jsonify, request
import asyncio
import threading
import json
from .config import Config
from .services.display import DisplayGenerator
from .services.position_api import PositionAPI

app = Flask(__name__)

# Initialize services
display_generator = DisplayGenerator(Config.DISPLAY_WIDTH, Config.DISPLAY_HEIGHT)
position_api = PositionAPI(Config.POSITION_API_URL, Config.AIS_API_KEY)

def start_position_tracking():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(position_api.connect_and_listen(Config.MMSI))
    except Exception as e:
        print(f"Error in tracking thread: {str(e)}")
    finally:
        loop.close()

# Start position tracking in a separate thread
tracking_thread = threading.Thread(target=start_position_tracking)
tracking_thread.daemon = True
tracking_thread.start()

@app.route('/')
def home():
    """Root route that explains the API"""
    return jsonify({
        "name": "TRMNL Ship Tracker",
        "description": "API for tracking ship positions on TRMNL e-ink display",
        "endpoints": {
            "/webhook": "GET - TRMNL webhook endpoint for display updates",
            "/status": "GET - Current connection status"
        },
        "status": "running",
        "connected": position_api.connected
    })

@app.route('/status')
def status():
    """Status endpoint for debugging"""
    return jsonify({
        "connected": position_api.connected,
        "latest_data": position_api.get_latest_data(),
        "ais_api_key_length": len(Config.AIS_API_KEY) if Config.AIS_API_KEY else 0,
        "mmsi": Config.MMSI,
        "websocket_url": Config.POSITION_API_URL
    })

@app.route('/webhook', methods=['GET'])
def trmnl_webhook():
    """TRMNL webhook endpoint"""
    try:
        print("\n=== Webhook Request ===")
        print(f"Headers: {dict(request.headers)}")
        
        # Get ship data
        ship_data = position_api.get_latest_data()
        print(f"Ship Data: {json.dumps(ship_data, indent=2)}")
        
        # Create display
        image_data = display_generator.create_display(ship_data)
        print(f"Generated image size: {len(image_data)} bytes")
        
        # Send response
        response = Response(
            image_data,
            mimetype='image/bmp',
            headers={
                'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL),
                'X-TRMNL-Plugin-UUID': Config.TRMNL_PLUGIN_UUID
            }
        )
        
        print(f"Response headers: {dict(response.headers)}")
        print("=== End Webhook Request ===\n")
        
        return response

    except Exception as e:
        print(f"Webhook error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"\nStarting TRMNL Ship Tracker")
    print(f"Plugin UUID: {Config.TRMNL_PLUGIN_UUID}")
    print(f"Position API URL: {Config.POSITION_API_URL}")
    print(f"Target MMSI: {Config.MMSI}")
    print(f"Refresh Interval: {Config.REFRESH_INTERVAL} seconds")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )