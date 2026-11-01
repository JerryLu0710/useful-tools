# Documentation Standard

## Scope and naming

Root-level documentation is limited to repository-discovery files: `README.md`, `AGENTS.md`, and `LICENSE`.
Maintained reference material belongs in `docs/`.
Use lowercase file names.
Use a tool's Python package name for its guide, such as `docs/tools/ytmusic_dl.md`.
Use one canonical document for each topic.

## Progressive disclosure

`README.md` explains what the repository provides and gives the shortest correct path to use it.
`docs/setup.md` covers installing the project and troubleshooting it.
`docs/configuration.md` lists every shared setting and its default.
`docs/workflows/` holds one file per procedure that chains a tool's commands against real data, and links to the tool guides for options instead of repeating them.
Add a workflow only once it has actually been run; an unexercised procedure is not documented.
`docs/architecture.md` describes package boundaries, shared conventions, and why they are chosen.
`docs/tools/` contains one operational guide per tool.
`docs/tutorials/` holds walk-throughs that teach a first task end to end; add one where a new user would actually stall, not one per tool.
`docs/adr/` records durable architectural decisions.

## One mode per document

A document either tells the reader how to do something, describes the machinery, or explains why it is the way it is.
Keep those apart: a reader who arrives for a setup step should not have to read a tooling rationale, and a reader who arrives for a setting's default should not have to follow numbered steps.
Split the material when a document serves two of those needs, and link between them.

## Source of truth

Code is authoritative for commands, arguments, defaults, configuration keys, output names, and failure behavior.
Documentation must be updated in the same change as any behavior it describes.
Do not document planned features as current behavior.

## Tutorials

A tutorial leads a reader through one complete task, in order, ending with a result they can verify.
It uses a synthetic input the reader creates, so the walk-through needs no sample data and no network access.
Every command and every quoted output comes from a real run.
It does not list every option; it links to the tool guide for that.

## Tool-guide requirements

Each tool guide must include its dependency group, configuration keys with real defaults, command usage, every user-facing option, representative examples, output behavior, and relevant failure modes.

## Decisions

Create an architecture decision record only when a decision has durable consequences across tools or commits.
Use the filename format `NNNN-short-title.md`.
Record context, decision, alternatives, and consequences.
