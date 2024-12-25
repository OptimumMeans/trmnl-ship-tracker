from datetime import datetime, UTC
from typing import Tuple, Optional
from flask import jsonify

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display.
    
    Args:
        timestamp: ISO format timestamp or UTC timestamp string
        
    Returns:
        Formatted timestamp string in "YYYY-MM-DD HH:MM UTC" format
    """
    try:
        # Handle ISO format
        if 'T' in timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        # Handle "YYYY-MM-DD HH:MM:SS UTC" format
        else:
            dt = datetime.strptime(timestamp.replace(' UTC', ''), '%Y-%m-%d %H:%M:%S')
            dt = dt.replace(tzinfo=UTC)
            
        return dt.strftime('%Y-%m-%d %H:%M UTC')
    except (ValueError, AttributeError):
        return timestamp

def format_coordinates(lat: float, lon: float) -> Tuple[str, str]:
    """Format coordinates with proper directional indicators.
    
    Args:
        lat: Latitude value (-90 to 90)
        lon: Longitude value (-180 to 180)
        
    Returns:
        Tuple of (latitude string, longitude string)
    """
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    
    return (
        f"{abs(lat):.4f}°{lat_dir}",
        f"{abs(lon):.4f}°{lon_dir}"
    )

def format_speed(speed: float) -> str:
    """Format speed value for display.
    
    Args:
        speed: Speed in knots
        
    Returns:
        Formatted speed string
    """
    return f"{float(speed):.1f}"

def format_course(course: float) -> str:
    """Format course/heading value for display.
    
    Args:
        course: Course in degrees (0-360)
        
    Returns:
        Formatted course string
    """
    return f"{float(course):.1f}°"

def format_error_response(error_message: str, status_code: int = 500) -> Tuple[dict, int]:
    """Format error response for API endpoints.
    
    Args:
        error_message: Error message to return
        status_code: HTTP status code (default 500)
        
    Returns:
        Tuple of (response dict, status code)
    """
    return jsonify({
        "error": error_message,
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "error"
    }), status_code

def format_mmsi(mmsi: str) -> Optional[str]:
    """Format MMSI number for display.
    
    Args:
        mmsi: Maritime Mobile Service Identity number
        
    Returns:
        Formatted MMSI string or None if invalid
    """
    try:
        # Remove any spaces or special characters
        mmsi_clean = ''.join(filter(str.isdigit, mmsi))
        
        # MMSI should be exactly 9 digits
        if len(mmsi_clean) != 9:
            return None
            
        # Format with spaces for readability
        return f"{mmsi_clean[:3]} {mmsi_clean[3:6]} {mmsi_clean[6:]}"
    except (ValueError, TypeError, AttributeError):
        return None