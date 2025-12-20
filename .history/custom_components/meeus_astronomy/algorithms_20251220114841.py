import math

# ==============================================================================
# LIBRARY OF ASTRONOMICAL ALGORITHMS
# Based on "Astronomical Algorithms" by Jean Meeus (2nd Edition)
# Chapter 7: Julian Day
# ==============================================================================

def is_leap_year(year: int) -> bool:
    """
    Determines if a year is a leap year according to the Gregorian calendar.
    Necessary for the Day of the Year calculation.
    """
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        return True
    return False

def gregorian_to_jd(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: float = 0.0) -> float:
    """
    Converts a Gregorian date to Julian Day (JD).
    
    REFERENCE: Page 60-61, Formula 7.1
    
    BOOK FORMULAS:
    If M > 2, then Y and M remain unchanged.
    If M = 1 or 2, then Y = Y - 1 and M = M + 12.
    
    In the Gregorian calendar:
    A = INT(Y / 100)
    B = 2 - A + INT(A / 4)
    
    JD = INT(365.25(Y + 4716)) + INT(30.6001(M + 1)) + D + B - 1524.5
    
    Args:
        year (Y): Year (e.g., 2024)
        month (M): Month (1-12)
        day (D): Day of the month (with decimals to include time)
    """
    # 1. Handle January/February (Page 61)
    if month <= 2:
        year -= 1
        month += 12
    
    # 2. Calculate A and B for the Gregorian calendar (Page 61)
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    
    # 3. Add the day fraction (Time) to day D
    day_fraction = day + (hour + minute / 60 + second / 3600) / 24.0
    
    # 4. Formula 7.1
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day_fraction + B - 1524.5
    
    return jd

def jd_to_gregorian(jd: float):
    """
    Converts a Julian Day (JD) to a Gregorian date.
    
    REFERENCE: Page 63, Inverse Algorithm
    
    BOOK FORMULAS:
    JD = JD + 0.5
    Z = Integer part of JD
    F = Fractional part of JD
    
    If Z < 2299161, A = Z
    Else:
        alpha = INT((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - INT(alpha / 4)
        
    B = A + 1524
    C = INT((B - 122.1) / 365.25)
    D = INT(365.25 * C)
    E = INT((B - D) / 30.6001)
    
    Day of month (with decimals) = B - D - INT(30.6001 * E) + F
    """
    jd_adjusted = jd + 0.5
    Z = int(jd_adjusted)
    F = jd_adjusted - Z
    
    if Z < 2299161:
        A = Z
    else:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
        
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    
    # Calculate day with its fraction
    day_with_fraction = B - D - int(30.6001 * E) + F
    day = int(day_with_fraction)
    
    if E < 14:
        month = E - 1
    else:
        month = E - 13
        
    if month > 2:
        year = C - 4716
    else:
        year = C - 4715
        
    # Convert day fraction to H:M:S
    fractional_day = day_with_fraction - day
    total_seconds = fractional_day * 86400
    
    hour = int(total_seconds // 3600)
    total_seconds %= 3600
    minute = int(total_seconds // 60)
    second = round(total_seconds % 60, 4)
    
    return year, month, day, hour, minute, second

def jd_to_mjd(jd: float) -> float:
    """
    Calculates the Modified Julian Day (MJD).
    REFERENCE: Page 63
    FORMULA: MJD = JD - 2400000.5
    """
    return jd - 2400000.5

def mjd_to_jd(mjd: float) -> float:
    """
    Converts MJD to JD.
    """
    return mjd + 2400000.5

def day_of_week(jd: float) -> str:
    """
    Calculates the day of the week.
    REFERENCE: Page 65
    FORMULA: (JD + 1.5) modulo 7
    """
    wd = int(jd + 1.5) % 7
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return days[wd]

def day_of_year(year: int, month: int, day: int) -> int:
    """
    Calculates the day number in the year (DoY).
    REFERENCE: Page 65
    """
    if is_leap_year(year):
        K = 1
    else:
        K = 2
        
    N = int((275 * month) / 9) - K * int((month + 9) / 12) + day - 30
    return N

def time_interval(jd1: float, jd2: float) -> float:
    """
    Calculates the time interval in days between two dates.
    REFERENCE: Page 66
    """
    return abs(jd2 - jd1)