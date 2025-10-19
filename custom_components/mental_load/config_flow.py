"""Config flow for Mental load Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2FlowHandler,
    LocalOAuth2Implementation,
)
import voluptuous as vol

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


# ======================================================================================
# === Optionen-Flow (für LLM API-Schlüssel)
# ======================================================================================
class MentalLoadOptionsFlowHandler(OptionsFlow):
    """Verwaltet den Optionen-Dialog für den Mental Load Assistant."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialisiert den Optionen-Flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Verwaltet die Optionen für die LLM-Konfiguration."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "llm_api_key",
                        default=self.config_entry.options.get("llm_api_key", ""),
                    ): str,
                }
            ),
        )


# ======================================================================================
# === Haupt-Konfigurations-Flow (für Google)
# ======================================================================================
class MentalLoadOAuth2FlowHandler(AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Verwaltet den OAuth2-Konfigurations-Flow für den Mental Load Assistant."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Gibt den Logger zurück."""
        return _LOGGER

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> MentalLoadOptionsFlowHandler:
        """Gibt den Optionen-Flow für diesen Handler zurück."""
        return MentalLoadOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Behandelt den vom Benutzer initiierten Flow, um die Anmeldedaten zu sammeln."""
        if user_input is not None:
            # Erstellt die "Anleitung" für den OAuth-Flow
            implementation = LocalOAuth2Implementation(
                self.hass,
                DOMAIN,
                user_input["client_id"],
                user_input["client_secret"],
                "https://accounts.google.com/o/oauth2/v2/auth",
                "https://oauth2.googleapis.com/token",
            )
            
            # --- KORREKTUR HIER ---
            # Wir initialisieren die Basisklasse mit der erstellten Implementierung.
            # Dies ist der offizielle Weg, um self.flow_impl korrekt zu setzen.
            super().__init__(implementation=implementation)

            # Startet den Authentifizierungsschritt, der den Benutzer zu Google weiterleitet
            return await self.async_step_auth()

        # Zeigt das Formular an, um die Google Client ID/Secret vom Nutzer zu erfragen
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("client_id"): str,
                    vol.Required("client_secret"): str,
                }
            ),
        )

    async def async_oauth_create_entry(
        self, data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Erstellt einen Konfigurationseintrag nach erfolgreicher Authentifizierung."""
        return self.async_create_entry(title="Mental Load Assistant", data=data)