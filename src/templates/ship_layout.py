from PIL import ImageFont
import os

class ShipLayout:
    def __init__(self):
        self.font = ImageFont.load_default()
        
    def draw(self, draw, data):
        if not data:
            self._draw_no_data(draw)
            return
            
        # Draw ship info
        draw.text((40, 40), f"Vessel: {data['ship_name']}", font=self.font, fill=0)
        draw.text((40, 70), f"MMSI: {data['mmsi']}", font=self.font, fill=0)
        
        # Draw position
        draw.text((40, 110), "Position:", font=self.font, fill=0)
        draw.text((40, 130), f"Lat: {data['lat']}°", font=self.font, fill=0)
        draw.text((40, 150), f"Lon: {data['lon']}°", font=self.font, fill=0)
        
        # Draw speed and course
        draw.text((40, 190), f"Speed: {data['speed']} knots", font=self.font, fill=0)
        draw.text((40, 210), f"Course: {data['course']}°", font=self.font, fill=0)
        
        # Draw timestamp
        draw.text((40, 250), f"Last Update: {data['timestamp']}", font=self.font, fill=0)
        
    def _draw_no_data(self, draw):
        draw.text((40, 40), "No vessel data available", font=self.font, fill=0)
        draw.text((40, 70), "Waiting for updates...", font=self.font, fill=0)