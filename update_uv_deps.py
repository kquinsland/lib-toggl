#!/usr/bin/env python
# https://gist.github.com/yhoiseth/c80c1e44a7036307e424fce616eed25e
##
# As of right now (very late 2024) there is no simple way to tell UV to update all dependencies in a project.
# You're basically stuck with rm/add for now.
# This script automates that process.
# It _should_ be obviated once this issue is resolved:
#   https://github.com/astral-sh/uv/issues/6794
##
# Run like:
#   ❯ uv run --with toml ./update_uv_deps.py
import subprocess
from re import Match, match
from typing import Any

import toml


def main() -> None:
    with open("pyproject.toml", "r") as file:
        pyproject: dict[str, Any] = toml.load(file)
    dependencies: list[str] = pyproject["project"]["dependencies"]
    package_name_pattern = r"^[a-zA-Z0-9\-]+"
    for dependency in dependencies:
        package_match = match(package_name_pattern, dependency)
        assert isinstance(package_match, Match)
        package = package_match.group(0)
        uv("remove", package)
        uv("add", package)


def uv(command: str, package: str) -> None:
    subprocess.run(["uv", command, package])


if __name__ == "__main__":
    main()
