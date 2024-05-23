"""Account Information
Parse/Coercion done by Pydantic
"""

from datetime import datetime
from typing import Optional

try:
    # Pydantic v2 ships a copy of v1.
    from pydantic.v1 import BaseModel, SecretStr
except ImportError:
    # Home Assistant does not yet support v2.
    from pydantic import BaseModel, SecretStr

from .const import BASE

ENDPOINT = f"{BASE}/me"


class Account(BaseModel):
    """
    https://developers.track.toggl.com/docs/api/me#200
    """

    id: int
    api_token: SecretStr
    email: str
    fullname: str
    timezone: str
    toggl_accounts_id: str
    default_workspace_id: int
    # TODO: define weekday type, convert
    beginning_of_week: int
    image_url: str
    created_at: datetime
    updated_at: datetime
    openid_email: Optional[str]
    openid_enabled: bool
    country_id: int
    has_password: bool
    at: datetime
    # Analytics?
    intercom_hash: SecretStr
