"""Config flow for Mental load Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import config_entry_oauth2_flow
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

        # Zeigt das Formular an (Texte werden aus strings.json geladen)
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
class MentalLoadOAuth2FlowHandler(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Verwaltet den OAuth2-Konfigurations-Flow für den Mental Load Assistant."""

    DOMAIN = DOMAIN
    VERSION = 1

    @property
    def logger(self) -> logging.Logger:
        """Gibt den Logger zurück."""
        return _LOGGER

    # Verbindet den Haupt-Flow mit dem Optionen-Flow
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
        """
        Wird aufgerufen, wenn der Nutzer die Integration hinzufügt.
        Da wir Application Credentials verwenden, leiten wir den Nutzer
        direkt zur Authentifizierung weiter.
        """
        # Startet den OAuth-Flow. Home Assistant holt sich die
        # global gespeicherten "Google"-Anmeldedaten.
        return await self.async_step_auth()

    async def async_oauth_create_entry(
        self, data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Erstellt einen Konfigurationseintrag nach erfolgreicher Authentifizierung."""
        return self.async_create_entry(title="Mental Load Assistant", data=data)