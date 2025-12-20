"""Platform for sensor integration."""
from __future__ import annotations
from datetime import datetime, timezone, timedelta

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# Import local algorithms library
from . import algorithms

SCAN_INTERVAL = timedelta(seconds=60)

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    async_add_entities([
        JulianDaySensor(),
        ModifiedJulianDaySensor(),
        DayOfWeekSensor(),
        DayOfYearSensor(),
        TimeIntervalJ2000Sensor(),
    ])

class JulianDaySensor(SensorEntity):
    """
    Representation of a Julian Day Sensor.
    Calculates the Julian Day number for the current UTC time.
    """

    _attr_name = "Julian Day"
    _attr_unique_id = "julian_day"
    _attr_icon = "mdi:calendar-clock"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "d" 

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        now = datetime.now(timezone.utc)
        # Calculate JD using the algorithms library
        jd = algorithms.gregorian_to_jd(
            now.year, now.month, now.day, 
            now.hour, now.minute, now.second + now.microsecond/1000000.0
        )
        self._attr_native_value = round(jd, 6)

class ModifiedJulianDaySensor(SensorEntity):
    """
    Representation of a Modified Julian Day (MJD) Sensor.
    """

    _attr_name = "Modified Julian Day"
    _attr_unique_id = "modified_julian_day"
    _attr_icon = "mdi:calendar-clock"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "d"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        now = datetime.now(timezone.utc)
        jd = algorithms.gregorian_to_jd(
            now.year, now.month, now.day, 
            now.hour, now.minute, now.second + now.microsecond/1000000.0
        )
        mjd = algorithms.jd_to_mjd(jd)
        self._attr_native_value = round(mjd, 6)

class DayOfWeekSensor(SensorEntity):
    """
    Representation of the Day of the Week Sensor.
    """

    _attr_name = "Day of Week"
    _attr_unique_id = "day_of_week"
    _attr_icon = "mdi:calendar-week"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        now = datetime.now(timezone.utc)
        jd = algorithms.gregorian_to_jd(
            now.year, now.month, now.day, 
            now.hour, now.minute, now.second + now.microsecond/1000000.0
        )
        self._attr_native_value = algorithms.day_of_week(jd)

class DayOfYearSensor(SensorEntity):
    """
    Representation of the Day of the Year (DoY) Sensor.
    """

    _attr_name = "Day of the Year"
    _attr_unique_id = "day_of_year"
    _attr_icon = "mdi:calendar-today"
    _attr_state_class = SensorStateClass.TOTAL

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        now = datetime.now(timezone.utc)
        doy = algorithms.day_of_year(now.year, now.month, now.day)
        self._attr_native_value = doy

class TimeIntervalJ2000Sensor(SensorEntity):
    """
    Representation of a Time Interval Sensor (Days since J2000.0).
    """

    _attr_name = "Days since J2000"
    _attr_unique_id = "interval_since_j2000"
    _attr_icon = "mdi:timer-sand"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "d"

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        now = datetime.now(timezone.utc)
        
        current_jd = algorithms.gregorian_to_jd(
            now.year, now.month, now.day, 
            now.hour, now.minute, now.second + now.microsecond/1000000.0
        )
        
        j2000_jd = 2451545.0
        interval = algorithms.time_interval(j2000_jd, current_jd)
        self._attr_native_value = round(interval, 6)