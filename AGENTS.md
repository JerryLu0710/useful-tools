# Repository Instructions

## Project Shape

This repository is a collection of independent Python command-line tools.
Each tool lives in its own package and has an optional dependency group in `pyproject.toml`.
Shared configuration and logging live in `config.py` and `logger_setup.py`.

## Commands

Use `uv` for all Python tooling.

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Install only the dependency group needed for a single tool when full development dependencies are unnecessary.

## Change Rules

- Keep tool-specific behavior inside its package.
- Keep command parsing in the CLI layer and reusable behavior in command or core modules.
- Return status codes from commands and call `SystemExit` only from a module entry point.
- Add or update focused tests for behavior changes.
- Do not add a dependency or abstraction without a demonstrated need.

## Documentation

Follow [the documentation standard](docs/standards/documentation.md).
Code is the source of truth for command behavior, configuration keys, defaults, and outputs.
Update the matching tool document whenever any of those change.
Read [the architecture guide](docs/architecture.md) before changing shared configuration, logging, package structure, or dependency groups.
Use [the agent workflow guide](docs/agent-workflow.md) only when task execution logging is requested.
