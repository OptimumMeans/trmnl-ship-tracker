from datetime import datetime
import pytz

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M UTC')
    except (ValueError, AttributeError):
        return timestamp

def format_coordinates(lat: float, lon: float) -> tuple:
    """Format coordinates with proper symbols"""
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    return (
        f"{abs(lat):.4f}°{lat_dir}",
        f"{abs(lon):.4f}°{lon_dir}"
    )