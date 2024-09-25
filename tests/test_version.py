import importlib.metadata
import re


def test_version_found():
    from lib_toggl import __version__

    assert __version__ is not None
    assert re.match(r"\d+\.\d+\.\d+", __version__)


def test_version_not_found(monkeypatch):
    # patching importlib.metadata.version() to raise an exception
    def _version_raise(distribution_name):
        raise importlib.metadata.PackageNotFoundError()

    monkeypatch.setattr(importlib.metadata, "version", _version_raise)

    from lib_toggl import __version__

    assert __version__ is None
