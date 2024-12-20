import websockets
import json
import asyncio
from datetime import datetime
import ssl
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionAPI:
    def __init__(self, url, api_key):
        self.url = url
        self.api_key = api_key
        self.latest_data = {
            'ship_name': 'Initializing...',
            'mmsi': 'N/A',
            'lat': '0.0000',
            'lon': '0.0000',
            'speed': '0.0',
            'course': '0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'connection_status': 'initializing'
        }
        self.connected = False
        self.connection_error = None
        self._max_retries = 10
        self._retry_delay = 5  # Base delay in seconds
        
    async def connect_and_listen(self, mmsi):
        retry_count = 0
        
        while True:
            try:
                logger.info(f"\nAttempt {retry_count + 1} to connect to AIS Stream")
                logger.info(f"URL: {self.url}")
                logger.info(f"MMSI Filter: {mmsi}")
                
                # Configure SSL context with proper error handling
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # Establish WebSocket connection with improved timeouts
                websocket = await websockets.connect(
                    self.url,
                    ssl=ssl_context,
                    ping_interval=20,
                    ping_timeout=30,  # Increased timeout
                    close_timeout=20,  # Increased timeout
                    max_size=2**23,    # Increased message size limit
                    compression=None   # Disable compression to reduce complexity
                )
                
                logger.info("WebSocket connection established")
                self.connected = True
                self.connection_error = None
                self.latest_data['connection_status'] = 'connected'
                
                # Prepare subscription message
                subscribe_message = {
                    "APIKey": self.api_key,
                    "BoundingBoxes": [[[-90, -180], [90, 180]]],
                    "FiltersShipMMSI": [str(mmsi)],
                    "FilterMessageTypes": ["PositionReport"]
                }
                
                # Send subscription with timeout
                try:
                    await asyncio.wait_for(
                        websocket.send(json.dumps(subscribe_message)),
                        timeout=10
                    )
                    logger.info("Subscription sent successfully")
                    
                    # Reset retry count on successful connection
                    retry_count = 0
                    
                    # Main message processing loop
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            message_type = data.get('MessageType', 'unknown')
                            logger.info(f"Received message type: {message_type}")
                            
                            if message_type == 'PositionReport':
                                self.latest_data = self.format_position_data(data)
                                self.latest_data['connection_status'] = 'connected'
                                logger.info(f"Updated position: {self.latest_data['lat']}, {self.latest_data['lon']}")
                            elif message_type == 'error':
                                error_msg = data.get('error', 'Unknown error')
                                logger.error(f"Received error message: {error_msg}")
                                raise Exception(error_msg)
                                
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse message: {str(e)}")
                            continue
                            
                except asyncio.TimeoutError:
                    logger.error("Timeout while sending subscription")
                    raise
                    
            except Exception as e:
                self.connected = False
                self.connection_error = str(e)
                self.latest_data['connection_status'] = 'disconnected'
                
                retry_count += 1
                wait_time = min(300, self._retry_delay * (2 ** min(retry_count, 5)))  # Exponential backoff capped at 5 minutes
                
                logger.error(f"Connection error: {str(e)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                
                if retry_count >= self._max_retries:
                    logger.error("Max retries reached, extending retry interval")
                    retry_count = 0  # Reset count but keep longer interval
                
                self.latest_data.update({
                    'ship_name': f'Reconnecting in {wait_time}s... (Attempt {retry_count + 1}/{self._max_retries})',
                    'mmsi': mmsi,
                })
                
                logger.info(f"Waiting {wait_time} seconds before retry...")
                await asyncio.sleep(wait_time)
            
            finally:
                try:
                    await websocket.close()
                except:
                    pass

    def format_position_data(self, data):
        """Format position data with proper error handling"""
        try:
            message = data.get('Message', {}).get('PositionReport', {})
            metadata = data.get('MetaData', {})
            
            return {
                'ship_name': metadata.get('ShipName', 'Unknown Vessel'),
                'mmsi': metadata.get('MMSI', 'N/A'),
                'lat': f"{message.get('Latitude', 0):.4f}",
                'lon': f"{message.get('Longitude', 0):.4f}",
                'speed': f"{message.get('Sog', 0):.1f}",
                'course': f"{message.get('Cog', 0):.1f}",
                'timestamp': metadata.get('time_utc', datetime.utcnow().isoformat()),
                'connection_status': 'connected'
            }
            
        except Exception as e:
            logger.error(f"Error formatting position data: {str(e)}")
            return {**self.latest_data, 'error': str(e)}

    def get_latest_data(self):
        """Get latest data with connection status"""
        return {
            **self.latest_data,
            'connection_status': 'connected' if self.connected else 'disconnected',
            'error': self.connection_error
        }