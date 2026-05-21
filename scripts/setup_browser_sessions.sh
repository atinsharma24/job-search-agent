#!/bin/bash

# One-time browser session setup.
# Run this ONCE per portal to log in and save the session.
# After this, all Playwright scripts run headless and stay authenticated.

set -euo pipefail

VAULT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$VAULT_PATH/scripts"

LINKEDIN_PROFILE="$VAULT_PATH/active_application_context/playwright/linkedin-profile"
WELLFOUND_PROFILE="$VAULT_PATH/active_application_context/playwright/wellfound-profile"
NAUKRI_PROFILE="$VAULT_PATH/active_application_context/playwright/naukri-profile"

mkdir -p "$LINKEDIN_PROFILE" "$WELLFOUND_PROFILE" "$NAUKRI_PROFILE"

echo ""
echo "=== Browser Session Setup ==="
echo "This script opens a headed browser for each portal."
echo "Log in manually in the browser that opens, then CLOSE the browser window."
echo "Your session will be saved automatically."
echo ""

# --- LinkedIn ---
echo "[1/3] Opening LinkedIn login..."
echo "Log in, then close the browser window to continue."
LINKEDIN_PLAYWRIGHT_HEADLESS=0 \
LINKEDIN_PLAYWRIGHT_PROFILE_DIR="$LINKEDIN_PROFILE" \
  python3 "$SCRIPTS/playwright_linkedin_easy_apply.py" \
    --application-url "https://www.linkedin.com/login" \
    --resume-path "$VAULT_PATH/resumes_and_docs/categories/pdf/AI_Integrated_FullStack.pdf" \
    --dry-run 2>/dev/null || true
echo "[1/3] LinkedIn session saved."
echo ""

# --- Wellfound ---
echo "[2/3] Opening Wellfound login..."
echo "Log in, then close the browser window to continue."
WELLFOUND_PLAYWRIGHT_HEADLESS=0 \
WELLFOUND_PLAYWRIGHT_PROFILE_DIR="$WELLFOUND_PROFILE" \
  python3 "$SCRIPTS/playwright_wellfound_apply.py" \
    --application-url "https://wellfound.com/login" \
    --resume-path "$VAULT_PATH/resumes_and_docs/categories/pdf/AI_Integrated_FullStack.pdf" \
    --dry-run 2>/dev/null || true
echo "[2/3] Wellfound session saved."
echo ""

# --- Naukri ---
echo "[3/3] Opening Naukri login..."
echo "Log in, then close the browser window to continue."
NAUKRI_PLAYWRIGHT_HEADLESS=0 \
NAUKRI_PLAYWRIGHT_PROFILE_DIR="$NAUKRI_PROFILE" \
  python3 "$SCRIPTS/playwright_naukri_apply.py" \
    --application-url "https://www.naukri.com/nlogin/login" \
    --resume-path "$VAULT_PATH/resumes_and_docs/categories/pdf/AI_Integrated_FullStack.pdf" \
    --dry-run 2>/dev/null || true
echo "[3/3] Naukri session saved."
echo ""

echo "=== Setup complete. All sessions are saved. ==="
echo "Profile directories:"
echo "  LinkedIn : $LINKEDIN_PROFILE"
echo "  Wellfound: $WELLFOUND_PROFILE"
echo "  Naukri   : $NAUKRI_PROFILE"
echo ""
echo "Next step: Run the full pipeline with:"
echo "  Read /Users/atinsharma/job_search_vault/INVOKE.md and execute it."
