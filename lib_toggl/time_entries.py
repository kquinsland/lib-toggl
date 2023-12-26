"""Various type/class definitions for the Organizations bit of the Toggle API
Parse/Coercion done by Pydantic
"""
from datetime import datetime
from typing import List, Optional

import structlog
from pydantic import BaseModel, Field, FieldSerializationInfo, field_serializer
from pyrfc3339 import generate

from .const import BASE, DEFAULT_CREATED_BY

log = structlog.get_logger(__name__)

ENDPOINT = f"{BASE}/me/time_entries"


@staticmethod
# pylint: disable=invalid-name
def CREATE_ENDPOINT(workspace_id: int = None) -> str:
    """Returns the endpoint for creating a new time entry in the specified workspace"""
    if not workspace_id:
        raise ValueError("workspace_id must be specified")
    return f"{BASE}/workspaces/{workspace_id}/time_entries"


@staticmethod
# pylint: disable=invalid-name
def STOP_ENDPOINT(workspace_id: int = None, time_entry_id: int = None) -> str:
    """Returns the endpoint for creating a new time entry in the specified workspace"""
    if not workspace_id:
        raise ValueError("workspace_id must be specified")
    if not time_entry_id:
        raise ValueError("time_entry_id must be specified")
    return f"{BASE}/workspaces/{workspace_id}/time_entries/{time_entry_id}/stop"


class TimeEntry(BaseModel):
    """Class representing the Toggl organization object.
    Leverages dataclass to cut down on boilerplate code.
    See: https://developers.track.toggl.com/docs/api/time_entries#200
    """

    # When user creates a TimeEntry, this will not be known; it is set by server when successful CREATE request
    id: Optional[int] = Field(default=None)
    # Toggle API has a few fields that are "legacy" and "should not be used" but are still
    #   returned by the API. We store the new/current/correct field value and set up aliases
    #   so the old field names still work.
    ##
    # TODO: do I want to frozen everything? May want to support updating a TE in the future...?
    workspace_id: int = Field(description="Workspace ID, required.", default=None)
    project_id: Optional[int] = Field(description="Project ID, optional.", default=None)
    task_id: Optional[int] = Field(alias="tid", default=None)
    user_id: int = Field(
        default=None,
        description="Time Entry creator ID, if omitted will use the requester user ID",
    )

    billable: bool = Field(
        default=False,
        description="Whether the time entry is marked as billable, optional, default false",
    )

    created_with: str = Field(
        description="Must be provided when creating a time entry and should identify the service/application used to create it",
        # value will NOT be provided when making a "get current" call so we default to None
        default=DEFAULT_CREATED_BY,
    )

    # Toggl API wants everything in RFC3339 format which is just a specific flavor of ISO8601
    # Internally, just store everything as a datetime with UTC timezone and only convert to
    #   RFC3339 when we need to send it to the API.
    start: datetime = Field(default_factory=datetime.utcnow)
    stop: Optional[datetime] = Field(
        default=None,
        # pylint: disable=line-too-long
        description="Stop time in UTC, can be omitted if it's still running or created with 'duration'. If 'stop' and 'duration' are provided, values must be consistent (start + duration == stop)",
    )

    # Duration in seconds
    # Should be -1 for something that's on-going but should be correct for creating an "already-done" TE
    # e.g. start + duration = stop
    # TODO: better validation around this field with the After validation
    # https://docs.pydantic.dev/2.5/concepts/validators/#before-after-wrap-and-plain-validators
    duration: int = Field(
        default=-1,
        description="Time entry duration. For running entries should be negative, preferable -1",
    )

    # Description is required when CREATING, but not required when deleting.
    description: Optional[str] = Field(
        default=None, description="Time entry description, optional"
    )
    # Can be "add" or "delete". Used when updating an existing time entry
    tag_action: Optional[str] = Field(pattern=r"^(add|delete)$", default="add")

    tags: List[str] = Field(
        default=None,
        description="Tag names, None if tags were not provided or were later deleted",
    )

    tag_ids: List[int] = Field(
        default=None,
        description="Tag IDs, None if tags were not provided or were later deleted",
    )

    # This field is deprecated for GET endpoints where the value will always be true.
    duronly: Optional[bool] = Field(
        exclude=True,
        default=False,
        repr=False,
        description="Deprecated: Used to create a time entry with a duration but without a stop time. This parameter can be ignored.",
    )
    # This appears to be the datetime server got/fulfilled request
    # Isn't something user will supply when creating a Time Entry and doesn't really serve a useful
    #   purpose so we exclude it from the model.
    at: Optional[datetime] = Field(
        exclude=True, default=None, description="When was last updated", repr=False
    )

    server_deleted_at: Optional[datetime] = Field(
        exclude=True, default=None, description="When was deleted, null if not deleted"
    )

    uid: Optional[int] = Field(
        exclude=True,
        default=None,
        repr=False,
        description="Time Entry creator ID, legacy field",
    )
    wid: Optional[int] = Field(
        exclude=True, default=None, repr=False, description="Workspace ID, legacy field"
    )
    pid: Optional[int] = Field(
        exclude=True, default=None, repr=False, description="Project ID, legacy field"
    )
    tid: Optional[int] = Field(
        exclude=True, default=None, repr=False, description="Task ID, legacy field"
    )

    # The start/stop timestamps need to be RFC3339 formatted strings
    # It would be nice if the same function could be used for both fields but
    #   there's an implementation detail that makes that difficult.
    # A typical example is creating a new Time Entry where the stop field will be None and
    #   the start field will be a datetime object.
    # The decorator can be configured to apply to both the start and stop field but an exception
    #   will be thrown if stop is None.
    # Ok, so set the check_fields input to False and then the decorator will only run on the
    #   start field, right? NOPE.
    @field_serializer("start", return_type=str, when_used="unless-none")
    def serialize_start(self, dt: datetime, _info: FieldSerializationInfo):
        """Generates rfc3339 formatted string from datetime object

        Args:
            dt (datetime): _description_
            _info (FieldSerializationInfo): _description_

        Returns:
            _type_: _description_
        """
        return generate(dt, utc=True, accept_naive=True)

    @field_serializer("stop", return_type=str, when_used="unless-none")
    def serialize_stop(self, dt: datetime, _info: FieldSerializationInfo):
        """Generates rfc3339 formatted string from datetime object

        Args:
            dt (datetime): _description_
            _info (FieldSerializationInfo): _description_

        Returns:
            _type_: _description_
        """
        return generate(dt, utc=True, accept_naive=True)


# TODO: general logic implementation around what fields are required / should be validated
#   when user is creating a new TE versus updating one versus getting current from API.
# TODO: fix: TypeError: 'TimeEntry' object is not subscriptable
