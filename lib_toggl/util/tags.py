"""Utility functions for working with tags."""

import logging
from typing import List

from lib_toggl.time_entries import TimeEntry
from lib_toggl.client import Toggl

log = logging.getLogger(__name__)


async def update_tags(client: Toggl, te: TimeEntry, new_tags: List[str]) -> None:
    """
    A wrapper to abstract the logic of updating the tags on a TimeEntry object.

    The Toggl API docs are a bit confusing and ambiguous about how tags are handled when updating a Time Entry.
    As it turns out, the "just give us the string, we'll do the rest" behavior applies only when creating a new Time Entry.

    If you have an existing Time Entry and want to update the tags, you must provide the tag IDs, not the tag strings.

    Furthermore, if you clear and then set the `tag_ids` field on a Time Entry and POST/PUT it to the server, you'd expect
        the time entry to have just the new tags, right? Wrong.
    The tags on the Time Entry will depend on what the `tag_action` was set to when the POST/PUT request was made with
        the tag_ids.

    So instead, we offer a nice simple interface to the user: just give us the list of strings you want the Time Entry to have.
    This means that we need to figure out which tags are new and which already exist in the workspace
    New tags need to be created and then we can get the tag IDs.

    Then we need to figure out which tag_ids should be added and or removed from the Time Entry.

    """
    log.debug("Updating tags on TimeEntry: %s", te.description)
    # TODO: much better error handling
    known_tags = await client.get_tags(te.workspace_id)
    known_tags = {tag.name: tag.id for tag in known_tags}
    log.debug("Found %s known tags: %s", len(known_tags), known_tags)

    # Figure out what tags need to be created, added and removed
    tags_to_create = set(new_tags) - set(known_tags.keys())
    log.debug("%s Tags to create: %s", len(tags_to_create), tags_to_create)

    tags_to_add = set(new_tags) - set(te.tags)
    log.debug("%s Tags to add: %s", len(tags_to_add), tags_to_add)

    tags_to_remove = set(te.tags) - set(new_tags)
    log.debug("%s Tags to remove: %s", len(tags_to_remove), tags_to_remove)
