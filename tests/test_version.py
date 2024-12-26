"""
Test the version of the package.
"""

import re


def test_version_found():
    """Assuming importlib.metadata.version() works, confirm version is a string."""
    from lib_toggl import __version__  # pylint: disable=import-outside-toplevel

    assert __version__ is not None
    assert re.match(r"\d+\.\d+\.\d+", __version__)
