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
        self._heartbeat_interval = 15  # Send heartbeat every 15 seconds
        
    async def _heartbeat(self, websocket):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(self._heartbeat_interval)
                try:
                    await websocket.ping()
                except:
                    break
        except asyncio.CancelledError:
            pass

    async def connect_and_listen(self, mmsi):
        while True:
            try:
                logger.info("\nConnecting to AIS Stream...")
                
                # Configure SSL context
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                async with websockets.connect(
                    self.url,
                    ssl=ssl_context,
                    ping_interval=None,  # Disable built-in ping
                    close_timeout=5,
                    max_size=2**23,
                    compression=None,
                    extra_headers={
                        'User-Agent': 'TRMNL-Ship-Tracker/1.0'
                    }
                ) as websocket:
                    logger.info("WebSocket connection established")
                    self.connected = True
                    self.connection_error = None
                    self.latest_data['connection_status'] = 'connected'
                    
                    # Start heartbeat task
                    heartbeat_task = asyncio.create_task(self._heartbeat(websocket))
                    
                    try:
                        # Subscribe to ship data
                        subscribe_message = {
                            "APIKey": self.api_key,
                            "BoundingBoxes": [[[-90, -180], [90, 180]]],
                            "FiltersShipMMSI": [str(mmsi)],
                            "FilterMessageTypes": ["PositionReport"]
                        }
                        
                        await websocket.send(json.dumps(subscribe_message))
                        logger.info("Subscription sent")
                        
                        # Process incoming messages
                        async for message in websocket:
                            try:
                                data = json.loads(message)
                                message_type = data.get('MessageType', 'unknown')
                                logger.info(f"Received message type: {message_type}")
                                
                                if message_type == 'PositionReport':
                                    self.latest_data = self.format_position_data(data)
                                    logger.info(f"Updated position: {self.latest_data['lat']}, {self.latest_data['lon']}")
                                elif message_type == 'error':
                                    error_msg = data.get('error', 'Unknown error')
                                    logger.error(f"Server error: {error_msg}")
                                    raise Exception(error_msg)
                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"JSON parse error: {str(e)}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"WebSocket error: {str(e)}")
                        raise
                        
                    finally:
                        # Clean up heartbeat task
                        heartbeat_task.cancel()
                        try:
                            await heartbeat_task
                        except asyncio.CancelledError:
                            pass
                            
            except Exception as e:
                self.connected = False
                self.connection_error = str(e)
                self.latest_data.update({
                    'connection_status': 'disconnected',
                    'ship_name': 'Reconnecting...',
                    'mmsi': mmsi,
                    'error': str(e)
                })
                
                logger.error(f"Connection error: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Wait before reconnecting
                await asyncio.sleep(5)
                continue

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