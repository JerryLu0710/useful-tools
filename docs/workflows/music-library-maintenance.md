# Music library maintenance

Applies to [`ytmusic_dl`](../tools/ytmusic_dl.md).
Options, defaults and failure modes for every command are in that guide; this page only fixes the order.

## Procedure

Run the steps in this order.

### 1. Download

```bash
uv run python -m ytmusic_dl download URL [URL ...]
```

A unique title is saved as `Title.m4a`; once a second track shares that title, both files become `Title - Artist.m4a`.
See [Download](../tools/ytmusic_dl.md#download).

### 2. Unify names that download did not create

```bash
uv run python -m ytmusic_dl normalize-names -dr
uv run python -m ytmusic_dl normalize-names
```

Do this when the folder already holds files from before the naming rule, or files you copied in yourself.
The dry run lists every planned rename and names any audio file that is missing from history, which the command deliberately leaves alone.
See [Normalize Names](../tools/ytmusic_dl.md#normalize-names).

### 3. Verify files against history

```bash
uv run python -m ytmusic_dl verify -b DIRECTORY
```

Worth running after moving, restoring, or syncing the folder, because matching uses the YouTube ID embedded in the audio tags and never the filename, so it still works after step 2 renamed things.
It reports tracks whose tags carry no ID.
See [Verify](../tools/ytmusic_dl.md#verify).

### 4. Prune history

```bash
uv run python -m ytmusic_dl prune-history -dr
uv run python -m ytmusic_dl prune-history
```

This step belongs last: step 2 appends a superseding history line per rename, so until this runs the history file holds more lines than the library holds tracks.
Read the dry run before applying it, it prints each dropped line together with the path that was kept.
See [Prune History](../tools/ytmusic_dl.md#prune-history).

## Counting tracks

The line count of a history file is not the track count until step 4 has run.
Count distinct video IDs, or the current line per ID, not raw lines.
See [ADR 0001](../adr/0001-append-only-history-with-explicit-pruning.md).
