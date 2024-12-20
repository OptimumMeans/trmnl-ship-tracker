import websockets
import json
import asyncio
from datetime import datetime
import ssl

class PositionAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.latest_data = {
            'ship_name': 'Starting...',
            'mmsi': 'N/A',
            'lat': '0.0000',
            'lon': '0.0000',
            'speed': '0.0',
            'course': '0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        self.connected = False
        self.connection_error = None

    async def connect_and_listen(self, mmsi):
        while True:
            try:
                print(f"Connecting to AIS Stream at {self.url}")
                
                # Create SSL context for secure connection
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                async with websockets.connect(
                    self.url,
                    ssl=ssl_context,
                    ping_interval=20,
                    ping_timeout=20,
                    close_timeout=15
                ) as websocket:
                    print("WebSocket connection established")
                    self.connected = True
                    self.connection_error = None
                    
                    # Send subscription message
                    subscribe_message = {
                        "APIKey": self.api_key,
                        "BoundingBoxes": [[[-90, -180], [90, 180]]],
                        "FiltersShipMMSI": [str(mmsi)],
                        "FilterMessageTypes": ["PositionReport"]
                    }
                    
                    print("Sending subscription message...")
                    await websocket.send(json.dumps(subscribe_message))
                    print(f"Subscription sent for MMSI {mmsi}")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            print(f"Received message of type: {data.get('MessageType')}")
                            
                            if data.get('MessageType') == 'PositionReport':
                                self.latest_data = self.format_position_data(data)
                                print(f"Updated position: {self.latest_data['lat']}, {self.latest_data['lon']}")
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse message: {e}")
                            continue
                        
            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                self.connected = False
                self.connection_error = f"Connection closed: {str(e)}"
                
            except Exception as e:
                print(f"Connection error: {str(e)}")
                self.connected = False
                self.connection_error = str(e)
                
            # Update status to show reconnection attempt
            self.latest_data = {
                'ship_name': f'Reconnecting... ({self.connection_error})',
                'mmsi': mmsi,
                'lat': '0.0000',
                'lon': '0.0000',
                'speed': '0.0',
                'course': '0.0',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Wait before reconnecting
            await asyncio.sleep(5)
    
    def format_position_data(self, data):
        try:
            message = data['Message']['PositionReport']
            metadata = data.get('MetaData', {})
            
            return {
                'ship_name': metadata.get('ShipName', 'Unknown Vessel'),
                'mmsi': metadata.get('MMSI', 'N/A'),
                'lat': f"{message.get('Latitude', 0):.4f}",
                'lon': f"{message.get('Longitude', 0):.4f}",
                'speed': f"{message.get('Sog', 0):.1f}",
                'course': f"{message.get('Cog', 0):.1f}",
                'timestamp': metadata.get('time_utc', datetime.utcnow().isoformat())
            }
        except Exception as e:
            print(f"Error formatting position data: {e}")
            return self.latest_data

    def get_latest_data(self):
        return {
            **self.latest_data,
            'connection_status': 'connected' if self.connected else 'disconnected',
            'error': self.connection_error if self.connection_error else None
        }