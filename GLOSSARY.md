# useful-tools

A collection of independent command-line tools. Each tool owns its own behaviour; only
configuration and logging are shared.

## Language

### ytmusic_dl history

**Current line**:
The last line written for a video ID in the JSONL history file; it carries the track's current
output path and is the only line that describes the track.
_Avoid_: latest entry, active record, live row

**Superseded line**:
An earlier line for a video ID that a rename replaced. It names an output path that no longer
exists and must never be counted as a second track.
_Avoid_: duplicate, orphan row, stale entry
