#!/bin/bash

set -euo pipefail

VAULT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_PLIST="$VAULT_PATH/scripts/com.jobscout.pipeline.plist"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/com.jobscout.pipeline.plist"
LOG_PATH="$VAULT_PATH/logs/launchd_scout.log"

mkdir -p "$TARGET_DIR"
mkdir -p "$VAULT_PATH/logs"

python3 - "$SOURCE_PLIST" "$TARGET_PLIST" "$VAULT_PATH" "$LOG_PATH" <<'PY'
import pathlib
import plistlib
import sys

source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
vault = pathlib.Path(sys.argv[3])
log_path = sys.argv[4]

data = plistlib.loads(source.read_bytes())
data["WorkingDirectory"] = str(vault)
data["ProgramArguments"] = [
    "/bin/bash",
    "-lc",
    f"cd {vault} && {vault / 'scripts' / 'run_scout.sh'}",
]
data["StandardOutPath"] = log_path
data["StandardErrorPath"] = log_path
target.write_bytes(plistlib.dumps(data))
PY

chmod 644 "$TARGET_PLIST"
launchctl bootout "gui/$(id -u)" "$TARGET_PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$TARGET_PLIST"
echo "Installed scheduler at $TARGET_PLIST"
