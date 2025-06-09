#!/usr/bin/env bash

set -e

BIN_DIR="$HOME/.local/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

mkdir -p "$BIN_DIR"

link_binary() {
  local relative_target_path="$1"  # subdir/actual_binary
  local link_name="$2"              # desired name in ~/.local/bin

  local target="$SCRIPT_DIR/$relative_target_path"
  local link="$BIN_DIR/$link_name"

  if [[ ! -f "$target" ]]; then
    echo -e "[${RED}FAILED${NC}] $link_name"
    return
  fi

  if [[ -L "$link" || -e "$link" ]]; then
    rm -f "$link"
  fi

  ln -s "$target" "$link"
  echo -e "[${GREEN}DONE${NC}] $link_name"
}

# Usage: link_binary <relative_path_to_binary> <symlink_name>
link_binary "py/csv2md.py" "csv2md"
link_binary "py/md2csv.py" "md2csv"
link_binary "py/textquery.py" "textquery"
link_binary "py/timestamp.py" "timestamp"
link_binary "tmpbuf/tb" "tb"


