#!/usr/bin/env python3
"""
Dump tag name/id pairs to a file for reference
"""
import asyncio
import logging
import os
import sys
import json

from lib_toggl.client import Toggl

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


async def main():
    """Does the needful"""
    _key = os.getenv("TOGGL_API_KEY")
    async with Toggl(_key) as api:
        w = await api.get_workspaces()
        if not w:
            log.error("No workspaces")
            sys.exit(1)

        workspace_id = w[0].id
        if workspace_id is None:
            log.error("No workspace id found")
            sys.exit(1)

        log.info("Using workspace id %s", workspace_id)
        tags = await api.get_tags(workspace_id)
        tag_map = {tag.name: tag.id for tag in tags}
        with open("tag_map.json", "w", encoding="utf8") as json_file:
            # Pretty print
            json.dump(tag_map, json_file, indent=4, sort_keys=True)

    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
