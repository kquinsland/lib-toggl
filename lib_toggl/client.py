"""
Very basic Toggl API wrapper

Order of importance for implementation

- Create/Update/Stop time entries
- Get current running time entry
- Projects
- Client
"""

import json
from base64 import b64encode
from urllib.request import Request, urlopen

import certifi
import structlog

from .workspace import ENDPOINT as WORKSPACE_ENDPOINT
from .workspace import Workspace
from .organization import ENDPOINT as ORGANIZATIONS_ENDPOINT
from .organization import Organization


log = structlog.get_logger(__name__)


class Toggl:
    """Basic wrapper for the Toggl API"""

    # Basically everything is JSON
    _headers = {"content-type": "application/json"}

    # default API user agent value
    _user_agent = "lib-toggl"

    def __init__(self) -> None:
        # TODO: implement session/cookie or can I get away with basic api token when I do HA integration?
        self.headers = {"Authorization": ""}
        self._api_key = None

    @property
    def api_key(self):
        """_summary_"""
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        """
        Toggl supports Basic Authentication with two flavors: email/pass and api-token.
        Only supports the api-token flavor; oddly enough the api token takes place of the email and
            the password is `api_token`.
        """

        log.info("api_key.setter", api_key=value)
        self._api_key = value

        _encoded = b64encode(
            format(f"{self._api_key}:api_token").encode("utf-8")
        ).decode("utf-8")
        self.headers["Authorization"] = f"Basic {_encoded}"

    def do_request(self, request: Request):
        """_summary_

        Args:
            request (_type_): _description_

        Returns:
            _type_: _description_
        """
        log.info("do_request is alive...", request=request)
        log.info("do_request is alive...", headers=self.headers)
        log.info("do_request is alive...", _headers=self._headers)

        # Add auth and other stuff
        self.headers.update(self._headers)

        request.headers = self.headers
        # TODO: error handling, lots of ways network/json parse can fail...
        with urlopen(request, cafile=certifi.where()) as response:
            log.info("do_request", response=response)
            return json.loads(response.read())

    def get_workspaces(self) -> [Workspace]:
        """_summary_

        Returns:
            [Workspace]: _description_
        """
        log.info("get_workspaces is alive...")
        d = self.do_request(Request(WORKSPACE_ENDPOINT))
        log.info("get_workspaces", d=d)
        return [Workspace(**x) for x in d]

    def get_organizations(self) -> [Organization]:
        """_summary_

        Returns:
            [Workspace]: _description_
        """
        log.info("get_organizations is alive...")
        d = self.do_request(Request(ORGANIZATIONS_ENDPOINT))
        log.info("get_workspaces", d=d)
        return [Organization(**x) for x in d]


#
