"""Various type/class definitions for the Organizations bit of the Toggle API
Parse/Coercion done by Pydantic
"""
from datetime import datetime
from typing import Any, Optional

import structlog
from pydantic import BaseModel, SecretStr

from .const import BASE

log = structlog.get_logger(__name__)

ENDPOINT = f"{BASE}/organizations"


class Organization(BaseModel):
    """Class representing the Toggl organization object.
    Leverages dataclass to cut down on boilerplate code.
    See: https://developers.track.toggl.com/docs/api/workspaces#200
    """
