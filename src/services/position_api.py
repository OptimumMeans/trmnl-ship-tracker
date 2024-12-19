import requests
from typing import Dict, Optional

class PositionAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_vessel_position(self, mmsi: str) -> Optional[Dict]:
        """
        Fetch vessel position data from position-api
        """
        try:
            response = requests.get(f"{self.base_url}/{mmsi}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching position: {e}")
            return None

    def format_position_data(self, data: Dict) -> Dict:
        """
        Format raw position data for display
        """
        if not data:
            return {
                'ship_name': 'Unknown',
                'mmsi': 'N/A',
                'lat': 'N/A',
                'lon': 'N/A',
                'speed': 'N/A',
                'course': 'N/A',
                'timestamp': 'N/A'
            }

        return {
            'ship_name': data.get('name', 'Unknown'),
            'mmsi': data.get('mmsi', 'N/A'),
            'lat': f"{data.get('lat', 0):.4f}",
            'lon': f"{data.get('lon', 0):.4f}",
            'speed': data.get('speed', 'N/A'),
            'course': data.get('course', 'N/A'),
            'timestamp': data.get('timestamp', 'N/A')
        }