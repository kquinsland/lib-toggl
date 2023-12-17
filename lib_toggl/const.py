"""
Constants for the Toggl API.
Implements a subset of the complete API.

"""

BASE = "https://api.track.toggl.com/api/v9"

CURRENT_RUNNING_TIME = f"{BASE}/time_entries/current"
PROJECTS = f"{BASE}/projects"
START_TIME = f"{BASE}/time_entries/start"
TIME_ENTRIES = f"{BASE}/time_entries"

WORKSPACES = "https://api.track.toggl.com/api/v8/workspaces"
