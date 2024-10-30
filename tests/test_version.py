"""
Test the version of the package.
"""

import importlib.metadata
import re


def test_version_found():
    """Assuming importlib.metadata.version() works, confirm version is a string."""
    from lib_toggl import __version__  # pylint: disable=import-outside-toplevel

    assert __version__ is not None
    assert re.match(r"\d+\.\d+\.\d+", __version__)


def test_version_not_found(monkeypatch):
    """Mock importlib error, confirm version is None."""

    # patching importlib.metadata.version() to raise an exception
    def _version_raise(distribution_name):
        raise importlib.metadata.PackageNotFoundError()

    # Works when only test run, reliably fails when run as part of the full suite
    # Going to be _so much fun_ to figure out why ;P
    monkeypatch.setattr(importlib.metadata, "version", _version_raise)
    from lib_toggl import __version__  # pylint: disable=import-outside-toplevel

    assert __version__ is None
