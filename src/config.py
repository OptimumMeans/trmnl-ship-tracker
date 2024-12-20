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
        # Create a simple test image for now
        img = Image.new('1', (800, 480), 1)  # White background
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='BMP')
        
        return Response(
            img_byte_arr.getvalue(),
            mimetype='image/bmp',
            headers={
                'X-TRMNL-Refresh': str(os.getenv('REFRESH_INTERVAL', '900'))
            }
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8080)),
        debug=os.getenv('DEBUG', 'True').lower() == 'true'
    )