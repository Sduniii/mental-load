# Mental Load Assistant für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)

Der **Mental Load Assistant** ist eine benutzerdefinierte Integration für Home Assistant, die dir hilft, deinen "Mental Load" zu visualisieren und zu bewältigen. Sie verbindet sich mit deinem Google Kalender, analysiert anstehende Termine mithilfe von künstlicher Intelligenz (Google Gemini) und wandelt sie in eine übersichtliche To-Do-Liste um.

Anstatt nur "Geburtstagsparty für Max vorbereiten" im Kalender zu sehen, generiert die Integration konkrete Aufgaben wie "Kuchen kaufen", "Geschenk einpacken" und "Gästeliste bestätigen", um den unsichtbaren Planungsaufwand sichtbar zu machen.

---

## Features

-   **Google Kalender-Integration**: Liest automatisch Termine aus deinem primären Google Kalender.
-   **KI-gestützte Aufgabenzerlegung**: Nutzt die Google Gemini API, um aus einem einzigen Termin mehrere umsetzbare To-Do-Punkte zu erstellen.
-   **Dynamische To-Do-Liste**: Stellt die generierten Aufgaben als `todo`-Entität in Home Assistant dar, die du auf deinem Dashboard anzeigen kannst.
-   **Einfache Konfiguration**: Einrichtung und Verwaltung erfolgen vollständig über die Home Assistant-Benutzeroberfläche.

---

## Voraussetzungen

Bevor du diese Integration installierst, stelle sicher, dass du die folgenden Dinge vorbereitet hast:

1.  **HACS installiert**: Diese Integration wird am einfachsten über den [Home Assistant Community Store (HACS)](https://hacs.xyz/) installiert.
2.  **Google Cloud Projekt**: Du benötigst ein Google Cloud Projekt mit aktivierter **Google Calendar API**.
3.  **Google OAuth Client ID und Secret**: Innerhalb deines Google Cloud Projekts musst du "OAuth 2.0-Anmeldedaten" für eine Webanwendung erstellen.
    * Gehe zu [APIs & Dienste > Anmeldedaten](https://console.cloud.google.com/apis/credentials).
    * Klicke auf **+ Anmeldedaten erstellen** -> **OAuth-Client-ID**.
    * Wähle als Anwendungstyp **Webanwendung**.
    * Füge unter **Autorisierte Weiterleitungs-URIs** die folgende URI hinzu: `https://my.home-assistant.io/redirect/oauth`.
    * Speichere die **Client-ID** und den **Clientschlüssel**.
4.  **Google Gemini API Key**: Du benötigst einen API-Schlüssel für die KI-Analyse.
    * Erstelle diesen im [Google AI Studio](https://ai.google.dev/) unter **"Get API key"**.

---

## Installation

1.  **HACS Repository hinzufügen**:
    * Gehe in HACS zu **Integrationen**.
    * Klicke auf die drei Punkte oben rechts und wähle **Benutzerdefinierte Repositories**.
    * Füge die URL deines GitHub-Repositorys (`https://github.com/Sduniii/mental-load`) als **Integration** hinzu und klicke auf **Hinzufügen**.
2.  **Integration installieren**:
    * Suche in HACS nach "Mental Load Assistant" und klicke auf **Installieren**.
3.  **Home Assistant neu starten**: Starte Home Assistant neu, um die Integration zu laden.

---

## Konfiguration

Nach der Installation musst du die Integration in Home Assistant einrichten.

1.  **Integration hinzufügen**:
    * Gehe zu **Einstellungen > Geräte & Dienste**.
    * Klicke unten rechts auf **+ Integration hinzufügen**.
    * Suche nach "Mental Load Assistant" und wähle ihn aus.
2.  **Google-Anmeldedaten eingeben**:
    * Es öffnet sich ein Formular. Gib hier die **Client-ID** und den **Clientschlüssel** aus deinem Google Cloud Projekt ein.
3.  **Mit Google authentifizieren**:
    * Du wirst zu einer Google-Anmeldeseite weitergeleitet. Melde dich an und erlaube der Anwendung den Zugriff auf deinen Kalender.
    * Nach erfolgreicher Authentifizierung wirst du zurück zu Home Assistant geleitet.
4.  **Gemini API-Schlüssel konfigurieren**:
    * Die Integration ist nun hinzugefügt. Klicke auf der Integrations-Kachel auf **Konfigurieren**.
    * Gib deinen **Gemini API-Schlüssel** in das Feld ein und speichere.

Die Einrichtung ist damit abgeschlossen! Die Integration beginnt nun, deine Kalendertermine abzurufen und zu analysieren.

---

## Benutzung

Nach der Konfiguration wird eine neue Entität erstellt: `todo.mental_load_assistant`.

Du kannst diese Entität zu deinem Lovelace-Dashboard hinzufügen, indem du die **To-do-Liste**-Karte verwendest. Die Liste aktualisiert sich automatisch alle 15 Minuten mit den aus deinen Kalendereinträgen generierten Aufgaben.

---

## Beitrag leisten

Fehler, Funktionswünsche und Pull Requests sind herzlich willkommen! Bitte erstelle bei Problemen oder Ideen einen [Issue](https://github.com/Sduniii/mental-load/issues).

## Lizenz

Dieses Projekt steht unter der [Apache 2.0-Lizenz](LICENSE).