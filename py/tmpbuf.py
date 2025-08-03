#!/usr/bin/env python3
import os
import sys
import subprocess
import re
import argparse
import string
from pathlib import Path
from bench.data import DataTable, MdFormat, TermColor

# Check environment variable
tb = os.environ.get("tb")
if not tb:
    print(TermColor.colorize(f'Env var "tb" is not set', 'red'))
    sys.exit(1)

tb_path = Path(tb)
tb_path.mkdir(parents=True, exist_ok=True)

STANDARD_FILES = list(string.ascii_lowercase + string.digits)

def get_stats(fname, preview_len = 50):
    """
    Returns a tuple (num_lines, num_chars, preview) for the given file.
    - If the file doesn't exist or is empty, returns (0, 0, "").
    - The preview is a collapsed version of the file contents with at most L characters.
    """
    path = Path(os.path.join(tb_path, fname))
    if not path.is_file() or path.stat().st_size == 0:
        return (0, 0, "")

    try:
        with path.open('r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            num_lines = len(lines)
            num_chars = sum(len(line) for line in lines)

            combined = ' '.join(line.strip() for line in lines)
            collapsed = re.sub(r'\s+', ' ', combined).strip()

            if len(collapsed) <= preview_len:
                preview = collapsed
            else:
                preview = collapsed[:preview_len-2] + '..'

        return (num_lines, num_chars, preview)
    except Exception:
        return (0, 0, "")

def tb_stats():
    table = DataTable(4, ['Buffer', 'Lines', 'Chars', 'Preview'])
    for fname in STANDARD_FILES:
        table.add_row([fname, *get_stats(fname)])
    print(*MdFormat(table).format(['cyan', 'red', 'yellow', 'white']), sep='\n')

def tb_regen():
    regenerated = [f for f in STANDARD_FILES if not (tb_path / f).exists()]
    for f in regenerated:
        (tb_path / f).touch()
    msg = "Regenerated files: " + ' '.join(regenerated) if regenerated else "All standard buffer files already exist."
    print(msg)

def tb_first_empty():
    for fname in STANDARD_FILES:
        if get_stats(fname)[0] == 0:
            return os.path.join(tb_path, fname)
    return None

def tb_non_empty():
    used = [fname for fname in STANDARD_FILES if get_stats(fname)[0] > 0]
    if used:
        open_editor(used)
    else:
        print("No non-empty buffers to open.")
        sys.exit(1)

def open_editor(files, cd_to_base=True):
    """
    Open the given list of file paths in the user's preferred editor.

    Args:
        files (list of str or Path): List of file paths to open.
        cd_to_base (bool): If True, issue a '+cd {tb_path}' command to the editor.
    """
    if not files:
        print("No files to open.")
        sys.exit(1)

    editor = os.environ.get("EDITOR")
    cmd = [editor]
    if cd_to_base:
        cmd.append(f"+cd {str(tb_path)}")
    cmd += [os.path.join(tb_path, f) for f in files]
    os.execvp(editor, cmd)

def main():
    parser = argparse.ArgumentParser(
        description="Buffer manager utility.",
        usage="tb [-l|--list] [-i|--init] [-e|--empty] [-u|--used] [a-z0-9]"
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--list", action="store_true", help="Show buffer list with stats")
    group.add_argument("-i", "--init", action="store_true", help="Initialize missing buffers")
    group.add_argument("-e", "--empty", action="store_true", help="Return path to first empty buffer")
    group.add_argument("-u", "--used", action="store_true", help="Open all used buffers")
    group.add_argument("file", nargs="?", help="Open or create buffer file a-z or 0-9")

    args = parser.parse_args()

    if args.list:
        tb_stats()
    elif args.init:
        tb_regen()
    elif args.empty:
        e = tb_first_empty()
        if e:
            print(e)
        else:
            sys.exit(1)
    elif args.used:
        tb_non_empty()
    elif args.file is None:
        e = tb_first_empty()
        if e:
            open_editor([e])
        else:
            sys.exit(1)
    elif args.file in STANDARD_FILES:
        open_editor(args.file)
    else:
        print(f"Unknown option or file: {args.file}")
        parser.print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
