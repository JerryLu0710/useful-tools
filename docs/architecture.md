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

Groups are PEP 735 dependency groups rather than optional dependencies, so a tool's heavy or
platform-specific requirements stay out of the way of the other three.
`uv run` is used instead of activating a virtual environment by hand because it resolves the
environment from `uv.lock` before executing: the environment a command runs in comes from the
lock file, not from whatever shell state happens to be active.

## CLI design

CLI modules parse arguments and translate command outcomes into exit codes.
Core and command modules should be reusable without terminating the interpreter.
Tool-specific behavior should not be placed in shared modules unless at least two tools need the same stable abstraction.

## Logging

Every tool logs through `logger_setup.get_logger`, which attaches a stdout handler and a rotating
file handler to a per-tool logger, so each tool writes its own log file under `LOG_DIRECTORY`.
The two handlers are deliberately asymmetric: the file handler accepts everything from `DEBUG` up
and carries module, line and function detail, while the console handler is filtered to `LOG_LEVEL`
and uses a shorter format. Detailed history therefore reaches disk whether or not the console
shows it.

A tool's own log-level option sets the level of the logger, which sits in front of both handlers,
so it can only remove output. Console detail is governed by `LOG_LEVEL`.

## Configuration and paths

The root `.env` file holds local configuration and is read once, when `config.py` is imported.
Keys and defaults are in [the configuration reference](configuration.md).
Tool output locations state their own defaults and path semantics in the relevant tool guide.
Some configured output directories sit on a synced or shared volume.
A tool that keeps a history file puts it inside that same directory, so the file travels with the media and can be written from more than one device.
Maintain such a history from one device at a time: a sync conflict in a history file costs more to untangle than an untidy one.

## Testing and CI

Tests live in `<package>/tests/`.
CI lints the repository and installs the dependency groups required by collected tests.
Any new test that imports an optional tool dependency must update the test environment definition.
