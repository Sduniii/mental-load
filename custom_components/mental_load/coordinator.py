"""Data update coordinator for the Mental load Assistant integration."""
from __future__ import annotations

import logging
from datetime import timedelta
import uuid

from googleapiclient.discovery import build
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    AbstractOAuth2FlowHandler,
    OAuth2Session,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

# ... (PROMPT und API_URL bleiben gleich) ...
PROMPT = """
Analysiere den folgenden Kalendereintrag und zerlege ihn in konkrete,
umsetzbare To-Do-Punkte, die den damit verbundenen "Mental Load" repräsentieren.
Antworte nur mit einer Liste von Aufgaben, eine pro Zeile. Formuliere die Aufgaben kurz und prägnant.
Wenn der Eintrag keine Aktion erfordert (z.B. "Urlaub"), antworte mit "NICHTS ZU TUN".

Kalendereintrag:
Titel: {summary}
Beschreibung: {description}
"""
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"


class MentalLoadCoordinator(DataUpdateCoordinator[list[dict]]):
    """A coordinator to fetch and analyze calendar events."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        implementation: AbstractOAuth2FlowHandler,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mental Load Assistant",
            update_interval=timedelta(minutes=15),
        )
        self.entry = entry
        # Erstellt die OAuth2-Session, die die Token automatisch verwaltet
        self.session = OAuth2Session(hass, entry, implementation)
        self.websession = async_get_clientsession(hass)

    async def _async_update_data(self) -> list[dict]:
        """Fetch and process calendar events."""
        api_key = self.entry.options.get("llm_api_key")
        if not api_key:
            _LOGGER.error("Gemini API key is not configured")
            return []

        events = await self.hass.async_add_executor_job(self._fetch_events)
        all_tasks = []

        for event in events:
            summary = event.get("summary", "Unbenannter Termin")
            description = event.get("description", "")
            prompt_text = PROMPT.format(summary=summary, description=description)
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

            try:
                # Token automatisch erneuern, falls nötig
                await self.session.async_ensure_token_valid()
                
                async with self.websession.post(GEMINI_API_URL.format(api_key=api_key), json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    tasks_text = result["candidates"][0]["content"]["parts"][0]["text"]

            except Exception as e:
                _LOGGER.error("Error calling Gemini API for event '%s': %s", summary, e)
                continue

            if "NICHTS ZU TUN" in tasks_text:
                continue

            for task_summary in tasks_text.strip().split("\n"):
                task_summary = task_summary.lstrip("- ").strip()
                if task_summary:
                    all_tasks.append({
                        "summary": task_summary,
                        "uid": str(uuid.uuid4()),
                        "event_id": event["id"],
                        "event_summary": summary,
                    })
        return all_tasks

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