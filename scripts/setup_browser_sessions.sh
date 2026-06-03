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
python3 "$SCRIPTS/playwright_login_setup.py" \
  --portal "LinkedIn" \
  --login-url "https://www.linkedin.com/login" \
  --profile-dir "$LINKEDIN_PROFILE"
echo "[1/3] LinkedIn session saved."
echo ""

# --- Wellfound ---
echo "[2/3] Opening Wellfound login..."
echo "Log in, then close the browser window to continue."
python3 "$SCRIPTS/playwright_login_setup.py" \
  --portal "Wellfound" \
  --login-url "https://wellfound.com/login" \
  --profile-dir "$WELLFOUND_PROFILE"
echo "[2/3] Wellfound session saved."
echo ""

# --- Naukri ---
echo "[3/3] Opening Naukri login..."
echo "Log in, then close the browser window to continue."
python3 "$SCRIPTS/playwright_login_setup.py" \
  --portal "Naukri" \
  --login-url "https://www.naukri.com/nlogin/login" \
  --profile-dir "$NAUKRI_PROFILE"
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
