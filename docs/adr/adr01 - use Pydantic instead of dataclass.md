# ADR 01: Use `pydantic` (`v1.X`) instead of `dataclasses`

**Date:** 2023-12-17
**Status:** Accepted
**Updated:** 2023-12-28

## Context

Python's stdlib [`dataclasses`](https://docs.python.org/3/library/dataclasses.html) is pretty good for simple data structures, but it's not as flexible as [`Pydantic`](https://docs.pydantic.dev/latest/) when it comes to coercing data into the correct types.

While building out types for the Toggl API, I found myself needing to do a lot of manual type coercion from strings to [`datetime`](https://docs.python.org/3/library/datetime.html) and the [`dataclasses` `__post_init__`](https://docs.python.org/3/library/dataclasses.html#dataclasses.__post_init__) method was getting pretty messy.

## Decision

Use Pydantic v1 due to [this](https://github.com/home-assistant/core/issues/99218) pending Home Assistant issue.

Essentially the use of Pydantic v2 is blocked by existing Home Assistant dependencies that are not compatible with Pydantic v2.

## Consequences

What becomes easier or more difficult to do because of this decision?

## References

* [Link to another ADR, if any]
* [Link to other reference, if any]
