"""Various type/class definitions for the Organizations bit of the Toggle API
Parse/Coercion done by Pydantic
"""

from pydantic import BaseModel

from .const import BASE

ENDPOINT = f"{BASE}/organizations"


class Organization(BaseModel):  # pyright: ignore[reportGeneralTypeIssues]
    """Class representing the Toggl organization object.
    Leverages dataclass to cut down on boilerplate code.
    See: https://developers.track.toggl.com/docs/api/workspaces#200
    """
