"""Sensor platform for Meeus Astronomy."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import logging
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .algorithms import (
    degrees_to_decimal_hours,
    degrees_to_hms,
    get_julian_day,
    get_local_sidereal_time,
    get_mean_sidereal_time_greenwich,
)
from .const import CONF_LOCATION_NAME

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

    # Create a data coordinator
    coordinator = MeeusAstronomyData(longitude)

    # Set up the coordinator to update every second
    async def async_update_data(now):
        """Update data."""
        await hass.async_add_executor_job(coordinator.update)

    async_track_time_interval(hass, async_update_data, SCAN_INTERVAL)

    # Add the sensors
    sensors = [
        MeeusJulianDaySensor(coordinator, name, latitude, longitude),
        MeeusGMSTSensor(coordinator, name, latitude, longitude),
        MeeusLMSTSensor(coordinator, name, latitude, longitude),
    ]
    async_add_entities(sensors, True)


class MeeusAstronomyData:
    """Calculates and holds the astronomical data."""

    def __init__(self, longitude: float):
        """Initialize the data object."""
        self._longitude = longitude
        self.jd = None
        self.gmst_deg = None
        self.lmst_deg = None

    def update(self):
        """Update the data."""
        utc_now = datetime.now(timezone.utc)
        self.jd = get_julian_day(utc_now)
        self.gmst_deg = get_mean_sidereal_time_greenwich(self.jd)
        self.lmst_deg = get_local_sidereal_time(self.gmst_deg, self._longitude)


class MeeusJulianDaySensor(SensorEntity):
    """Sensor for Julian Day."""

    _attr_has_entity_name = True
    _attr_translation_key = "julian_day"
    _attr_icon = "mdi:counter"

    def __init__(
        self, coordinator: MeeusAstronomyData, name: str, latitude: float, longitude: float
    ):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_name = f"{name} Julian Day"
        self._attr_unique_id = f"meeus_jd_{latitude}_{longitude}"

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


class MeeusGMSTSensor(SensorEntity):
    """Sensor for Greenwich Mean Sidereal Time (GMST)."""

    _attr_has_entity_name = True
    _attr_translation_key = "gmst"
    _attr_icon = "mdi:clock-star-four-points-outline"

    def __init__(
        self, coordinator: MeeusAstronomyData, name: str, latitude: float, longitude: float
    ):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_name = f"{name} GMST"
        self._attr_unique_id = f"meeus_gmst_{latitude}_{longitude}"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self._coordinator.gmst_deg is None:
            return None
        return degrees_to_hms(self._coordinator.gmst_deg)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self._coordinator.gmst_deg is None:
            return {}
        return {
            "degrees": round(self._coordinator.gmst_deg, 4),
            "decimal_hours": round(
                degrees_to_decimal_hours(self._coordinator.gmst_deg), 4
            ),
        }

    @property
    def available(self) -> bool:
        """Return true if the sensor is available."""
        return self._coordinator.gmst_deg is not None


class MeeusLMSTSensor(SensorEntity):
    """Sensor for Local Mean Sidereal Time (LMST)."""

    _attr_has_entity_name = True
    _attr_translation_key = "lmst"
    _attr_icon = "mdi:clock-star-four-points"

    def __init__(
        self, coordinator: MeeusAstronomyData, name: str, latitude: float, longitude: float
    ):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._attr_name = f"{name} LMST"
        self._attr_unique_id = f"meeus_lmst_{latitude}_{longitude}"

    @property
    def state(self) -> str | None:
        """Return the state of the sensor."""
        if self._coordinator.lmst_deg is None:
            return None
        return degrees_to_hms(self._coordinator.lmst_deg)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self._coordinator.lmst_deg is None:
            return {}
        return {
            "degrees": round(self._coordinator.lmst_deg, 4),
            "decimal_hours": round(
                degrees_to_decimal_hours(self._coordinator.lmst_deg), 4
            ),
            "longitude": self._coordinator._longitude,
        }

    @property
    def available(self) -> bool:
        """Return true if the sensor is available."""
        return self._coordinator.lmst_deg is not None