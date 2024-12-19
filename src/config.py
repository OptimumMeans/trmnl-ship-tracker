import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server settings
    PORT = int(os.getenv('PORT', 8080))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # Ship tracking configuration
    MMSI = os.getenv('MMSI', '235103357')
    # Fixed URL to match the working endpoint
    POSITION_API_URL = 'http://localhost:5000/legacy/getLastPositionFromVF'
    REFRESH_INTERVAL = 900  # 15 minutes in seconds