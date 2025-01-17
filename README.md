# `lib-toggl`

`lib-toggl` is a Python library for interacting with the [Toggl](https://developers.track.toggl.com/docs/api) API.
It exists because I figured it'd be easier to start fresh instead of update [TogglPy](https://github.com/matthewdowney/TogglPy) to use the new `v9` API and the other changes needed for better Home Assistant integration.

> [!NOTE]
> `lib-toggl` is currently in a very early stage of development and is meant primarily for use in with [`ha-toggl-track`](https://github.com/kquinsland/ha-toggl-track).
> There are other, better Python based API clients for toggl track.
> You should probably use one of those instead.

**Seriously, the number of `#TODO:` comments in this code is ridiculous.**

As this library is mostly meant for use with Home Assistant, it's written to be compatible with Python 3.11+ and is mostly `async` based with strong-ish typing.
It is _absolutely_ not meant to be a complete implementation of the Toggl API; it does just enough for[`ha-toggl-track`](https://github.com/kquinsland/ha-toggl-track) and that's about it.

- [`lib-toggl`](#lib-toggl)
  - [Using](#using)
  - [Dev](#dev)
    - [pre-commit](#pre-commit)
    - [`doctoc`](#doctoc)
  - [TODO](#todo)

## Using

More formal docs [to be added](#todo).
Tests are also needed!

For now, see the `scripts` directory for a quick example of how to use the library.

## Dev

I use VSCode for development so there's a [`.vscode`](./.vscode) directory with some settings that I use.
Most of the extensions and configuration directives there should be easy to port to your preferred editor / IDE as needed.

Pretty simple setup; it's all [`uv`](https://github.com/astral-sh/uv) driven...

Create a virtual environment for the project.

```shell
❯ uv venv --python 3.13
Using CPython 3.13.0 interpreter at: /opt/homebrew/opt/python@3.13/bin/python3.13
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
❯ source .venv/bin/activate
```

Use [autoenv](https://github.com/Tarrasch/zsh-autoenv) to automatically activate the virtual environment when you enter the project directory.

```shell
❯ cd TogglPy
Switching virtualenv: .venv [🐍Python 3.11.6]
❯ which python
/home/karl/projects/ha-dev/TogglPy/.venv/bin/python
```

Don't forget to [install `pre-commit` hooks.](https://pre-commit.com/)

### pre-commit

Assuming you've [installed the `pre-commit` tool](https://pre-commit.com/#install), just run the following to install the git hooks:

```shell
❯ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

### `doctoc`

The table of contents in `readme.md` is updated with [`doctoc`](https://github.com/thlorenz/doctoc)

```shell
❯ docker run --rm -v "$(pwd)":/app peterdavehello/npm-doctoc doctoc /app/README.md
<...>
```

## TODO

- [ ] pre-commit hooks
- [ ] Tests
- [ ] CI/CD/GHA automation for testing and pypi release
- [ ] Devcontainers (for VSCode) so the dev environment is more portable / easier to set up
