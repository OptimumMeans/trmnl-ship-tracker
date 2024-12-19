from jinja2 import Template
from PIL import Image, ImageDraw
import io
from typing import Dict
from ..templates.ship_layout import get_html_template

class DisplayGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.template = Template(get_html_template())

    def generate_bitmap(self, data: Dict) -> bytes:
        """
        Generate 1-bit bitmap for TRMNL EPD display
        """
        # Create a new blank image (1-bit color mode for EPD)
        image = Image.new('1', (self.width, self.height), 1)
        
        # Render HTML template with data
        html_content = self.template.render(**data)
        
        # Convert HTML to bitmap
        # Note: In a real implementation, you'd need a HTML to bitmap renderer
        # Here we're creating a simple representation
        draw = ImageDraw.Draw(image)
        
        # Save as BMP
        output = io.BytesIO()
        image.save(output, format='BMP')
        return output.getvalue()

    def create_display_response(self, image_data: bytes, refresh_interval: int) -> tuple:
        """
        Create response with proper TRMNL headers
        """
        return (image_data, 
                {'Content-Type': 'image/bmp',
                 'X-TRMNL-Refresh': str(refresh_interval)})