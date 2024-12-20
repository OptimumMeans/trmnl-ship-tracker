import requests
from typing import Dict, Optional

class PositionAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present

    def get_vessel_position(self, mmsi: str) -> Optional[Dict]:
        """
        Fetch vessel position data from position-api
        """
        try:
            # First try with MMSI as path parameter
            url = f"{self.base_url}/{mmsi}"
            print(f"Attempting to fetch position from: {url}")  # Debug print
            
            response = requests.get(url)
            print(f"API Response Status: {response.status_code}")  # Debug print
            print(f"API Response Content: {response.text}")  # Debug print
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Error fetching position: {str(e)}")
            
            # Try alternative endpoint format if first attempt fails
            try:
                url = f"{self.base_url}?mmsi={mmsi}"
                print(f"Retrying with query parameter: {url}")  # Debug print
                
                response = requests.get(url)
                print(f"Second attempt Status: {response.status_code}")  # Debug print
                print(f"Second attempt Content: {response.text}")  # Debug print
                
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                print(f"Error on second attempt: {str(e)}")
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