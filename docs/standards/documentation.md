# Documentation Standard

## Scope and naming

Root-level documentation is limited to repository-discovery files: `README.md`, `AGENTS.md`, and `LICENSE`.
Maintained reference material belongs in `docs/`.
Use lowercase file names.
Use a tool's Python package name for its guide, such as `docs/tools/ytmusic_dl.md`.
Use one canonical document for each topic.

## Progressive disclosure

`README.md` explains what the repository provides and gives the shortest correct path to use it.
`docs/setup.md` covers installation, environment configuration, and troubleshooting.
`docs/architecture.md` describes package boundaries and shared conventions.
`docs/tools/` contains one operational guide per tool.
`docs/decisions/` records durable architectural decisions.

## Source of truth

Code is authoritative for commands, arguments, defaults, configuration keys, output names, and failure behavior.
Documentation must be updated in the same change as any behavior it describes.
Do not document planned features as current behavior.

## Tool-guide requirements

Each tool guide must include its dependency group, configuration keys with real defaults, command usage, every user-facing option, representative examples, output behavior, and relevant failure modes.

## Decisions

Create an architecture decision record only when a decision has durable consequences across tools or commits.
Use the filename format `NNNN-short-title.md`.
Record context, decision, alternatives, and consequences.
