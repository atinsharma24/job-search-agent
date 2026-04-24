#!/bin/bash

set -euo pipefail

VAULT_PATH="/Users/atinsharma/job_search_vault"
SCOUT_MODEL="gemini-3.1-flash-lite-preview"
APPLY_MACRO_PATH="$VAULT_PATH/scripts/browseros_apply_macro.sh"
PAYLOAD_EXTRACTOR="$VAULT_PATH/scripts/extract_llm_apply_payload.py"
DISCOVERY_FEEDER="$VAULT_PATH/scripts/job_discovery_feeder.py"
NOTIFY_SCRIPT="$VAULT_PATH/scripts/notify_user.sh"
DRY_RUN_FLAG=""

if [[ "${DRY_RUN:-}" == "1" ]]; then
  DRY_RUN_FLAG="--dry-run"
fi

mkdir -p "$VAULT_PATH/logs/run_reports"
LOG_FILE="$VAULT_PATH/logs/run_reports/$(date +%Y-%m-%d_%H-%M-%S).log"

cd "$VAULT_PATH" || exit

echo "--- [1/2] Discovery Run Started: $(date) ---" >> "$LOG_FILE"

RAW_OUTPUT_FILE="$(mktemp)"
PAYLOAD_FILE="$(mktemp)"
DISCOVERY_FILE="$(mktemp)"

cleanup() {
  rm -f "$RAW_OUTPUT_FILE" "$PAYLOAD_FILE" "$DISCOVERY_FILE"
}

trap cleanup EXIT

if ! python3 "$DISCOVERY_FEEDER" --output-file "$DISCOVERY_FILE" ${DRY_RUN_FLAG} >> "$LOG_FILE" 2>&1; then
  echo "--- Discovery Failed: $(date) ---" >> "$LOG_FILE"
  exit 1
fi

DISCOVERY_PACKET="$(cat "$DISCOVERY_FILE")"

if [[ "$DISCOVERY_PACKET" == "[]" || -z "$DISCOVERY_PACKET" ]]; then
  echo "No new jobs discovered. Exiting cleanly." >> "$LOG_FILE"
  echo "--- Run Finished: $(date) ---" >> "$LOG_FILE"
  exit 0
fi

read -r -d '' SCOUT_PROMPT <<EOF || true
@job-scout Use this pre-extracted discovery packet as the only active input:
$DISCOVERY_PACKET

Execute prompt #01 from $VAULT_PATH/prompts/job-automation-library/01_scout_and_filter.md.
Do not perform portal discovery in this step. Evaluate only the supplied packet and return one flat JSON object.
EOF

echo "--- [2/2] Fast-Path Scout Run Started: $(date) ---" >> "$LOG_FILE"

if ! gemini-cli --model "$SCOUT_MODEL" "$SCOUT_PROMPT" > "$RAW_OUTPUT_FILE" 2>&1; then
  cat "$RAW_OUTPUT_FILE" >> "$LOG_FILE"
  echo "--- Run Failed: $(date) ---" >> "$LOG_FILE"
  exit 1
fi

cat "$RAW_OUTPUT_FILE" >> "$LOG_FILE"
if ! python3 "$PAYLOAD_EXTRACTOR" \
  --source-file "$RAW_OUTPUT_FILE" \
  --output-file "$PAYLOAD_FILE" >> "$LOG_FILE" 2>&1; then
  echo "No JSON payload found in scout output." >> "$LOG_FILE"
  echo "--- Run Failed: $(date) ---" >> "$LOG_FILE"
  exit 1
fi

ACTION="$(python3 "$PAYLOAD_EXTRACTOR" --payload-file "$PAYLOAD_FILE" --field action)"

if [[ "$ACTION" == "apply" ]]; then
  echo "--- I/O Handler Started: $(date) ---" >> "$LOG_FILE"
  if ! python3 "$VAULT_PATH/scripts/apply_io_handler.py" --payload-file "$PAYLOAD_FILE" >> "$LOG_FILE" 2>&1; then
    echo "--- I/O Handler Failed: $(date) ---" >> "$LOG_FILE"
    exit 1
  fi

  if [[ -x "$APPLY_MACRO_PATH" ]]; then
    echo "--- BrowserOS Apply Macro Started: $(date) ---" >> "$LOG_FILE"
    if ! "$APPLY_MACRO_PATH" ${DRY_RUN_FLAG} "$PAYLOAD_FILE" "$VAULT_PATH/active_application_context/staged_application_resume.pdf" >> "$LOG_FILE" 2>&1; then
      echo "--- BrowserOS Apply Macro Failed: $(date) ---" >> "$LOG_FILE"
      exit 1
    fi

    COMPANY="$(python3 "$PAYLOAD_EXTRACTOR" --payload-file "$PAYLOAD_FILE" --field company)"
    ROLE="$(python3 "$PAYLOAD_EXTRACTOR" --payload-file "$PAYLOAD_FILE" --field job_title)"
    if [[ -x "$NOTIFY_SCRIPT" ]]; then
      "$NOTIFY_SCRIPT" "$ROLE" "$COMPANY" >> "$LOG_FILE" 2>&1 || true
    fi
  else
    echo "BrowserOS apply macro not configured at $APPLY_MACRO_PATH." >> "$LOG_FILE"
  fi
else
  echo "Scout action was '$ACTION'; apply macro not executed." >> "$LOG_FILE"
fi

echo "--- Run Finished: $(date) ---" >> "$LOG_FILE"
echo "Scout run completed successfully. Log saved to: $LOG_FILE"
