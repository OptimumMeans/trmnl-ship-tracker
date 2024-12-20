import websockets
import json
import asyncio
from datetime import datetime

class PositionAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.latest_data = {
            'ship_name': 'Connecting...',
            'mmsi': 'N/A',
            'lat': '0.0000',
            'lon': '0.0000',
            'speed': '0.0',
            'course': '0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.connected = False
    
    async def connect_and_listen(self, mmsi):
        while True:
            try:
                async with websockets.connect(self.url) as websocket:
                    print(f"Connected to AIS stream, subscribing to MMSI {mmsi}")
                    self.connected = True
                    
                    # Send subscription message
                    subscribe_message = {
                        "APIKey": self.api_key,
                        "BoundingBoxes": [[[-90, -180], [90, 180]]],
                        "FiltersShipMMSI": [str(mmsi)],
                        "FilterMessageTypes": ["PositionReport"]
                    }
                    
                    await websocket.send(json.dumps(subscribe_message))
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            if data['MessageType'] == 'PositionReport':
                                self.latest_data = self.format_position_data(data)
                                print(f"Received position update for {self.latest_data['ship_name']}")
                        except Exception as e:
                            print(f"Error processing message: {e}")
            except Exception as e:
                print(f"WebSocket connection error: {e}")
                self.connected = False
                self.latest_data = {
                    'ship_name': 'Reconnecting...',
                    'mmsi': 'N/A',
                    'lat': '0.0000',
                    'lon': '0.0000',
                    'speed': '0.0',
                    'course': '0.0',
                    'timestamp': datetime.utcnow().isoformat()
                }
                await asyncio.sleep(5)  # Wait before reconnecting

    def format_position_data(self, data):
        if not data:
            return None
            
        message = data['Message']['PositionReport']
        metadata = data['MetaData']
        
        return {
            'ship_name': metadata.get('ShipName', 'Unknown'),
            'mmsi': metadata.get('MMSI', 'N/A'),
            'lat': f"{message.get('Latitude', 0):.4f}",
            'lon': f"{message.get('Longitude', 0):.4f}",
            'speed': f"{message.get('Sog', 0):.1f}",
            'course': f"{message.get('Cog', 0):.1f}",
            'timestamp': metadata.get('time_utc', datetime.utcnow().isoformat())
        }

    def get_latest_data(self):
        return self.latest_data