from PIL import Image, ImageDraw
import io
from ..templates.ship_layout import ShipLayout

class DisplayGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.layout = ShipLayout()

    def create_display(self, ship_data):
        # Create a new blank image (1-bit color mode for EPD)
        image = Image.new('1', (self.width, self.height), 1)
        draw = ImageDraw.Draw(image)
        
        # Use the layout template to draw the display
        self.layout.draw(draw, ship_data)
        
        # Convert to BMP format
        buffer = io.BytesIO()
        image.save(buffer, format='BMP')
        return buffer.getvalue()