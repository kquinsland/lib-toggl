"""lib-toggl
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("lib-toggl")
except PackageNotFoundError:
    __version__ = None


__all__ = ["client", "account", "time_entries"]
