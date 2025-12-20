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
    This formula is valid for both Gregorian and Julian calendars.
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
        
    # Check if date is in Gregorian calendar
    if Y > 1582 or (Y == 1582 and M > 10) or (Y == 1582 and M == 10 and D >= 15):
        A = math.floor(Y / 100)
        B = 2 - A + math.floor(A / 4)
    else:
        B = 0
    
    JD = math.floor(365.25 * (Y + 4716)) + math.floor(30.6001 * (M + 1)) + D + B - 1524.5
    return JD + day_fraction