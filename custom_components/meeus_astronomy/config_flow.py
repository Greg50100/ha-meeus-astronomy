"""Config flow for Jean Meeus Astronomy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_ELEVATION
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_NAME, CONF_LOCATION_NAME

_LOGGER = logging.getLogger(__name__)

class MeeusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Meeus Astronomy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate unique ID based on location name to prevent duplicates
            await self.async_set_unique_id(f"{user_input[CONF_LATITUDE]}_{user_input[CONF_LONGITUDE]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input[CONF_LOCATION_NAME], data=user_input)

        # Default values from Home Assistant core config
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_LOCATION_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_LATITUDE, default=self.hass.config.latitude): cv.latitude,
                    vol.Required(CONF_LONGITUDE, default=self.hass.config.longitude): cv.longitude,
                    vol.Optional(CONF_ELEVATION, default=self.hass.config.elevation): vol.Coerce(float),
                }
            ),
            errors=errors,
        )