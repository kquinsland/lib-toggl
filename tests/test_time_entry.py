"""Tests Pydantic validation around Time Entry object instantiation and modification"""

# pylint: disable=missing-function-docstring

import pytest

from lib_toggl.const import BASE
from lib_toggl.time_entries import (
    CREATE_ENDPOINT,
    EDIT_ENDPOINT,
    EXPLICIT_ENDPOINT,
    STOP_ENDPOINT,
    TimeEntry,
)

##
# Mostly dumb tests to ensure that the endpoints are generated correctly.
##


def test_create_endpoint_with_valid_workspace_id():
    workspace_id = 123
    expected_endpoint = f"{BASE}/workspaces/123/time_entries"
    assert CREATE_ENDPOINT(workspace_id) == expected_endpoint


def test_create_endpoint_with_zero_workspace_id():
    workspace_id = 0
    with pytest.raises(ValueError):
        CREATE_ENDPOINT(workspace_id)


def test_create_endpoint_with_negative_workspace_id():
    workspace_id = -123
    with pytest.raises(ValueError):
        CREATE_ENDPOINT(workspace_id)


def test_create_endpoint_with_none_workspace_id():
    with pytest.raises(TypeError):
        # pylint: disable=no-value-for-parameter
        CREATE_ENDPOINT()  # pyright: ignore reportCallIssue


def test_stop_endpoint_with_valid_ws_te_ids():
    workspace_id = 123
    time_entry_id = 456
    expected_endpoint = (
        f"{BASE}/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop"
    )
    assert STOP_ENDPOINT(workspace_id, time_entry_id) == expected_endpoint


def test_stop_endpoint_with_invalid_ws_te_ids():
    workspace_id = 0
    time_entry_id = -456
    with pytest.raises(ValueError):
        STOP_ENDPOINT(workspace_id, time_entry_id)


def test_stop_endpoint_with_missing_workspace_id():
    with pytest.raises(ValueError):
        STOP_ENDPOINT(None, 456)  # pyright: ignore reportArgumentType


def test_stop_endpoint_with_missing_te_id():
    with pytest.raises(ValueError):
        STOP_ENDPOINT(123, None)  # pyright: ignore reportArgumentType


def test_stop_endpoint_with_none_workspace_id():
    with pytest.raises(TypeError):
        # pylint: disable=no-value-for-parameter
        STOP_ENDPOINT()  # pyright: ignore reportCallIssue


def test_edit_endpoint_with_valid_workspace_valid_te():
    workspace_id = 123
    time_entry_id = 456
    expected_endpoint = f"{BASE}/workspaces/{workspace_id}/time_entries/{time_entry_id}"
    assert EDIT_ENDPOINT(workspace_id, time_entry_id) == expected_endpoint


def test_edit_endpoint_with_valid_workspace_id_missing_te():
    workspace_id = 123
    with pytest.raises(TypeError):
        # pylint: disable=no-value-for-parameter
        EDIT_ENDPOINT(workspace_id)  # pyright: ignore reportCallIssue


def test_edit_endpoint_with_invalid_workspace_id_valid_te():
    te_id = 456
    with pytest.raises(ValueError):
        EDIT_ENDPOINT(None, te_id)  # pyright: ignore reportCallIssue


def test_edit_endpoint_with_valid_workspace_id_invalid_te():
    ws_id = 123
    with pytest.raises(ValueError):
        EDIT_ENDPOINT(ws_id, None)  # pyright: ignore reportCallIssue


def test_explicit_endpoint_with_valid_te_id():
    time_entry_id = 456
    expected_endpoint = f"{BASE}/me/time_entries/{time_entry_id}"
    assert EXPLICIT_ENDPOINT(time_entry_id) == expected_endpoint


def test_explicit_endpoint_with_zero_te_id():
    time_entry_id = 0
    with pytest.raises(ValueError):
        EXPLICIT_ENDPOINT(time_entry_id)


def test_explicit_endpoint_with_negative_workspace_id():
    time_entry_id = -123
    with pytest.raises(ValueError):
        EXPLICIT_ENDPOINT(time_entry_id)


def test_explicit_endpoint_with_none_workspace_id():
    with pytest.raises(TypeError):
        # pylint: disable=no-value-for-parameter
        EXPLICIT_ENDPOINT()  # pyright: ignore reportCallIssue


##
# Validating TimeEntry object instantiation with sample data from toggl API
# Note: Pydantic is already well tested so there's not a ton of value in testing the basics here.
# Most of the tests below are there to ensure that the additional validation that I added to
#   the base pydantic model is working as expected.
##


def test_time_entry_instantiation_with_valid_data():
    """Aside from the inconsistent behavior and docs, the basic Pydantic/Field() logic is sound.
    The only real thing that I had to add was when the API would return Tags = None, Tag IDs = [] or
    vice versa.
    """
    valid_no_tags = {
        "id": 123,
        "description": "Test Description",
        "tags": None,
        "tag_ids": [],
        "workspace_id": 456,
    }

    valid_te_no_tags_ids = {
        "id": 123,
        "description": "Test Description",
        "tags": [],
        "tag_ids": None,
        "workspace_id": 456,
    }

    valid_no_tags = TimeEntry(**valid_no_tags)
    valid_no_tags_ids = TimeEntry(**valid_te_no_tags_ids)

    assert valid_no_tags.id == 123
    assert valid_no_tags.id == 123

    assert valid_no_tags.workspace_id == 456
    assert valid_no_tags_ids.workspace_id == 456

    assert valid_no_tags.description == "Test Description"
    assert valid_no_tags_ids.description == "Test Description"

    # pylint: disable=use-implicit-booleaness-not-comparison
    assert valid_no_tags.tags is None
    assert valid_no_tags_ids.tags == []

    assert valid_no_tags.tag_ids == []
    assert valid_no_tags_ids.tag_ids is None
