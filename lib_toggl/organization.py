"""Various type/class definitions for the Organizations bit of the Toggle API
Parse/Coercion done by Pydantic
"""

try:
    # Pydantic v2 ships a copy of v1.
    from pydantic.v1 import BaseModel
except ImportError:
    # Home Assistant does not yet support v2.
    from pydantic import BaseModel


from .const import BASE

ENDPOINT = f"{BASE}/organizations"


class Organization(BaseModel):
    """Class representing the Toggl organization object.
    Leverages dataclass to cut down on boilerplate code.
    See: https://developers.track.toggl.com/docs/api/workspaces#200
    """
