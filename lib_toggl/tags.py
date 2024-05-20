"""Represents a Toggl Tag object."""

import logging
from datetime import datetime
from typing import Optional

from pydantic.v1 import BaseModel, Field

from .const import BASE

log = logging.getLogger(__name__)


@staticmethod
# pylint: disable=invalid-name
def TAGS_ENDPOINT(workspace_id: int | None) -> str:
    """Returns the endpoint for managing Tags in a particular worksapce."""
    if not workspace_id:
        raise ValueError("workspace_id must be specified")
    return f"{BASE}/workspaces/{workspace_id}/tags"


class Tag(BaseModel):
    """Class representing Tag object.
    Leverages dataclass to cut down on boilerplate code.
    See: https://engineering.toggl.com/docs/api/tags
    """

    # Name of the tag
    name: str = Field(default=None, description="Tag Name, required.")

    # Optional to account for user creating a Tag object to send to API
    id: Optional[int] = Field(default=None, description="Tag ID.")

    workspace_id: int = Field(
        description="Workspace ID tag is associated with, required.", default=None
    )

    creator_id: Optional[int] = Field(
        description="ID of the user who created the tag, optional.", default=None
    )

    at: Optional[datetime] = Field(
        exclude=True, default=None, description="When Tag was last updated", repr=False
    )

    deleted_at: Optional[datetime] = Field(
        exclude=True, default=None, description="When was deleted, null if not deleted"
    )

    # Dev docs don't explain what this is?
    permissions: Optional[str] = Field(
        default=None, exclude=True, repr=False, description="permissions"
    )
