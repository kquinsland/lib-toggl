#!/usr/bin/env python3
"""
Super simple PoC for playing with the API Client
"""
import asyncio
import logging
import os
import sys
from datetime import datetime
from time import sleep

from lib_toggl.client import Toggl
from lib_toggl.time_entries import TimeEntry

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


async def main():
    """Does the needful"""
    _key = os.getenv("TOGGL_API_KEY")
    async with Toggl(_key) as api:
        # Start with getting account information.
        # This does two things: 1) confirms API key is valid, 2) gets user ID
        ##
        # Can also do get_account_details()
        me = await api.account
        log.info("account details are:", extra={"account": me})

        log.info("Fetching workspaces")
        w = await api.get_workspaces()
        log.info("Got workspace!", extra={"count": len(w), "workspaces": w})

        # I am not a premium user, so I only have one workspace.
        if len(w) > 1:
            log.warning("More than one workspace found, using first one")

        workspace_id = w[0].id
        log.info("Using workspace id %s", workspace_id)

        log.info("Fetching Current Time Entry")
        te = await api.current_time_entry
        if te is None:
            log.info("No current time entry")
        else:
            log.info("get_current_time_entry", extra={"entry": te})

        log.info("Creating a new Time Entry")

        body = {
            "description": "Testing from poc.py!",
            "tags": ["test-tag"],
            "workspace_id": workspace_id,
        }

        new_time_entry = TimeEntry(**body)
        log.debug(f"new_time_entry: {new_time_entry}")
        created_te = await api.create_new_time_entry(new_time_entry)
        log.info(f"created_te: {created_te}")

        log.info("Sleeping before stopping time entry")
        sleep(10)
        result = await api.stop_time_entry(created_te)
        log.info("stop_time_entry", extra={"result": result})

        log.info("Fetching time entries")
        _now = datetime.now()
        _today = datetime(_now.year, _now.month, _now.day)
        te = await api.get_time_entries(start_date=_today, end_date=_now)
        log.info("get_time_entries", extra={"count": len(te), "entries": te})

    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
