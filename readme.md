# `lib-toggl`

`lib-toggl` is a Python library for interacting with the [Toggl](https://developers.track.toggl.com/docs/api) API.
It's loosely based off of [TogglPy](https://github.com/matthewdowney/TogglPy).

It's currently in a very early stage of development, and is primarily focused on the time entry endpoints.

<!-- Maintained with yzhang.markdown-all-in-one -->
- [`lib-toggl`](#lib-toggl)
  - [Using](#using)
  - [Dev](#dev)

## Using

More formal docs to be added.
For now, see the `scripts` directory for examples of how to use the library.

## Dev

I use VSCode for development so there's a `.vscode` directory with some settings that I use.
Most of the extensions and configuration directives there should be easy to port to your preferred editor / IDE as needed.

Pretty simple setup; it's all `poetry` driven...

Create a virtual environment for the project.

```shell
❯ poetry env use -- python3
Creating virtualenv togglpy in /home/karl/projects/ha-dev/TogglPy/.venv
Using virtualenv: /home/karl/projects/ha-dev/TogglPy/.venv
```

Use [autoenv](https://github.com/Tarrasch/zsh-autoenv) to automatically activate the virtual environment when you enter the project directory.

```shell
❯ cd TogglPy
Switching virtualenv: .venv [🐍Python 3.11.6]
❯ which python
/home/karl/projects/ha-dev/TogglPy/.venv/bin/python
```
