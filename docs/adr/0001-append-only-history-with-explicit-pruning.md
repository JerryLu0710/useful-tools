# Append-only history with explicit pruning

`ytmusic_dl` records every download as one JSONL line, and `normalize-names` records a rename by appending a second line for the same video ID. That makes the history file a running log rather than a table, so a renamed track appears twice and one of its `file_path` values points at a file that no longer exists. We kept the append-only log for crash safety, and added `prune-history` as the single, explicit, atomic way to collapse it, rather than rewriting the file on every write.

## Context

The library must survive a crash or an interrupted download mid-write, which an append-only log does for free: the worst case is one truncated trailing line. The cost showed up in a real library where 1372 lines described 1348 tracks, and 24 lines named paths that did not exist. Any consumer that reads the file line by line reports those tracks as duplicates.

## Decision

History stays append-only during normal operation. The last line written for a video ID is the **current line** for that ID and every earlier one is **superseded**. All commands read history through one shared helper (`latest_history_by_id`) so they cannot disagree about which line is current. `prune-history` is the only command that replaces the file, it writes a temporary file and replaces atomically, and it refuses a file it cannot fully read.

## Alternatives considered

- Mark superseded rows in place: impossible without rewriting, which is the thing append-only avoids.
- Rewrite the history after every rename: removes the phantom lines automatically but turns every rename into a whole-file write, so a crash there loses the whole history instead of one line.
- Leave the log alone and only fix the readers: keeps the file honest for the tool but permanently wrong for anything else that reads it, including backups and ad-hoc scripts.

## Consequences

- The history file is not a reliable count of the library until it is pruned; use the current-line count.
- Any new reader must go through the shared helper. Iterating `load_history_entries` directly reintroduces the duplicate-track bug.
- `prune-history` is destructive to blank and superseded lines, so it is documented as an explicit maintenance step and offers `--dry-run`.
- `file_path` remains absolute and host-specific, so history is still not portable across machines or mount points. That is unresolved and tracked separately.
