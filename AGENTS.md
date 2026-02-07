# Repository Guidelines

## Project Structure & Module Organization

- `lib_toggl/`: core async client and API models (`client.py`, `time_entries.py`, `tags.py`, etc.).
- `tests/`: pytest suites; keep test files named `test_*.py`.
- `scripts/`: manual/dev scripts (for example `scripts/poc.py`) to exercise the API.
- `docs/adr/`: architecture decision records.
- `dist/`: build artifacts generated during packaging; do not edit manually.

## Build, Test, and Development Commands

Use `uv` for environment and dependency management.

- `uv venv --python 3.13 && source .venv/bin/activate`: create and activate local virtualenv.
- `uv sync --all-extras --dev`: install project and development dependencies from `uv.lock`.
- `uv run pytest` (or `PYTHONPATH=. uv run pytest`): run the full test suite.
- `uv run ruff check .`: run lint checks.
- `uv run ruff format .`: apply formatting.
- `pre-commit run --all-files`: run all repository hooks (YAML/JSON/Markdown checks, Ruff, etc.).
- `uv build`: build the package into `dist/`.

## Coding Style & Naming Conventions

- Python target: 3.13+, async-first code style.
- Indentation: 4 spaces for Python; 2 spaces for JSON/YAML/Markdown (`.editorconfig`).
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Prefer explicit type hints and Pydantic models for request/response structures.
- Let Ruff and pre-commit enforce style before opening a PR.

## Testing Guidelines

- Frameworks: `pytest`, `pytest-asyncio`, and `aioresponses`.
- Mark async tests with `@pytest.mark.asyncio`.
- Keep tests focused on behavior and validation (endpoint builders, model validation, client flows).
- No hard coverage gate is configured; add tests for every behavior change or bug fix.

## Commit & Pull Request Guidelines

- Use short, imperative commit subjects; prefixes like `fix`, `chore`, `ci`, and `docs` match existing history.
- Keep each commit scoped to one logical change.
- PRs should include: purpose, behavior impact, and linked issue (if applicable).
- Before requesting review, run: `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pytest`.

## Security & Configuration Tips

- Provide the Toggl API token via `TOGGL_API_KEY` (see `scripts/readme.md`).
- Never commit credentials or private keys; pre-commit includes secret-detection hooks.
- Keep local secrets in ignored files such as `.envrc`.
