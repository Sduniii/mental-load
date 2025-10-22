"""The Mental load Assistant integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import (
    async_get_config_entry_implementation,
)

from .const import DOMAIN
from .coordinator import MentalLoadCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mental load Assistant from a config entry."""
    
    # Holt die OAuth-Implementierung
    implementation = await async_get_config_entry_implementation(hass, entry)
    
    # Erstellt die Coordinator-Instanz
    coordinator = MentalLoadCoordinator(hass, entry, implementation)

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(options_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, ["todo"])

    return True


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unloaded := await hass.config_entries.async_unload_platforms(entry, ["todo"]):
        hass.data[DOMAIN].pop(entry.entry_id)
        return unloaded
    return False