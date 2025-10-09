"""Todo platform for the Mental load Assistant integration."""

from __future__ import annotations

from homeassistant.components.todo import TodoItem, TodoItemStatus, TodoListEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MentalLoadCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Mental Load to-do list."""
    coordinator: MentalLoadCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MentalLoadTodoEntity(coordinator, entry)])


class MentalLoadTodoEntity(CoordinatorEntity[MentalLoadCoordinator], TodoListEntity):
    """A to-do list entity for the Mental Load integration."""

    _attr_translation_key = "mental_load_list"

    def __init__(self, coordinator: MentalLoadCoordinator, entry: ConfigEntry) -> None:
        """Initialize the Mental Load to-do list."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_mental_load"

    @property
    def todo_items(self) -> list[TodoItem] | None:
        """Return the to-do items from the coordinator."""
        if not self.coordinator.data:
            return None

        # KORREKTUR: Die for-Schleife wurde durch eine List Comprehension ersetzt.
        return [
            TodoItem(
                summary=event.get("summary", "Unbenannter Termin"),
                status=TodoItemStatus.NEEDS_ACTION,
                uid=event["id"],
            )
            for event in self.coordinator.data
        ]
