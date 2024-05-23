"""
Very basic Toggl API wrapper
"""

from datetime import UTC, datetime
from typing import Any, List

import aiohttp
from pyrfc3339 import generate

from lib_toggl import __version__ as version

from .account import ENDPOINT as ACCOUNT_ENDPOINT
from .account import Account
from .const import USER_AGENT
from .tags import TAGS_ENDPOINT, Tag
from .time_entries import CREATE_ENDPOINT as TIME_ENTRY_CREATE_ENDPOINT
from .time_entries import EDIT_ENDPOINT as TIME_ENTRY_EDIT_ENDPOINT
from .time_entries import ENDPOINT as TIME_ENTRY_ENDPOINT
from .time_entries import EXPLICIT_ENDPOINT
from .time_entries import STOP_ENDPOINT as TIME_ENTRY_STOP_ENDPOINT
from .time_entries import TimeEntry, validate_time_entry_id, validate_workspace_id
from .workspace import ENDPOINT as WORKSPACE_ENDPOINT
from .workspace import Workspace

# Try structlog (available in dev context), fall back to stdlib logging
try:
    import structlog

    log = structlog.get_logger()

except ImportError:
    import logging

    log = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class Toggl:
    """Processes the client request

    Raises:
        ValueError: If the request method is not supported.
        ValueError: If the request URL is not valid.
        ValueError: If the request headers are not properly formatted.
        ValueError: If the request body is not properly formatted.
        ValueError: If the request timeout is not a positive number.
        ValueError: If the request fails due to network issues.
        ValueError: If the server responds with an error status code.

    Returns:
        Response: The server's response to the client's request.
    """

    # Basically everything is JSON
    _headers = {"content-type": "application/json"}

    # default API user agent value
    _user_agent = USER_AGENT

    def __init__(self, api_key: str | None) -> None:
        self.headers = {}
        self._session = aiohttp.ClientSession()

        self._account: Account | None = None
        self._current_time_entry: TimeEntry | None = None
        self._workspaces: List[Workspace] | None = None

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
        """Current API key."""
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
    async def account(self) -> Account | None:
        """Toggle Account details."""
        if self._account is None:
            self._account = await self.get_account_details()
        return self._account

    @property
    async def workspaces(self) -> List[Workspace] | None:
        """List of Workspaces the user has access to."""
        if self._workspaces is None:
            self._workspaces = await self.get_workspaces()
        return self._workspaces

    @property
    async def current_time_entry(self) -> TimeEntry | None:
        """Currently running Time Entry, if one exists."""
        if self._current_time_entry is None:
            self._current_time_entry = await self.get_current_time_entry()
        return self._current_time_entry

    async def _pre_flight_check(self):
        """Common pre-request checks"""
        if self._api_key is None:
            raise ValueError("api_key must be set before making requests.")

        if self._session.closed:
            log.error("session is closed, creating new session")
            self._session = aiohttp.ClientSession()

        # Merge common headers with instance specific headers
        self.headers.update(self._headers)

    async def do_get_request(
        self, url: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Does a GET request to the specified URL.

        Args:
            url (str): URL to send the GET request to.
            data (dict | None, optional): A dictionary to be passed as query parameters. Defaults to None.

        Returns:
            Response: The server's response to the GET request.
        """

        await self._pre_flight_check()
        log.debug("do_get_request", extra={"data": data})
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.get(
            url, headers=self.headers, auth=self._auth, params=data
        ) as resp:
            if resp.status != 200:
                log.debug("here is resp", extra={"resp": await resp.text()})
                resp.raise_for_status()
            return await resp.json()

    async def do_post_request(self, url: str, data_as_json_str: str) -> dict[str, Any]:
        """Does a POST request to the specified URL.

        Args:
            url (str): URL to send the POST request to.
            data_as_json_str (str): String encoded JSON data. Not using built-in json kwarg because we need to use the json encoder in pydantic so we can exclude None values.

        Returns:
            Response: The server's response to the POST request.
        """

        await self._pre_flight_check()

        log.debug("do_post_request", extra={"data": data_as_json_str})
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.post(
            url, headers=self.headers, auth=self._auth, data=data_as_json_str
        ) as resp:
            if resp.status != 200:
                log.debug("here is resp", extra={"resp": await resp.text()})
                resp.raise_for_status()
            return await resp.json()

    async def do_patch_request(
        self, url: str, data: dict | None = None
    ) -> dict[str, Any]:
        """Performs a PATCH request to the specified URL.

        Args:
            url (str): URL to send the PATCH request to.
            data (dict | None, optional): A dictionary to be sent as JSON in the body of the request. Defaults to None.

        Returns:
            Response: The server's response to the PATCH request.
        """
        await self._pre_flight_check()

        log.debug("do_patch_request", extra={"data": data})
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.patch(
            url, headers=self.headers, auth=self._auth, data=data
        ) as resp:
            if resp.status != 200:
                log.debug("here is resp", extra={"resp": await resp.text()})
                resp.raise_for_status()
            return await resp.json()

    async def do_put_request(self, url: str, data_as_json_str: str) -> dict[str, Any]:
        """Does PUT request to the specified URL.

        Args:
            url (str): URL to send the PUT request to.
            data (str): JSON encoded string to send in the body of the request.

        Returns:
            dict[str, Any]: JSON response from the server.
        """
        await self._pre_flight_check()

        log.debug("do_put_request", extra={"data": data_as_json_str})
        # TODO: error handling, lots of ways network/json parse can fail...
        async with self._session.put(
            url, headers=self.headers, auth=self._auth, data=data_as_json_str
        ) as resp:
            if resp.status != 200:
                log.debug("here is resp", extra={"resp": await resp.text()})
                resp.raise_for_status()

            return await resp.json()

    ##
    # Actual methods for fetching things from Toggl
    ##

    async def get_workspaces(self) -> List[Workspace]:
        """Gets a list of Workspaces the user has access to.

        Returns:
            [Workspace]: List of Workspace objects.
        """
        log.debug("get_workspaces is alive...")
        ws = await self.do_get_request(WORKSPACE_ENDPOINT)
        log.debug("get_workspaces", extra={"ws": ws})
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if ws is None:
            log.debug("No workspaces found")
            return []
        # Assuming nothing went wrong, `ws` will be a list with one json object per workspace
        return [Workspace(**x) for x in ws]  # pyright: ignore reportCallIssue

    async def get_tags(self, workspace_id: int) -> List[Tag]:
        """Returns a list of Tags for the specified workspace.

        Args:
            workspace_id (int): Workspace ID to fetch tags for.

        Returns:
            List[Tag]: List of Tag objects.
        """
        tags = await self.do_get_request(TAGS_ENDPOINT(workspace_id))
        log.debug("get_tags", extra={"tags": tags})
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if tags is None:
            log.debug("No workspaces found")
            return []
        # Assuming nothing went wrong, `tags` will be a list with one json object per tag
        return [Tag(**x) for x in tags]  # pyright: ignore reportCallIssue

    async def create_tag(self, workspace_id: int, tag_name: str) -> Tag | None:
        """Creates a new Tag in the specified workspace.

        Args:
            workspace_id (int): Workspace ID to create the tag in.
            tag_name (str): Name of the tag to create.

        Returns:
            Tag | None: Tag object if successful, else None.
        """
        body = {"name": tag_name, "workspace_id": workspace_id}
        _t = Tag(**body)
        data = _t.json(exclude_none=True)
        log.debug("create_tag. To make: %s", data)
        d = await self.do_post_request(
            TAGS_ENDPOINT(workspace_id), data_as_json_str=data
        )
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if d is None:
            log.debug("Tag not created?")
            return None
        return Tag(**d)

    async def get_time_entries(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> List[TimeEntry]:
        """Retrieves a list of Time Entries within a specific date range

        Args:
            start_date (datetime): The start date of the range.
            end_date (datetime): The end date of the range.

        Raises:
            ValueError: If the start_date is later than the end_date.
            ValueError: If either the start_date or end_date is not a valid datetime.

        Returns:
            List[TimeEntry]: A list of TimeEntry objects within the specified date range.
        """
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

        time_enttrries = await self.do_get_request(TIME_ENTRY_ENDPOINT, data=params)
        log.debug("get_time_entries", extra={"time_enttrries": time_enttrries})
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if time_enttrries is None:
            log.debug("No time entries found")
            return []
        # Assuming nothing went wrong, `time_enttrries` will be a list with one json object per time entry
        return [
            TimeEntry(**x) for x in time_enttrries  # pyright: ignore reportCallIssue
        ]

    async def get_current_time_entry(self) -> TimeEntry | None:
        """Returns active Time Entry if one is running, else None"""
        log.info("get_current_time_entry is alive...")

        cte = await self.do_get_request(f"{TIME_ENTRY_ENDPOINT}/current")
        if cte is None:
            log.debug("There doesn't seem to be a currently running Time Entry")
            return None
        try:
            log.debug("get_current_time_entry", extra={"cte": cte})
            self._current_time_entry = TimeEntry(**cte)
            return await self.current_time_entry

        # pylint: disable-next=broad-except
        except Exception as exc:
            log.debug("err", exc_info=exc)
        return None

    async def get_time_entry_by_id(self, time_entry_id: int) -> TimeEntry | None:
        """Retrieves a specific Time Entry by its ID

        Args:
            time_entry_id (int): The ID of the Time Entry to retrieve.

        Returns:
            TimeEntry | None: The TimeEntry object with the given ID if it exists, else None.
        """
        log.info("get_current_time_entry is alive...")

        te = await self.do_get_request(f"{EXPLICIT_ENDPOINT(time_entry_id)}")
        if te is None:
            log.debug("There doesn't seem to be a currently running Time Entry")
            return None
        try:
            log.debug("get_current_time_entry", extra={"cte": te})
            return TimeEntry(**te)

        # pylint: disable-next=broad-except
        except Exception as exc:
            log.debug("err", exc_info=exc)
        return None

    async def get_account_details(self) -> Account | None:
        """Retrieves the account details

        Returns:
            Account | None: The Account object containing the details of the current account if the operation is successful, else None.
        """
        d = await self.do_get_request(ACCOUNT_ENDPOINT)
        log.debug("get_account_details", extra={"data": d})
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if d is None:
            return None
        self._account = Account(**d)
        return await self.account

    async def create_new_time_entry(self, te: TimeEntry) -> TimeEntry | None:
        """Creates a new Toggl Track Time Entry

        Args:
            te (TimeEntry): Time Entry object to create. If the `start` property is not set, it will be set to the current time.

        Raises:
            ValueError: If the provided TimeEntry object is not valid.
            ValueError: If the operation on the TimeEntry object fails.

        Returns:
            TimeEntry: The newly created TimeEntry object if the operation is successful, else None.
        """
        log.debug("create_new_time_entry is alive...")
        # This will be the first POST/PUT request
        # Also need to collect / validate data
        # Can leverage pydantic for that, but need to be mindful of that class / what data ONLY comes back with a GET
        # Versus what data should be populated for a PUT
        ##
        _url = TIME_ENTRY_CREATE_ENDPOINT(te.workspace_id)

        if not te.start:
            te.start = datetime.now(UTC)
            log.debug("te.start was not set, setting to %s", te.start)

        # Render out to JSON, exclude the things that user didn't set
        # In testing, it looks like tag_ids will override tags.
        # If tags is set to a list of strings but tag_action is not set or tag_ids is an empty list, the server will NOT
        #   set the tags and will create a new time track entry with the empty list of tags.
        # So, we default both tags and tag_ids to None and let the user pick which to set.
        # TODO: i'll want to do more sophisticated validation / coercion to handle this case.
        #   e.g: tag_action should remain None unless tags is a list with at least one string, then default to add
        data = te.json(exclude_none=True)
        log.debug("create_new_time_entry. To make: %s", data)
        d = await self.do_post_request(_url, data_as_json_str=data)
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if d is None:
            return None
        return TimeEntry(**d)

    async def _persist_time_entry(self, te: TimeEntry) -> TimeEntry | None:
        """Lower level level API that attemmpts to update state for an existing Time Entry.
        Can be used directly, is meant to be used by higher level API functions like edit_time_entry().

        Args:
            te (TimeEntry): Object representing the desired state.

        Returns:
            TimeEntry | None: Object representing the presisted state or None on failure.
        """
        # If user creates a TimeEntry directly and tries to use _persist_time_entry instead of create()
        validate_workspace_id(te.workspace_id)
        validate_time_entry_id(te.id)

        _url = TIME_ENTRY_EDIT_ENDPOINT(
            te.workspace_id, te.id  # pyright: ignore reportArgumentType
        )
        data = te.json(exclude_none=True)
        log.debug("_persist_time_entry. sending: %s", data)
        d = await self.do_put_request(_url, data_as_json_str=data)
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if d is None:
            return None
        return TimeEntry(**d)

    async def edit_time_entry(self, local_te: TimeEntry) -> TimeEntry | None:
        """High level API that attemmpts to update state for an existing Time Entry.

        Modifying some aspects of a Time Entry are trivial, such as the description.
        Tags are a bit more convoluted. Depending on the passed time entry and the desired state
            several API calls may be needed.
        This is abstracted away in the update_tags() function which is called by this function.
        That function is meant to be relatively cheap to call if the user ends up passing in a desired set of tags
            that perfectly overlaps with the current set of tags on the Time Entry.
        In that case, we'll just move on to updating the description for the Time Entry

        Args:
            local_te (TimeEntry): Object representing the desired state.

        Returns:
            TimeEntry | None: Object representing the presisted state or None on failure.
        """
        log.debug("edit_time_entry is alive. Starting with %s", local_te)

        # To determine if we have any tags to update, we first need to ask the server what IT thinks the passed in TE looks like
        remote_te = await self.get_time_entry_by_id(
            local_te.id  # pyright: ignore reportArgumentType
        )
        log.debug("remote_te: %s", remote_te)
        if remote_te is None:
            log.error(
                "Failed to fetch remote Time Entry. Can't edit what server doesn't know about."
            )
            return None

        # update_tags() requires non-None inputs
        if local_te.tags is None:
            local_te.tags = []
        # Do tag updates, if any.
        updated_te = await self.update_tags(remote_te, local_te.tags)
        log.debug("edit_time_entry: updated_te: %s", updated_te)
        if updated_te is None:
            log.error(
                "Failed to update tags on Time Entry, attempting to update other fields, though"
            )
            updated_te = local_te
        # Update the description to match what the user passed in
        updated_te.description = local_te.description
        log.debug("edit_time_entry: [returning] updated_te: %s", updated_te)
        return await self._persist_time_entry(updated_te)

    async def stop_time_entry(self, te: TimeEntry) -> TimeEntry | None:
        """Summary

        Args:
            te (TimeEntry): The TimeEntry object to be processed.

        Returns:
            TimeEntry | None: The processed TimeEntry object if successful, None otherwise.
        """
        validate_workspace_id(te.workspace_id)
        validate_time_entry_id(te.id)

        log.info(
            "stop_time_entry is alive...",
            extra={"id": te.id, "workspace": te.workspace_id},
        )
        _url = TIME_ENTRY_STOP_ENDPOINT(
            te.workspace_id, te.id  # pyright: ignore reportArgumentType
        )

        d = await self.do_patch_request(_url)
        # As of now, not a ton of error handling in the do_*_request functions.
        # We do basic checking here to make sure pylance is happy.
        if d is None:
            return None
        return TimeEntry(**d)

    async def update_tags(self, te: TimeEntry, new_tags: List[str]) -> TimeEntry | None:
        """
        A wrapper to abstract the logic of updating the tags on a TimeEntry object.

        The Toggl API docs are a bit confusing and ambiguous about how tags are handled when updating a Time Entry.
        As it turns out, the "just give us the string, we'll do the rest" behavior applies only when creating a new Time Entry.

        If you have an existing Time Entry and want to update the tags, you must provide the tag IDs, not the tag strings.

        Furthermore, if you clear and then set the `tag_ids` field on a Time Entry and POST/PUT it to the server, you'd expect
            the time entry to have just the new tags, right? Wrong.
        The tags on the Time Entry will depend on what the `tag_action` was set to when the POST/PUT request was made with
            the tag_ids.

        So instead, we offer a nice simple interface to the user: just give us the list of strings you want the Time Entry to have.
        This means that we need to figure out which tags are new and which already exist in the workspace
        New tags need to be created and then we can get the tag IDs.

        Then we need to figure out which tag_ids should be added and or removed from the Time Entry.

        We take a best effort approach to updating the tags on the Time Entry. Add new tags first, then remove old tags.
        This way, even if there's an error removing tags, the Time Entry will still have the new tags that the user wanted.
        They can always manually search for the old tag(s) and remove them if necessary.
        """
        validate_workspace_id(te.workspace_id)
        validate_time_entry_id(te.id)
        if new_tags is None:
            raise ValueError("new_tags is required.")

        log.debug("Updating tags on TimeEntry: %s.", te.description)
        # TODO: much better error handling
        known_tags = await self.get_tags(te.workspace_id)
        if known_tags is None:
            log.error("Failed to get tags for workspace: %s.", te.workspace_id)
            return

        # Even though get_tags should never return a Tag with either field as None
        # Pylance only sees that Pydantic has either None or Int/Str for the fields
        known_tags = {
            tag.name: tag.id
            for tag in known_tags
            if tag.name is not None and tag.id is not None
        }
        log.debug("Found %s known tags: %s.", len(known_tags), known_tags)

        # Figure out what tags need to be created, added and removed
        tags_to_create = set(new_tags) - set(known_tags.keys())
        log.debug("%s Tags to create: %s", len(tags_to_create), tags_to_create)

        # Pylance only sees that `tags` is Optional[List[str]]. It knows that Pydanitc's Optional means None is possible.
        # It can't see that there is a post validation function that replaces None with [].
        tags_to_add = set(new_tags) - set(te.tags)  # pyright: ignore reportArgumentType
        log.debug("%s Tags to add: %s", len(tags_to_add), tags_to_add)

        # fmt: off
        tags_to_remove = set(te.tags) - set(new_tags) # pyright: ignore reportArgumentType
        log.debug("%s Tags to remove: %s", len(tags_to_remove), tags_to_remove)

        if (
            len(tags_to_create) == 0
            and len(tags_to_add) == 0
            and len(tags_to_remove) == 0
        ):
            log.info("No changes to tags needed.")
            return te

        # Technically, if the TimeEntry that the user passed in has a valid ID but a different description / start / stop / duration... etc
        #   from what the server has handy, calling _persist_time_entry will update the Time Entry to match the user's Time Entry in it's entirety.
        # The name of this function implies that it's only for updating tags so we unset any attributes on the current Time Entry that aren't tags.
        # This way, when we persist the Time Entry, we only update the tags on the server.
        # Easiest way to do this is to clone the Time Entry that user passed in and then unset the non-tag fields; leave the TE they passed in alone.
        ##
        te = TimeEntry(
            id=te.id,
            workspace_id=te.workspace_id,
            tags=te.tags,
            tag_ids=te.tag_ids,
            tag_action=te.tag_action,
        )

        # Create the new tags
        for tag in tags_to_create:
            log.info("Creating new tag: %s", tag)
            new_tag = await self.create_tag(te.workspace_id, tag)
            if new_tag is None:
                log.error("Failed to create tag: %s", tag)
                continue
            if new_tag.name is None or new_tag.id is None:
                log.error(
                    "Tag creation failed: [%s] (%s,%s)", tag, new_tag.id, new_tag.name
                )
                continue
            # Creation was successful, add the new tag to the known tags
            known_tags[new_tag.name] = new_tag.id

        # Assuming nothing went wrong, we should now have an updated list of known tags
        for tag in tags_to_add:
            log.info("Adding tag: %s", tag)
            if tag not in known_tags:
                log.error("Tag not found in known tags: %s. Creation failed?", tag)
                continue
            # Update the Time Entry with the new tag ID and name to be sure.
            # API appears to be inconsistent about weather the string or the ID matters more depending on the action!?!!
            ##
            # pylint: disable=no-member
            te.tag_ids.append(known_tags[tag]) # pyright: ignore reportOptionalMemberAccess
            # pylint: disable=no-member
            te.tags.append(tag) # pyright: ignore reportOptionalMemberAccess

        updated_te = await self._persist_time_entry(te)
        if updated_te is None:
            log.error(
                "Failed to update Time Entry with new tags; refusing to remove old tags (if any)"
            )
            return

        # Assuming nothing broke, the time entry should have tag IDs for new tags and old tags.
        # Clear the tag_ids / strings, set the tag_action to remove, and then set string/ids to the tags that need to be removed.
        if len(tags_to_remove) > 0:
            updated_te.tag_ids = []
            updated_te.tags = []
            updated_te.tag_action = "remove"
            for tag in tags_to_remove:
                log.debug("Removing tag: %s", tag)
                if tag not in known_tags:
                    log.error("Tag not found in known tags: %s. Cannot remove.", tag)
                    continue
                # Again, when remove is the action, behavior is inconsistent when the tag_ids versus tag strings don't match
                updated_te.tag_ids.append(known_tags[tag])
                updated_te.tags.append(tag)

        # Should return a Time Entry with just the new tags
        return await self._persist_time_entry(updated_te)


# TODO: General exceptions to handle and wrap
# Trying to stop a TE that was deleted:
#   aiohttp.client_exceptions.ClientResponseError: 404, message='Not Found',
# Incorrect basic auth
#   aiohttp.client_exceptions.ClientResponseError: 401, message='Unauthorized',
# Trying to stop an entry on a workspace that's not mine
#   aiohttp.client_exceptions.ClientResponseError: 403, message='Forbidden',
#       409 when trying to stop a time entry that's already stopped... etc
# When sending a request BODY with verb GET (or just a bad request in general)
#   aiohttp.client_exceptions.ClientResponseError: 400, message='Bad Request',
##
# TODO: can probably re-factor a bit and remove the do_$VERB_request functions and replace with
#   a singular do_request which takes an aiohttp.request() object
