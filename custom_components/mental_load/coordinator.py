"""Data update coordinator for the Mental load Assistant integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from googleapiclient.discovery import build

from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)


class MentalLoadCoordinator(DataUpdateCoordinator[list]):
    """A coordinator to fetch calendar events."""

    def __init__(self, hass: HomeAssistant, session: OAuth2Session) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mental Load Assistant",
            update_interval=timedelta(minutes=15),
        )
        self.session = session

    async def _async_update_data(self) -> list:
        """Fetch calendar events from the Google Calendar API."""
        return await self.hass.async_add_executor_job(self._fetch_events)

    def _fetch_events(self) -> list:
        """Fetch events sync."""
        service = build("calendar", "v3", credentials=self.session.token)
        now = dt_util.utcnow()
        time_max = now + timedelta(days=1)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
