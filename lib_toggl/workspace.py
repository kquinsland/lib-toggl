"""Various type/class definitions for the Workspaces bit of the Toggle API
Parse/Coercion done by Pydantic
"""
from datetime import datetime
from typing import Any, Optional

import structlog
from pydantic import BaseModel, Field, SecretStr

from .const import BASE

log = structlog.get_logger(__name__)

ENDPOINT = f"{BASE}/workspaces"


class CSVUpload(BaseModel):
    """_summary_"""

    at: datetime
    log_id: int


class Subscription(BaseModel):
    """Machine generated class representing the Toggl Subscription object."""

    auto_renew: bool
    # Docs say type is: models.CardDetails
    # But not sure where that's actually defined / I don't have an example of it.
    card_details: Any
    company_id: int
    # Docs say type is: models.ContactDetail
    # But not sure where that's actually defined / I don't have an example of it.
    contact_detail: Any
    created_at: str
    currency: str
    customer_id: int
    deleted_at: datetime
    last_pricing_plan_id: int
    organization_id: int
    # Docs say type is: models.PaymentDetails
    # But not sure where that's actually defined / I don't have an example of it.
    payment_details: Any
    pricing_plan_id: int
    renewal_at: datetime
    subscription_id: int

    subscription_period: Any
    workspace_id: int


class Workspace(BaseModel):
    """Class representing the Toggl Workspace object.
    Leverages dataclass to cut down on boilerplate code.
    See: https://developers.track.toggl.com/docs/api/workspaces#200
    """

    admin: bool = Field(
        default=False,
        description="Indicates if current user is an Admin for workspace ID (unconfirmed)",
    )

    # Unclear why the server sends this back... It's sensitive so don't print it or include it in model serialization
    # When user instantiates, this could be known but should not need to be set
    api_token: Optional[SecretStr] = Field(exclude=True, repr=False)

    # Seems to be the datetime server side that request was received
    at: Optional[datetime] = Field(
        exclude=True,
        repr=False,
        default=None,
        description="When was last updated",
    )

    business_ws: bool = Field(
        default=None,
        description="Indicates if the workspace is personal or business? (unconfirmed)",
    )

    csv_upload: Optional[CSVUpload] = Field(
        default=None,
        description="TODO",
    )

    default_currency: Optional[str] = Field(
        default=None,
        description="String representation of currency for billable tasks/time entries? (unconfirmed)",
    )

    default_hourly_rate: Optional[float] = Field(
        description="TODO (unconfirmed)", default=None
    )

    ical_enabled: Optional[bool] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    ical_url: Optional[str] = Field(default=None, description="TODO (unconfirmed)")

    # Optional because we won't know
    id: Optional[int] = Field(default=None, description="TODO (unconfirmed)")

    last_modified: Optional[datetime] = Field(
        description="TODO (unconfirmed)", default=None
    )

    logo_url: Optional[str] = Field(default=None, description="TODO (unconfirmed)")

    # How far back free workspaces can access data.
    # Docs indicate that it's a thing ... I don't have it in the payloads that I'm getting back
    # Disable for now.
    # max_data_retention_days: Optional[int | None]

    name: str = Field(default=None, description="TODO (unconfirmed)")

    only_admins_may_create_projects: bool = Field(
        default=None,
        description="Indicates if users with Admin roles  (unconfirmed)",
    )

    only_admins_may_create_tags: bool = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    only_admins_see_billable_rates: bool = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    only_admins_see_team_dashboard: bool = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    organization_id: Optional[int] = Field(
        default=None,
        description="ID of the organization that owns this workspace (unconfirmed)",
    )

    premium: Optional[bool] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    profile: Optional[int] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    projects_billable_by_default: Optional[bool] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    rate_last_updated: Optional[datetime] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    reports_collapse: Optional[bool] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    role: Optional[str] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    rounding_minutes: int = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    # Should be a bool?
    rounding: int = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    server_deleted_at: Optional[datetime] = Field(
        exclude=True, default=None, description="When was deleted, null if not deleted"
    )

    subscription: Optional[Subscription] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )

    suspended_at: Optional[datetime] = Field(
        exclude=True, default=None, description="When was deleted, null if not deleted"
    )

    working_hours_in_minutes: Optional[int] = Field(
        default=None,
        description="TODO (unconfirmed)",
    )
