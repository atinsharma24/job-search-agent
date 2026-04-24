#!/bin/bash

set -euo pipefail

VAULT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FALLBACK_MODEL="${BROWSEROS_FALLBACK_MODEL:-gemini-3-flash-preview}"
PARSER="$VAULT_PATH/scripts/extract_llm_apply_payload.py"
LINKEDIN_RUNNER="$VAULT_PATH/scripts/playwright_linkedin_easy_apply.py"
WELLFOUND_RUNNER="$VAULT_PATH/scripts/playwright_wellfound_apply.py"
DRY_RUN_FLAG=""
POSITIONAL_ARGS=()

if [[ "${DRY_RUN:-}" =~ ^(1|true|TRUE|yes|YES)$ ]]; then
  DRY_RUN_FLAG="--dry-run"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN_FLAG="--dry-run"
      shift
      ;;
    *)
      POSITIONAL_ARGS+=("$1")
      shift
      ;;
  esac
done

PAYLOAD_FILE="${POSITIONAL_ARGS[0]:-}"
RESUME_PATH="${POSITIONAL_ARGS[1]:-}"

if [[ -z "$PAYLOAD_FILE" || -z "$RESUME_PATH" ]]; then
  echo "Usage: $0 <payload-file> <staged-resume-pdf-path>" >&2
  exit 2
fi

if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "Payload file not found: $PAYLOAD_FILE" >&2
  exit 2
fi

if [[ ! -f "$RESUME_PATH" ]]; then
  echo "Resume file not found: $RESUME_PATH" >&2
  exit 2
fi

APPLICATION_URL="$(python3 "$PARSER" --payload-file "$PAYLOAD_FILE" --field application_url)"

run_browseros_fallback() {
  gemini-cli --model "$FALLBACK_MODEL" "@job-scout BrowserOS visual fallback. Load /Users/atinsharma/job_search_vault/BROWSEROS MASTER ORCHESTRATION PROMPT: @JOB-SCOUT (OPTIMIZED V2).md. Read payload from $PAYLOAD_FILE and use staged resume $RESUME_PATH. Navigate to the application URL and complete the apply flow visually. If blocked by CAPTCHA, login wall, redirect, or unsupported ATS flow, stop and return blocked."
}

if [[ "$APPLICATION_URL" == *"linkedin.com"* ]]; then
  set +e
  python3 "$LINKEDIN_RUNNER" \
    --application-url "$APPLICATION_URL" \
    --resume-path "$RESUME_PATH" \
    ${DRY_RUN_FLAG}
  PLAYWRIGHT_EXIT=$?
  set -e

  if [[ "$PLAYWRIGHT_EXIT" -eq 0 ]]; then
    exit 0
  fi

  echo "Playwright LinkedIn fast-path failed with exit code $PLAYWRIGHT_EXIT. Falling back to BrowserOS." >&2
  run_browseros_fallback
  exit $?
fi

if [[ "$APPLICATION_URL" == *"wellfound.com"* || "$APPLICATION_URL" == *"angel.co"* ]]; then
  set +e
  python3 "$WELLFOUND_RUNNER" \
    --application-url "$APPLICATION_URL" \
    --resume-path "$RESUME_PATH" \
    ${DRY_RUN_FLAG}
  PLAYWRIGHT_EXIT=$?
  set -e

  if [[ "$PLAYWRIGHT_EXIT" -eq 0 ]]; then
    exit 0
  fi

  echo "Playwright Wellfound fast-path failed with exit code $PLAYWRIGHT_EXIT. Falling back to BrowserOS." >&2
  run_browseros_fallback
  exit $?
fi

run_browseros_fallback
