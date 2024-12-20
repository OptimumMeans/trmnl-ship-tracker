import websockets
import json
import asyncio
from datetime import datetime

class PositionAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.latest_data = {
            'ship_name': 'Waiting for Data...',
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
                print(f"Attempting to connect to AIS Stream with API key: {self.api_key[:5]}...")
                async with websockets.connect(self.url) as websocket:
                    print(f"Connected to AIS stream, subscribing to MMSI {mmsi}")
                    self.connected = True
                    
                    subscribe_message = {
                        "APIKey": self.api_key,
                        "BoundingBoxes": [[[-90, -180], [90, 180]]],
                        "FiltersShipMMSI": [str(mmsi)],
                        "FilterMessageTypes": ["PositionReport"]
                    }
                    
                    print(f"Sending subscription message: {json.dumps(subscribe_message)}")
                    await websocket.send(json.dumps(subscribe_message))
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            print(f"Received message type: {data.get('MessageType')}")
                            if data['MessageType'] == 'PositionReport':
                                self.latest_data = self.format_position_data(data)
                                print(f"Updated ship data: {json.dumps(self.latest_data)}")
                        except Exception as e:
                            print(f"Error processing message: {str(e)}")
                            print(f"Raw message: {message[:200]}...")  # Print first 200 chars
            except Exception as e:
                print(f"WebSocket connection error: {str(e)}")
                self.connected = False
                await asyncio.sleep(5)  # Wait before reconnecting

    def format_position_data(self, data):
        if not data:
            return self.latest_data
            
        try:
            message = data['Message']['PositionReport']
            metadata = data['MetaData']
            
            formatted_data = {
                'ship_name': metadata.get('ShipName', 'Unknown'),
                'mmsi': metadata.get('MMSI', 'N/A'),
                'lat': f"{message.get('Latitude', 0):.4f}",
                'lon': f"{message.get('Longitude', 0):.4f}",
                'speed': f"{message.get('Sog', 0):.1f}",
                'course': f"{message.get('Cog', 0):.1f}",
                'timestamp': metadata.get('time_utc', datetime.utcnow().isoformat())
            }
            print(f"Formatted data: {json.dumps(formatted_data)}")
            return formatted_data
        except Exception as e:
            print(f"Error formatting data: {str(e)}")
            return self.latest_data

    def get_latest_data(self):
        print(f"Returning latest data: {json.dumps(self.latest_data)}")
        return self.latest_data