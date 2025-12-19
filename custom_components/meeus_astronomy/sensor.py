"""Sensor platform for Meeus Astronomy."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LONGITUDE, CONF_LATITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN, CONF_LOCATION_NAME
from .algorithms import (
    get_julian_day, 
    get_mean_sidereal_time_greenwich, 
    get_local_sidereal_time, 
    degrees_to_hms
)

_LOGGER = logging.getLogger(__name__)

# Update every second to maintain a "clock-like" feel for Sidereal Time
SCAN_INTERVAL = timedelta(seconds=1)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform from a config entry."""
    longitude = entry.data[CONF_LONGITUDE]
    latitude = entry.data[CONF_LATITUDE]
    name = entry.data[CONF_LOCATION_NAME]

    async_add_entities([MeeusSiderealTimeSensor(hass, name, longitude, latitude)], True)


class MeeusSiderealTimeSensor(SensorEntity):
    """Sensor for Local Sidereal Time (LMST)."""

    _attr_has_entity_name = True
    _attr_translation_key = "sidereal_time"

    def __init__(self, hass, name, longitude, latitude):
        """Initialize the sensor."""
        self._hass = hass
        self._longitude = longitude
        self._latitude = latitude
        self._attr_name = f"{name} Sidereal Time"
        self._attr_unique_id = f"meeus_lst_{latitude}_{longitude}"
        self._attr_icon = "mdi:clock-star-four-points"
        self._state = None
        self._attrs = {}

    async def async_added_to_hass(self):
        """Register the time interval callback when entity is added."""
        self.async_on_remove(
            async_track_time_interval(
                self._hass, self._update_state, SCAN_INTERVAL
            )
        )

    async def _update_state(self, now=None):
        """Update the sensor state and attributes."""
        # Get current UTC time
        utc_now = datetime.now(timezone.utc)
        
        # 1. Calculate Julian Day
        jd = get_julian_day(utc_now)
        
        # 2. Calculate GMST (Greenwich)
        gmst_deg = get_mean_sidereal_time_greenwich(jd)
        
        # 3. Calculate LMST (Local)
        lmst_deg = get_local_sidereal_time(gmst_deg, self._longitude)
        
        # The main state is the formatted HH:MM:SS string
        self._state = degrees_to_hms(lmst_deg)
        
        # Detailed attributes for advanced usage
        self._attrs = {
            "julian_day": round(jd, 6),
            "gmst_degrees": round(gmst_deg, 4),
            "gmst_hms": degrees_to_hms(gmst_deg),
            "lmst_degrees": round(lmst_deg, 4),
            "longitude_used": self._longitude
        }
        
        # Write state to Home Assistant
        self.async_write_ha_state()

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attrs