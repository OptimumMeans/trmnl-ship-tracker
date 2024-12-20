from PIL import ImageFont, ImageDraw
from datetime import datetime
import os

class ShipLayout:
    def __init__(self):
        # Using default font since we're working with e-ink display
        self.font = ImageFont.load_default()
        
    def draw(self, draw, data):
        """Draw the ship tracking display using TRMNL design system"""
        if not data or data.get('connection_status') != 'connected':
            self._draw_error_state(draw, data)
            return
            
        # Main container view
        self._draw_container(draw)
        
        # Ship information section
        self._draw_ship_info(draw, data)
        
        # Position section
        self._draw_position(draw, data)
        
        # Navigation data section
        self._draw_navigation_data(draw, data)
        
        # Status bar
        self._draw_status_bar(draw, data)
    
    def _draw_container(self, draw):
        """Draw main container with border"""
        # Using view view--full from TRMNL design system
        draw.rectangle([10, 10, 790, 470], outline=0)
        
    def _draw_ship_info(self, draw, data):
        """Draw ship identification section"""
        # Using layout layout--col gap--medium
        y_start = 30
        
        # Title bar equivalent
        draw.rectangle([30, y_start, 770, y_start + 40], fill=0)
        draw.text((40, y_start + 10), data['ship_name'], font=self.font, fill=1)
        
        # MMSI with label--outline style
        draw.rectangle([30, y_start + 50, 770, y_start + 80], fill=1)
        draw.text((40, y_start + 60), f"MMSI: {data['mmsi']}", font=self.font, fill=0)
        
    def _draw_position(self, draw, data):
        """Draw position information"""
        # Using layout layout--col gap--small
        y_start = 160
        
        # Section title
        draw.text((40, y_start), "Current Position", font=self.font, fill=0)
        
        # Position data using value value--large
        draw.rectangle([30, y_start + 20, 770, y_start + 60], fill=1)
        position_text = f"Lat: {data['lat']}° Lon: {data['lon']}°"
        draw.text((40, y_start + 30), position_text, font=self.font, fill=0)
        
    def _draw_navigation_data(self, draw, data):
        """Draw speed and course information"""
        # Using grid grid--cols-2 gap--medium
        y_start = 240
        
        # Speed section
        draw.rectangle([30, y_start, 380, y_start + 60], fill=1)
        draw.text((40, y_start + 10), "Speed", font=self.font, fill=0)
        draw.text((40, y_start + 30), f"{data['speed']} knots", font=self.font, fill=0)
        
        # Course section
        draw.rectangle([420, y_start, 770, y_start + 60], fill=1)
        draw.text((430, y_start + 10), "Course", font=self.font, fill=0)
        draw.text((430, y_start + 30), f"{data['course']}°", font=self.font, fill=0)
        
    def _draw_status_bar(self, draw, data):
        """Draw status bar with timestamp"""
        # Using layout layout--bottom
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            time_str = str(data['timestamp'])
            
        # Status bar with bg-gray-1
        draw.rectangle([10, 430, 790, 470], fill=1)
        draw.text((20, 440), f"Last Update: {time_str}", font=self.font, fill=0)
        
    def _draw_error_state(self, draw, data):
        """Draw error state when no data is available"""
        # Using layout layout--col gap--large
        
        # Error title
        draw.rectangle([30, 30, 770, 70], fill=0)
        draw.text((40, 40), "Connection Status", font=self.font, fill=1)
        
        # Error message
        draw.rectangle([30, 90, 770, 150], fill=1)
        status = "Disconnected" if data else "No Data Available"
        if data and data.get('error'):
            status = f"Error: {data['error']}"
        draw.text((40, 100), status, font=self.font, fill=0)
        
        # Reconnection message if applicable
        if data and 'ship_name' in data and 'Reconnecting' in data['ship_name']:
            draw.text((40, 130), data['ship_name'], font=self.font, fill=0)