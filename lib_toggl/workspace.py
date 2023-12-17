"""Various type/class definitions for the Workspaces bit of the Toggle API
Parse/Coercion done by Pydantic
"""
from datetime import datetime
from typing import Any, Optional

import structlog
from pydantic import BaseModel, SecretStr

from .const import BASE

log = structlog.get_logger(__name__)

ENDPOINT = f"{BASE}/workspaces"


class CSVUpload(BaseModel):
    """_summary_"""

    at: datetime
    log_id: int


class Subscription(BaseModel):
    """_summary_"""

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

    admin: bool
    api_token: SecretStr
    at: datetime
    business_ws: bool
    csv_upload: CSVUpload
    default_currency: str
    default_hourly_rate: Optional[float]
    ical_enabled: bool
    ical_url: str
    id: int
    last_modified: datetime
    logo_url: str
    # How far back free workspaces can access data.
    # max_data_retention_days: Optional[int | None]
    name: str
    only_admins_may_create_projects: bool
    only_admins_may_create_tags: bool
    only_admins_see_billable_rates: bool
    only_admins_see_team_dashboard: bool
    organization_id: int
    premium: bool
    profile: int
    projects_billable_by_default: bool
    rate_last_updated: Optional[datetime]
    reports_collapse: bool
    role: str
    rounding_minutes: int
    rounding: int
    server_deleted_at: Optional[datetime]
    subscription: Optional[Subscription]
    suspended_at: Optional[datetime]
    working_hours_in_minutes: Optional[int]
