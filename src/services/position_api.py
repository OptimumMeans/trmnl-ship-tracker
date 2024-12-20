import websockets
import json
import asyncio
from datetime import datetime
import ssl
import traceback

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
        print(f"PositionAPI initialized with URL: {url}, API key length: {len(api_key)}")

    async def connect_and_listen(self, mmsi):
        retry_count = 0
        while True:
            try:
                print(f"\nAttempt {retry_count + 1} to connect to AIS Stream")
                print(f"URL: {self.url}")
                print(f"MMSI Filter: {mmsi}")
                
                # Configure SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # Set up connection with detailed error handling
                try:
                    websocket = await websockets.connect(
                        self.url,
                        ssl=ssl_context,
                        ping_interval=20,
                        ping_timeout=20,
                        close_timeout=15
                    )
                except Exception as conn_err:
                    print(f"Connection failed: {str(conn_err)}")
                    print(f"Traceback: {traceback.format_exc()}")
                    raise
                
                print("WebSocket connection established successfully")
                self.connected = True
                self.connection_error = None
                
                # Prepare subscription message
                subscribe_message = {
                    "APIKey": self.api_key,
                    "BoundingBoxes": [[[-90, -180], [90, 180]]],
                    "FiltersShipMMSI": [str(mmsi)],
                    "FilterMessageTypes": ["PositionReport"]
                }
                
                # Log subscription attempt (without showing full API key)
                safe_message = subscribe_message.copy()
                safe_message["APIKey"] = f"{self.api_key[:5]}...{self.api_key[-5:]}"
                print(f"Sending subscription: {json.dumps(safe_message, indent=2)}")
                
                try:
                    await websocket.send(json.dumps(subscribe_message))
                    print("Subscription message sent successfully")
                    
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            message_type = data.get('MessageType', 'unknown')
                            print(f"Received message type: {message_type}")
                            
                            if message_type == 'PositionReport':
                                self.latest_data = self.format_position_data(data)
                                print(f"Updated position: {self.latest_data['lat']}, {self.latest_data['lon']}")
                            elif message_type == 'error':
                                print(f"Received error message: {data.get('error', 'Unknown error')}")
                                raise Exception(data.get('error', 'Unknown error from AIS Stream'))
                                
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse message: {e}")
                            print(f"Raw message: {message[:200]}...")
                            continue
                            
                except websockets.exceptions.ConnectionClosed as e:
                    print(f"Connection closed while sending/receiving: {e}")
                    raise
                    
            except Exception as e:
                self.connected = False
                self.connection_error = str(e)
                print(f"Error in connection loop: {str(e)}")
                print(f"Full traceback: {traceback.format_exc()}")
                
                retry_count += 1
                wait_time = min(30, retry_count * 5)  # Exponential backoff up to 30 seconds
                
                self.latest_data.update({
                    'ship_name': f'Reconnecting in {wait_time}s... ({str(e)[:50]})',
                    'mmsi': mmsi,
                })
                
                print(f"Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)

    def format_position_data(self, data):
        try:
            message = data['Message']['PositionReport']
            metadata = data.get('MetaData', {})
            
            formatted = {
                'ship_name': metadata.get('ShipName', 'Unknown Vessel'),
                'mmsi': metadata.get('MMSI', 'N/A'),
                'lat': f"{message.get('Latitude', 0):.4f}",
                'lon': f"{message.get('Longitude', 0):.4f}",
                'speed': f"{message.get('Sog', 0):.1f}",
                'course': f"{message.get('Cog', 0):.1f}",
                'timestamp': metadata.get('time_utc', datetime.utcnow().isoformat())
            }
            print(f"Formatted data: {json.dumps(formatted, indent=2)}")
            return formatted
            
        except Exception as e:
            print(f"Error formatting position data: {str(e)}")
            print(f"Raw data: {json.dumps(data, indent=2)[:500]}...")
            return self.latest_data

    def get_latest_data(self):
        data = {
            **self.latest_data,
            'connection_status': 'connected' if self.connected else 'disconnected',
            'error': self.connection_error
        }
        print(f"Returning status: {json.dumps(data, indent=2)}")
        return data