"""Basic tests of the client module"""

import pytest

from lib_toggl import client


@pytest.mark.asyncio
async def test_client_init():
    """Tests that client can be instantiated correctly and that all calls before setting the api_key fail"""
    api_client = client.Toggl()
    assert api_client is not None
    assert api_client.api_key is None

    # Try to get current time entry w/o api_key
    with pytest.raises(ValueError):
        await api_client.get_current_time_entry()

    # Set API key to invalid value, get ValueError
    with pytest.raises(ValueError):
        api_client.api_key = ""

    # Set API key to valid value, get no ValueError
    try:
        api_client.api_key = "1234567890"
        assert True
    # pylint: disable=broad-except
    except Exception as ex:
        assert False, f"'Setting API key didn't work! ex: '{ex}'"


# TODO: lots more tests, specifically around the optional/required fields in Pydantic models
# TODO: mock the async http
