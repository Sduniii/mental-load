"""Data update coordinator for the Mental load Assistant integration."""
from __future__ import annotations

import logging
from datetime import timedelta
import uuid

import google.generativeai as genai
from googleapiclient.discovery import build
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

# Der Prompt, der die Magie bewirkt
PROMPT = """
Analysiere den folgenden Kalendereintrag und zerlege ihn in konkrete,
umsetzbare To-Do-Punkte, die den damit verbundenen "Mental Load" repräsentieren.
Antworte nur mit einer Liste von Aufgaben, eine pro Zeile. Formuliere die Aufgaben kurz und prägnant.
Wenn der Eintrag keine Aktion erfordert (z.B. "Urlaub"), antworte mit "NICHTS ZU TUN".

Kalendereintrag:
Titel: {summary}
Beschreibung: {description}
"""


class MentalLoadCoordinator(DataUpdateCoordinator[list]):
    """A coordinator to fetch calendar events."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, session: OAuth2Session) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Mental Load Assistant",
            update_interval=timedelta(minutes=15),
        )
        self.session = session
        self.entry = entry

    async def _async_update_data(self) -> list[dict]:
        """Fetch and process calendar events."""
        api_key = self.entry.options.get("llm_api_key")
        if not api_key:
            _LOGGER.error("LLM API key is not configured")
            return []

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")

        events = await self.hass.async_add_executor_job(self._fetch_events)
        all_tasks = []

        for event in events:
            summary = event.get("summary", "Unbenannter Termin")
            description = event.get("description", "")
            
            prompt = PROMPT.format(summary=summary, description=description)
            
            try:
                response = await model.generate_content_async(prompt)
                tasks_text = response.text
            except Exception as e:
                _LOGGER.error("Error calling Gemini API for event '%s': %s", summary, e)
                continue

            if "NICHTS ZU TUN" in tasks_text:
                continue

            # Erstelle eine Aufgabe für jede Zeile in der KI-Antwort
            for task_summary in tasks_text.strip().split("\n"):
                if task_summary: # Ignoriere leere Zeilen
                    all_tasks.append({
                        "summary": task_summary,
                        "uid": str(uuid.uuid4()), # Eindeutige ID für jede Aufgabe
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
