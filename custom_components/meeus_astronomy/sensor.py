"""Sensor platform for Astronomy."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .algorithms import get_julian_day
from .const import CONF_LOCATION_NAME

_LOGGER = logging.getLogger(__name__)

# Update every second
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

    # Create a data coordinator
    coordinator = AstronomyData()

    # Set up the coordinator to update every second
    async def async_update_data(now):
        """Update data."""
        await hass.async_add_executor_job(coordinator.update)

    async_track_time_interval(hass, async_update_data, SCAN_INTERVAL)

    # Add the sensors
    sensors = [
        JulianDaySensor(coordinator, name, latitude, longitude),
    ]
    async_add_entities(sensors, True)


class AstronomyData:
    """Calculates and holds the astronomical data."""

    def __init__(self):
        """Initialize the data object."""
        self.jd = None

    def update(self):
        """Update the data."""
        utc_now = datetime.now(timezone.utc)
        self.jd = get_julian_day(utc_now)


class JulianDaySensor(SensorEntity):
    """Sensor for Julian Day."""

    _attr_has_entity_name = True
    _attr_translation_key = "julian_day"
    _attr_icon = "mdi:counter"

    def __init__(
        self, coordinator: AstronomyData, name: str, latitude: float, longitude: float
    ):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_name = f"{name} Julian Day"
        self._attr_unique_id = f"astronomy_jd_{latitude}_{longitude}"

    @property
    def state(self) -> float | None:
        """Return the state of the sensor."""
        if self._coordinator.jd is None:
            return None
        return round(self._coordinator.jd, 6)

    @property
    def available(self) -> bool:
        """Return true if the sensor is available."""
        return self._coordinator.jd is not None