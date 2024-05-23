"""
Constants for the Toggl API.
Implements a subset of the complete API.

"""

from . import __version__ as version

BASE = "https://api.track.toggl.com/api/v9"

CURRENT_RUNNING_TIME = f"{BASE}/time_entries/current"
PROJECTS = f"{BASE}/projects"
START_TIME = f"{BASE}/time_entries/start"

DEFAULT_CREATED_BY = "lib-toggl"
USER_AGENT = f"{DEFAULT_CREATED_BY} ({version})"
