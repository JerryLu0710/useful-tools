# Convert a document for the first time

This walk-through takes a file of simplified Chinese, produces a traditional version, and explains
what happened to your files afterwards.
It needs no network and no sample data: you will create the input yourself.

When you are done you will have converted one file and one directory, and you will know which files
the tool is allowed to touch.

## Install the tool

From the project root:

```bash
uv sync --group chinese_converter
uv run python -m chinese_converter --help
```

The second command prints the option list. If it fails with "No module named opencc", the
dependency group did not install.

## Convert one file

Create something to convert:

```bash
mkdir -p temp/hands-on
printf '简单中文测试：网络与机器。\n' > temp/hands-on/notes.txt
```

Run the tool on it with no output path:

```bash
uv run python -m chinese_converter temp/hands-on/notes.txt
```

You get three files where there was one:

```text
temp/hands-on/notes.txt           the original, unchanged
temp/hands-on/notes.txt.backup    a copy of the original, made before anything was written
temp/hands-on/notes_trad.txt      the converted text
```

The output name is always built from the input name plus `_trad`, in the same directory, unless you
name the output yourself.

Check the result:

```bash
cat temp/hands-on/notes_trad.txt
```

The last two lines of the run tell you whether anything went wrong:

```text
✓ Conversion completed in 0.00s
  Files: 1, Texts: 1, Errors: 0
```

## Convert the other way

Traditional to simplified takes one more option:

```bash
uv run python -m chinese_converter temp/hands-on/notes_trad.txt --type t2s
```

The output is `notes_trad_trad.txt`. The `_trad` in the name comes from how the output path is
generated, not from the direction of the conversion, so name the output explicitly when the
direction matters:

```bash
uv run python -m chinese_converter temp/hands-on/notes_trad.txt temp/hands-on/notes_simp.txt --type t2s
```

Put the output path immediately after the input, before any option. An option between the two
positionals makes the command fail with `unrecognized arguments` and exit status `2`, because the
argument parser cannot tell that the trailing path belongs to the command.

## Convert a whole directory

Batch mode takes an input directory and an output directory:

```bash
uv run python -m chinese_converter temp/hands-on temp/hands-on-out --batch
```

Batch names files differently from single-file mode: each converted file keeps its original name
inside the output directory, so `temp/hands-on-out/notes.txt` is the converted text, not
`notes_trad.txt`. Only `*.epub` and `*.txt` in that directory are picked up; subdirectories are not
searched.

If you leave the output directory out, batch mode writes to a sibling named after the input
directory with `_trad` appended.

## See what a failure looks like

Both of these fail:

```bash
uv run python -m chinese_converter temp/hands-on/notes.txt.pdf
uv run python -m chinese_converter temp/hands-on/missing.txt
```

Each reports `Conversion failed`, writes no output, creates no backup, and exits with status `1`.
The first fails on extension only: the tool decides what it can read from the filename, never from
the contents.

## Where to go next

- [Chinese Converter guide](../tools/chinese_converter.md) for every option and conversion profile.
- [Configuration reference](../configuration.md) for `BACKUP_SUFFIX` and `EPUB_DEFAULT_CONVERSION`.
