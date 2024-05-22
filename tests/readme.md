# Pytest import errors

I do not know why `pytest` seems to have issues with `PYTHONPATH`.
Simple way to fix after activating the `venv` is to run the following command:

```bash
❯ python3 -m pytest tests/
Alias tip: py -m pytest tests/
===================================================================================================== test session starts =====================================================================================================
platform linux -- Python 3.11.8, pytest-7.4.4, pluggy-1.5.0
rootdir: /home/karl/Projects/ha-toggl/lib-toggl
plugins: asyncio-0.23.7
asyncio: mode=Mode.STRICT
collected 5 items
<...>
```

There might be a [better way to fix this](https://stackoverflow.com/a/50610630/1521764)
