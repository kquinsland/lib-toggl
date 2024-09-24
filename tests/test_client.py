"""Basic tests of the client module"""

import pytest

from lib_toggl.client import Toggl
from lib_toggl.time_entries import TimeEntry


@pytest.mark.asyncio
async def test_client_init_no_api_key():
    """Tests that client requires an API key"""
    with pytest.raises(TypeError):
        # pylint: disable=no-value-for-parameter
        _ = Toggl()  # pyright: ignore reportCallIssue


@pytest.mark.asyncio
async def test_client_init_with_api_key():
    """Tests that client requires an API key"""
    _key = "fake_api_key"
    x = Toggl(_key)
    assert x.api_key == _key


##
# Most of client is boilerplate for API calls and I'm not in the mood to mock aiohttp since the data
#   is almost always directly piped into Pydantic models.
# The update_tags() function does have some non-standard logic that's worth testing.
# But it will require mocking out some of the API calls.
# Let's call this a TODO for now.
##
