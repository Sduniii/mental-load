"""The Mental load Assistant integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)

from .const import DOMAIN
from .coordinator import MentalLoadCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mental load Assistant from a config entry."""
    implementation = await async_get_config_entry_implementation(hass, entry)
    session = OAuth2Session(hass, entry, implementation)

    # Erstelle den Koordinator
    coordinator = MentalLoadCoordinator(hass, session)

    # Lade die initialen Daten
    await coordinator.async_config_entry_first_refresh()

    # Speichere den Koordinator, damit die Plattformen darauf zugreifen können
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Leite das Setup an die To-Do-Plattform weiter
    await hass.config_entries.async_forward_entry_setups(entry, ["todo"])

    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, ["todo"]):
        hass.data[DOMAIN].pop(entry.entry_id)
        return unloaded
    return False

async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    # Lädt die Integration neu, wenn die Optionen geändert werden
    await hass.config_entries.async_reload(entry.entry_id)
