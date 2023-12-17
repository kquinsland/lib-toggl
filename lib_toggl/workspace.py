"""_summary_
"""
from typing import Self
import structlog
from .const import BASE

log = structlog.get_logger(__name__)

ENDPOINT = f"{BASE}/workspaces"


class Workspace:
    """Class representing the Toggl Workspace object"""

    def __init__(self, **kwargs) -> Self:
        # log.info("Workspace is alive...", kwargs=kwargs)
        """
        There's lots more data in the response, but we only care about a few things ... at least for now
        """
        self._id = kwargs.get("id")
        self._org_id = kwargs.get("organization_id")
        self._name = kwargs.get("name")

    @property
    def id(self) -> int:
        """_summary_

        Returns:
            int: _description_
        """
        return self._id

    @property
    def org_id(self) -> int:
        """_summary_

        Returns:
            int: _description_
        """
        return self._org_id

    @property
    def name(self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        return self._name

    def __repr__(self):
        return f"<Workspace {self.id} {self.org_id}/{self.name}>"
