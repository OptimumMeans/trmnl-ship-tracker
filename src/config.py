import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8080))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Ship Tracking Configuration
    MMSI = os.getenv('MMSI', '235103357')
    POSITION_API_URL = os.getenv('POSITION_API_URL')
    REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', '900'))
    
    # API Keys
    TRMNL_API_KEY = os.getenv('TRMNL_API_KEY')
    AIS_API_KEY = os.getenv('AIS_API_KEY')
    TRMNL_PLUGIN_UUID = os.getenv('TRMNL_PLUGIN_UUID')
    
    # Display Configuration
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480