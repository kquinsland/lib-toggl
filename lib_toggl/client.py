"""
Very basic Toggl API wrapper
"""
from datetime import datetime
from typing import Any

import aiohttp
import structlog
from pyrfc3339 import generate

from lib_toggl import __version__ as version

from .account import ENDPOINT as ACCOUNT_ENDPOINT
from .account import Account
from .const import USER_AGENT
from .time_entries import CREATE_ENDPOINT as TIME_ENTRY_CREATE_ENDPOINT
from .time_entries import ENDPOINT as TIME_ENTRY_ENDPOINT
from .time_entries import STOP_ENDPOINT as TIME_ENTRY_STOP_ENDPOINT
from .time_entries import TimeEntry
from .workspace import ENDPOINT as WORKSPACE_ENDPOINT
from .workspace import Workspace

log = structlog.get_logger(__name__)


# pylint: disable=too-many-instance-attributes
class Toggl:
    """Basic wrapper for the Toggl API"""

    # Basically everything is JSON
    _headers = {"content-type": "application/json"}

    # default API user agent value
    _user_agent = USER_AGENT

    def __init__(self, api_key: str = None) -> None:
        self.headers = {}
        self._session = aiohttp.ClientSession()

        self._account: Account = None
        self._current_time_entry: TimeEntry = None
        self._workspaces: [Workspace] = None

        self._auth = None

        if api_key:
            self.api_key = api_key
            self._auth = aiohttp.BasicAuth(
                login=api_key, password="api_token", encoding="utf-8"
            )
        else:
            self._api_key = None

    async def __aenter__(self):
        """Alternative: See: https://stackoverflow.com/a/67577364"""
        return self

    async def __aexit__(self, *excinfo):
        await self._session.close()

    async def close(self) -> None:
        """Closes the underlying aiohttp session.

        Needed when not using with X as Y context manager pattern."""
        await self._session.close()

    @property
    def api_key(self) -> str | None:
        """_summary_"""
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        """
        Toggl supports Basic Authentication with two flavors: email/pass and api-token.
        Only supports the api-token flavor; oddly enough the api token takes place of the email and
            the password is `api_token`.

        Toggl does not have details on what makes a valid API token.
        Looks like 32 alphanumeric chars but I don't want to code in that assumption.
        """
        if not value:
            raise ValueError("api_key cannot be None")
        self._api_key = value
        self._auth = aiohttp.BasicAuth(
            login=self._api_key, password="api_token", encoding="utf-8"
        )

    @property
    async def account(self) -> Account:
        """_summary_"""
        if self._account is None:
            self._account = await self.get_account_details()
        return self._account

    @property
    async def workspaces(self) -> [Workspace]:
        """_summary_"""
        if self._workspaces is None:
            self._workspaces = await self.get_workspaces()
        return self._workspaces

    @property
    async def current_time_entry(self) -> TimeEntry | None:
        """_summary_"""
        if self._current_time_entry is None:
            self._current_time_entry = await self.get_current_time_entry()
        return self._current_time_entry

    async def _pre_flight_check(self):
        """Common pre-request checks"""
        if self._api_key is None:
            raise ValueError("api_key must be set before making requests")

        if self._session.closed:
            log.error("session is closed, creating new session")
            self._session = aiohttp.ClientSession()

        # Merge common headers with instance specific headers
        self.headers.update(self._headers)

    async def do_get_request(
        self, url: str, data: dict | None = None
    ) -> dict[str, Any] | None:
        """_summary_

        Args:
            url (str): _description_
            data (dict | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        await self._pre_flight_check()
        log.debug("do_get_request", data=data)
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.get(
            url, headers=self.headers, auth=self._auth, params=data
        ) as resp:
            if resp.status != 200:
                resp.raise_for_status()
                log.debug("here is resp (text) ", resp=await resp.text())
            return await resp.json()

    async def do_post_request(
        self, url: str, data: dict | None = None
    ) -> dict[str, Any] | None:
        """_summary_

        Args:
            url (str): _description_
            data (dict | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        await self._pre_flight_check()

        log.debug("do_post_request", data=data)
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.post(
            url, headers=self.headers, auth=self._auth, data=data
        ) as resp:
            if resp.status != 200:
                resp.raise_for_status()
                log.debug("here is resp (text) ", resp=await resp.text())
            return await resp.json()

    async def do_patch_request(
        self, url: str, data: dict | None = None
    ) -> dict[str, Any] | None:
        """_summary_

        Args:
            url (str): _description_
            data (dict | None, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        await self._pre_flight_check()

        log.debug("do_patch_request", data=data)
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.patch(
            url, headers=self.headers, auth=self._auth, data=data
        ) as resp:
            if resp.status != 200:
                resp.raise_for_status()
                log.debug("here is resp (text) ", resp=await resp.text())
            return await resp.json()

    # Actual methods for fetching things from Toggl
    ##
    async def get_workspaces(self) -> [Workspace]:
        """_summary_

        Returns:
            [Workspace]: _description_
        """
        log.debug("get_workspaces is alive...")
        d = await self.do_get_request(WORKSPACE_ENDPOINT)
        log.debug("get_workspaces", d=d)
        return [Workspace(**x) for x in d]

    async def get_time_entries(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> [TimeEntry]:
        """_summary_"""
        log.info("get_time_entries is alive...")

        # Start and end date must be provided together
        if start_date and not end_date:
            raise ValueError("start_date provided but not end_date")
        if end_date and not start_date:
            raise ValueError("end_date provided but not start_date")

        # Toggle wants RFC3339 formatted strings
        _start = generate(start_date, utc=True, accept_naive=True)
        _end = generate(end_date, utc=True, accept_naive=True)

        # When I don't include these params, things are fine.
        # When
        params = {"start_date": _start, "end_date": _end}

        d = await self.do_get_request(TIME_ENTRY_ENDPOINT, data=params)
        return [TimeEntry(**x) for x in d]

    async def get_current_time_entry(self) -> TimeEntry | None:
        """Returns active Time Entry if one is running, else None"""
        log.info("get_current_time_entry is alive...")

        d = await self.do_get_request(f"{TIME_ENTRY_ENDPOINT}/current")
        if d is None:
            log.debug("There doesn't seem to be a currently running Time Entry")
            return None
        try:
            log.debug("get_current_time_entry", data=d)
            self._current_time_entry = TimeEntry(**d)
            return await self.current_time_entry

        # pylint: disable-next=broad-except
        except Exception as exc:
            log.debug("err", exec=exc)
        return None

    async def get_account_details(self) -> Account:
        """_summary_

        Returns:
            Account: _description_
        """
        d = await self.do_get_request(ACCOUNT_ENDPOINT)
        log.debug("get_account_details", data=d)
        self._account = Account(**d)
        return await self.account

    async def create_new_time_entry(self, te: TimeEntry) -> TimeEntry:
        """Creates a new Toggl Track Time Entry

        Args:
            te (TimeEntry): _description_

        Returns:
            TimeEntry: _description_
        """
        # This will be the first POST/PUT request
        # Also need to collect / validate data
        # Can leverage pydantic for that, but need to be mindful of that class / what data ONLY comes back with a GET
        # Versus what data should be populated for  a PUT
        _url = TIME_ENTRY_CREATE_ENDPOINT(te.workspace_id)
        # Render out to JSON, exclude the things that user didn't set
        # In testing, it looks like tag_ids will override tags.
        # If tags is set to a list of strings but tag_action is not set or tag_ids is an empty list, the server will NOT
        #   set the tags and will create a new time track entry with the empty list of tags.
        # So, we default both tags and tag_ids to None and let the user pick which to set.
        # TODO: i'll want to do more sophisticated validation / coercion to handle this case.
        #   e.g: tag_action should remain None unless tags is a list with at least one string, then default to add
        data = te.model_dump_json(exclude_none=True)
        d = await self.do_post_request(_url, data=data)

        log.debug("create_new_time_entry", data=d)
        return TimeEntry(**d)

    async def stop_time_entry(self, te: TimeEntry) -> TimeEntry:
        """Stops a running Time Entry

        Args:
            te (TimeEntry): _description_

        Returns:
            TimeEntry: _description_
        """

        # Don't bother stopping a TE that doesn't have required info or has already been stopped
        if te.workspace_id is None:
            raise ValueError("workspace_id is required")
        if te.id is None:
            raise ValueError("id is required")
        if te.stop is not None:
            raise ValueError("Time Entry is already stopped")
        if te.start is None:
            raise ValueError("Time Entry has no start time")

        log.info("stop_time_entry is alive...", id=te.id, workspace=te.workspace_id)
        _url = TIME_ENTRY_STOP_ENDPOINT(te.workspace_id, te.id)
        d = await self.do_patch_request(_url)
        return TimeEntry(**d)


# TODO: General exceptions to handle and wrap
# Trying to stop a TE that was deleted:
#   aiohttp.client_exceptions.ClientResponseError: 404, message='Not Found',
# Incorrect basic auth
#   aiohttp.client_exceptions.ClientResponseError: 401, message='Unauthorized',
# Trying to stop an entry on a workspace that's not mine
#   aiohttp.client_exceptions.ClientResponseError: 403, message='Forbidden',
# When sending a request BODY with verb GET
#   aiohttp.client_exceptions.ClientResponseError: 400, message='Bad Request',
##
# TODO: can probably re-factor a bit and remove the do_$VERB_request functions and replace with
#   a singular do_request which takes an aiohttp.request() object
