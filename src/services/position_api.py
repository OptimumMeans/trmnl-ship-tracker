import websockets
import json
import asyncio
from datetime import datetime

class PositionAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.latest_data = None
    
    async def connect_and_listen(self, mmsi):
        async with websockets.connect(self.url) as websocket:
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
                except Exception as e:
                    print(f"Error processing message: {e}")

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
            'speed': message.get('Sog', 'N/A'),
            'course': message.get('Cog', 'N/A'),
            'timestamp': metadata.get('time_utc', 'N/A')
        }

    def get_latest_data(self):
        return self.latest_data