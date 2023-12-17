#!/usr/bin/env python3
"""
Super simple PoC for playing with the API Client
"""

import os

import structlog

from lib_toggl import client

log = structlog.get_logger(__name__)


def main():
    """Does the needful"""

    api = client.Toggl()
    api.api_key = os.getenv("TOGGL_API_KEY")
    w = api.get_workspaces()
    log.info("workspaces", count=len(w), workspaces=w)

    o = api.get_organizations()
    log.info("get_organizations", count=len(o), orgs=o)


if __name__ == "__main__":
    main()
