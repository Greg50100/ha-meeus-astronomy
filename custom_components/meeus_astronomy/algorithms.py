"""
Implementation of Jean Meeus 'Astronomical Algorithms'.
Pure Python implementation to ensure compatibility with Home Assistant OS.
"""
import math
from datetime import datetime

def get_julian_day(date_utc: datetime) -> float:
    """
    Calculate Julian Day (JD) from a UTC datetime object.
    Based on Jean Meeus, Astronomical Algorithms, Chapter 7.
    """
    Y = date_utc.year
    M = date_utc.month
    D = date_utc.day
    
    # Decimal part of the day including hours, minutes, seconds
    h = date_utc.hour
    m = date_utc.minute
    s = date_utc.second
    day_fraction = (h + m / 60.0 + s / 3600.0) / 24.0
    
    # Adjust months for Jan and Feb
    if M <= 2:
        Y -= 1
        M += 12
        
    A = math.floor(Y / 100)
    B = 2 - A + math.floor(A / 4)
    
    JD = math.floor(365.25 * (Y + 4716)) + math.floor(30.6001 * (M + 1)) + D + B - 1524.5
    return JD + day_fraction

def get_julian_centuries(jd: float) -> float:
    """Calculate Julian Centuries (T) from J2000.0."""
    return (jd - 2451545.0) / 36525.0

def get_mean_sidereal_time_greenwich(jd: float) -> float:
    """
    Calculate Mean Sidereal Time at Greenwich (GMST) in degrees.
    Meeus Chapter 12, Formula 12.4.
    """
    T = get_julian_centuries(jd)
    
    # Formula 12.4 (IAU 1982)
    mst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + \
          0.000387933 * (T**2) - (T**3) / 38710000.0
          
    # Normalize to 0-360 degrees
    return mst % 360.0

def get_local_sidereal_time(gmst_deg: float, longitude: float) -> float:
    """
    Calculate Local Sidereal Time (LMST) in degrees.
    
    Args:
        gmst_deg: Greenwich Mean Sidereal Time in degrees.
        longitude: Observer's longitude (Positive East, Negative West).
                   e.g., Cherbourg is approx -1.62.
    """
    return (gmst_deg + longitude) % 360.0

def degrees_to_hms(degrees: float) -> str:
    """Convert degrees (0-360) to a string formatted as HH:MM:SS."""
    hours_float = degrees / 15.0
    h = int(hours_float)
    m = int((hours_float - h) * 60)
    s = int((((hours_float - h) * 60) - m) * 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def degrees_to_decimal_hours(degrees: float) -> float:
    """Convert degrees (0-360) to decimal hours."""
    return degrees / 15.0