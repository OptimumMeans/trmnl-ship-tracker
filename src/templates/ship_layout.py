from PIL import ImageFont, ImageDraw
import os
from datetime import datetime

class ShipLayout:
    def __init__(self):
        self.font = ImageFont.load_default()
        
    def draw(self, draw, data):
        if not data:
            self._draw_no_data(draw)
            return
            
        # Draw background rectangle for ship info
        draw.rectangle([30, 30, 770, 90], fill=1)  # White background
        
        # Draw ship info with borders
        draw.text((40, 40), f"Vessel: {data['ship_name']}", font=self.font, fill=0)
        draw.text((40, 65), f"MMSI: {data['mmsi']}", font=self.font, fill=0)
        
        # Draw position section with background
        draw.rectangle([30, 110, 770, 170], fill=1)
        draw.text((40, 120), "Position:", font=self.font, fill=0)
        draw.text((40, 145), f"Lat: {data['lat']}° Lon: {data['lon']}°", font=self.font, fill=0)
        
        # Draw speed and course section
        draw.rectangle([30, 190, 370, 250], fill=1)  # Speed box
        draw.rectangle([400, 190, 770, 250], fill=1)  # Course box
        
        draw.text((40, 200), f"Speed: {data['speed']} knots", font=self.font, fill=0)
        draw.text((410, 200), f"Course: {data['course']}°", font=self.font, fill=0)
        
        # Draw timestamp at bottom
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            time_str = data['timestamp']
            
        draw.text((40, 420), f"Last Update: {time_str}", font=self.font, fill=0)
        
    def _draw_no_data(self, draw):
        # Draw error state with background
        draw.rectangle([30, 30, 770, 90], fill=1)
        draw.text((40, 40), "No vessel data available", font=self.font, fill=0)
        draw.text((40, 65), "Waiting for updates...", font=self.font, fill=0)