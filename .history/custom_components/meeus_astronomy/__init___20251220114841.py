"""The Meeus Astronomy integration."""
from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from . import algorithms

_LOGGER = logging.getLogger(__name__)

# Schemas for service arguments
SERVICE_CONVERT_TO_JD = "convert_to_julian_day"
SERVICE_CONVERT_TO_GREGORIAN = "convert_to_gregorian"

# Schema for converting Date -> JD
# Required: year, month, day. Optional: hour, minute, second.
CONVERT_TO_JD_SCHEMA = vol.Schema({
    vol.Required("year"): cv.positive_int,
    vol.Required("month"): vol.All(cv.positive_int, vol.Range(min=1, max=12)),
    vol.Required("day"): vol.All(cv.positive_int, vol.Range(min=1, max=31)),
    vol.Optional("hour", default=0): vol.All(cv.positive_int, vol.Range(min=0, max=23)),
    vol.Optional("minute", default=0): vol.All(cv.positive_int, vol.Range(min=0, max=59)),
    vol.Optional("second", default=0.0): vol.Coerce(float),
})

# Schema for converting JD -> Date
# Required: julian_day
CONVERT_TO_GREGORIAN_SCHEMA = vol.Schema({
    vol.Required("julian_day"): vol.Coerce(float),
})

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Meeus Astronomy component."""
    
    async def handle_convert_to_jd(call: ServiceCall) -> dict:
        """Handle the service call to convert Gregorian date to JD."""
        year = call.data["year"]
        month = call.data["month"]
        day = call.data["day"]
        hour = call.data["hour"]
        minute = call.data["minute"]
        second = call.data["second"]

        try:
            jd = algorithms.gregorian_to_jd(year, month, day, hour, minute, second)
            response = {
                "julian_day": round(jd, 6),
                "input_date": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:05.2f}"
            }
            return response
        except Exception as err:
            _LOGGER.error("Error calculating Julian Day: %s", err)
            raise

    async def handle_convert_to_gregorian(call: ServiceCall) -> dict:
        """Handle the service call to convert JD to Gregorian date."""
        jd = call.data["julian_day"]

        try:
            y, m, d, h, mn, s = algorithms.jd_to_gregorian(jd)
            # Create a formatted ISO string and separate fields
            response = {
                "year": y,
                "month": m,
                "day": d,
                "hour": h,
                "minute": mn,
                "second": s,
                "formatted": f"{y}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{s:05.2f}"
            }
            return response
        except Exception as err:
            _LOGGER.error("Error calculating Gregorian Date: %s", err)
            raise

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_CONVERT_TO_JD,
        handle_convert_to_jd,
        schema=CONVERT_TO_JD_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_CONVERT_TO_GREGORIAN,
        handle_convert_to_gregorian,
        schema=CONVERT_TO_GREGORIAN_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    return True