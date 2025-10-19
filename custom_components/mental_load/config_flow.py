"""Config flow for Mental load Assistant."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.config_entries import ConfigFlowResult, OptionsFlow, ConfigEntry
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2FlowHandler,
    LocalOAuth2Implementation,
)

from .const import DOMAIN

class MentalLoadOptionsFlowHandler(OptionsFlow):
    """Handle an options flow for Mental Load."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "llm_api_key",
                        default=self.config_entry.options.get("llm_api_key"),
                    ): str,
                }
            ),
        )

class MentalLoadOAuth2FlowHandler(AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Handle an OAuth2 config flow for Mental load Assistant."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Return logger."""
        return logging.getLogger(__name__)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initiated by the user to collect credentials."""
        if user_input is not None:
            implementation = LocalOAuth2Implementation(
                self.hass,
                DOMAIN,
                user_input["client_id"],
                user_input["client_secret"],
                "https://accounts.google.com/o/oauth2/v2/auth",
                "https://oauth2.googleapis.com/token",
            )
            self.async_register_implementation(self.hass, implementation)

            return await self.async_step_auth()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("client_id"): str,
                    vol.Required("client_secret"): str,
                }
            ),
        )

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create an entry for the flow."""
        return self.async_create_entry(title="Mental load Assistant", data=data)
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> MentalLoadOptionsFlowHandler:
        """Get the options flow for this handler."""
        return MentalLoadOptionsFlowHandler(config_entry)

