#!/bin/bash

set -euo pipefail

VAULT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARSER="$VAULT_PATH/scripts/extract_llm_apply_payload.py"
LINKEDIN_RUNNER="$VAULT_PATH/scripts/playwright_linkedin_easy_apply.py"
WELLFOUND_RUNNER="$VAULT_PATH/scripts/playwright_wellfound_apply.py"
NAUKRI_RUNNER="$VAULT_PATH/scripts/playwright_naukri_apply.py"
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

# Claude CLI visual fallback — invoked when Playwright fast-path fails.
run_claude_fallback() {
  local url="$1"
  local reason="${2:-Playwright fast-path failed}"

  echo "[$reason] Falling back to Claude visual apply for: $url" >&2

  # Build the fallback prompt as a heredoc.
  FALLBACK_PROMPT=$(cat <<PROMPT
You are completing a job application on behalf of Atin Sharma.
Vault: $VAULT_PATH

Task:
1. Read $PAYLOAD_FILE for job details (company, job_title, application_url).
2. Read $VAULT_PATH/core_vault/01_atomic_fact_sheet.json for all candidate data.
3. Read $VAULT_PATH/core_vault/06_logistics_mapping.json for logistics answers.
4. Navigate to: $url
5. Fill every visible form field using ONLY values from the two vault files above.
   - Salary fields: use 15 LPA (min) or 15–18 LPA range. Current CTC = 0.
   - Notice period: 0 days / Immediate Joiner.
   - For open-ended text questions, read $VAULT_PATH/core_vault/02_situational_qa_library.md and use the 100-word answer that best fits the question.
6. Upload resume: $RESUME_PATH
7. Take a screenshot of the completely filled form BEFORE submitting.
8. If any field cannot be answered from the vault files, STOP and report which field is missing.
9. Submit only after all fields are filled from vault data.
10. Report: applied / blocked / error with reason.

Safety: Never invent data. Never enter a salary outside 15–18 LPA. Never claim experience beyond what is in the fact sheet.
PROMPT
)

  if command -v claude &>/dev/null; then
    claude --print "$FALLBACK_PROMPT"
  else
    echo "claude CLI not found. Manual apply required." >&2
    echo ""
    echo "=== PASTE THIS PROMPT TO CLAUDE DESKTOP ==="
    echo "$FALLBACK_PROMPT"
    echo "==========================================="
    exit 1
  fi
}

# --- LinkedIn ---
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

  echo "Playwright LinkedIn failed (exit $PLAYWRIGHT_EXIT)." >&2
  run_claude_fallback "$APPLICATION_URL" "LinkedIn Playwright exit $PLAYWRIGHT_EXIT"
  exit $?
fi

# --- Wellfound ---
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

  echo "Playwright Wellfound failed (exit $PLAYWRIGHT_EXIT)." >&2
  run_claude_fallback "$APPLICATION_URL" "Wellfound Playwright exit $PLAYWRIGHT_EXIT"
  exit $?
fi

# --- Naukri ---
if [[ "$APPLICATION_URL" == *"naukri.com"* ]]; then
  set +e
  python3 "$NAUKRI_RUNNER" \
    --application-url "$APPLICATION_URL" \
    --resume-path "$RESUME_PATH" \
    ${DRY_RUN_FLAG}
  PLAYWRIGHT_EXIT=$?
  set -e

  if [[ "$PLAYWRIGHT_EXIT" -eq 0 ]]; then
    exit 0
  fi

  echo "Playwright Naukri failed (exit $PLAYWRIGHT_EXIT)." >&2
  run_claude_fallback "$APPLICATION_URL" "Naukri Playwright exit $PLAYWRIGHT_EXIT"
  exit $?
fi

# --- Everything else: direct Claude visual apply ---
run_claude_fallback "$APPLICATION_URL" "No Playwright script for this domain"
exit $?
