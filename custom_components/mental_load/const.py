"""Constants for the Mental load Assistant integration."""

# The domain of your integration. Should be unique amongst all integrations.
DOMAIN = "mental_load"

# Scopes provide access to certain parts of the Google API.
# We are requesting read-only access to the user's calendar.
OAUTH2_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
