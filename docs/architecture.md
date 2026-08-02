# Architecture

Useful Tools is a monorepo of independent Python command-line utilities.

## Package boundaries

Each tool owns its CLI, tool-specific settings, core behavior, and tests.

```text
anime1_downloader/
chinese_converter/
image_tool/
ytmusic_dl/
```

Shared configuration and logging are provided by `config.py` and `logger_setup.py`.

## Dependencies

Dependencies are declared in `pyproject.toml`.
The `dev` group provides repository tooling.
Each tool has a separate group for its runtime dependencies.
Use `uv sync --group <tool>` for one tool or `uv sync --all-groups` for full development.

## CLI design

CLI modules parse arguments and translate command outcomes into exit codes.
Core and command modules should be reusable without terminating the interpreter.
Tool-specific behavior should not be placed in shared modules unless at least two tools need the same stable abstraction.

## Configuration and paths

The root `.env` file holds local configuration.
Shared project artifacts such as logs use project-root-relative paths.
Tool output locations state their own defaults and path semantics in the relevant tool guide.

## Testing and CI

Tests live in `<package>/tests/`.
CI lints the repository and installs the dependency groups required by collected tests.
Any new test that imports an optional tool dependency must update the test environment definition.
