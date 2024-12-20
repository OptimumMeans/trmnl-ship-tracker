from flask import Flask, Response, jsonify, request
import asyncio
import threading
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
    loop.run_until_complete(position_api.connect_and_listen(Config.MMSI))

# Start position tracking in a separate thread
tracking_thread = threading.Thread(target=start_position_tracking)
tracking_thread.daemon = True
tracking_thread.start()

@app.route('/webhook', methods=['GET'])
def trmnl_webhook():
    """TRMNL webhook endpoint"""
    try:
        # Log incoming request
        print(f"Received webhook request with headers: {dict(request.headers)}")
        
        # Get the latest ship data
        ship_data = position_api.get_latest_data()
        print(f"Current ship data: {json.dumps(ship_data)}")
        
        # Create the display image
        image_data = display_generator.create_display(ship_data)
        print(f"Generated image of size: {len(image_data)} bytes")
        
        # Return bitmap with TRMNL headers
        response = Response(
            image_data,
            mimetype='image/bmp',
            headers={
                'X-TRMNL-Refresh': str(Config.REFRESH_INTERVAL),
                'X-TRMNL-Plugin-UUID': Config.TRMNL_PLUGIN_UUID
            }
        )
        print(f"Sending response with headers: {dict(response.headers)}")
        return response

    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500
        
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