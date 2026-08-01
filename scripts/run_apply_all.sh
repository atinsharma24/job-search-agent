#!/usr/bin/env bash
# =============================================================================
# MASTER APPLY ORCHESTRATOR — LinkedIn + Cutshort + Instahyre + Naukri
# Uses CDP connection to existing Chrome session on port 9222
#
# Usage:
#   bash scripts/run_apply_all.sh [--dry-run]
#
# CTC: Current 11.2 LPA | Expected 16-22 LPA
# =============================================================================

set -euo pipefail

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$VAULT_ROOT/scripts"
LOG_DIR="$VAULT_ROOT/output/logs"
mkdir -p "$LOG_DIR"

DRY_RUN=""
AUTO_CHROME="false"

for arg in "$@"; do
    case "$arg" in
        --dry-run)
            DRY_RUN="--dry-run"
            echo "⚠️  DRY RUN MODE — Forms will be filled but NOT submitted"
            ;;
        --background|--auto-chrome)
            AUTO_CHROME="true"
            echo "🌙 BACKGROUND MODE — Chrome will run headless (--headless=new) without stealing focus"
            ;;
    esac
done

TIMESTAMP=$(date "+%Y-%m-%d_%H-%M")
LOG_FILE="$LOG_DIR/apply_all_${TIMESTAMP}.log"

echo "============================================================"
echo "MULTI-PORTAL APPLY PIPELINE"
echo "Current CTC: 11.2 LPA | Expected CTC: 16-22 LPA (negotiable)"
echo "Mode: ${DRY_RUN:-LIVE} ${AUTO_CHROME_MSG:-}"
echo "Log: $LOG_FILE"
echo "Time: $(date)"
echo "============================================================"

# Verify Chrome CDP is reachable
if ! curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
    if [[ "$AUTO_CHROME" == "true" ]]; then
        echo "🚀 Auto-launching Chrome in background (--headless=new)..."
        bash "$SCRIPTS/run_chrome_background.sh"
    else
        echo "❌ ERROR: Chrome not found on port 9222"
        echo "To run Chrome in the background without stealing macOS window focus, run:"
        echo "  bash scripts/run_chrome_background.sh"
        echo ""
        echo "Or pass --background to run_apply_all.sh to launch automatically:"
        echo "  bash scripts/run_apply_all.sh --background [--dry-run]"
        exit 1
    fi
fi
echo "✅ Chrome CDP connected (port 9222)"
echo ""

# --- STEP 1: LinkedIn Discovery + Easy Apply ---
echo "============================================================"
echo "STEP 1: LinkedIn Job Discovery + Easy Apply"
echo "============================================================"
python3 "$SCRIPTS/playwright_linkedin_discover_apply.py" $DRY_RUN --max-apply 15 2>&1 | tee -a "$LOG_FILE"
echo ""
echo "✅ LinkedIn pipeline complete"
echo ""
sleep 5

# --- STEP 2: Cutshort Apply ---
echo "============================================================"
echo "STEP 2: Cutshort Applications (5 jobs queued)"
echo "============================================================"
python3 "$SCRIPTS/playwright_cutshort_apply.py" $DRY_RUN 2>&1 | tee -a "$LOG_FILE"
echo ""
echo "✅ Cutshort pipeline complete"
echo ""
sleep 5

# --- STEP 3: Instahyre Apply ---
echo "============================================================"
echo "STEP 3: Instahyre Applications (2 jobs queued)"
echo "============================================================"
python3 "$SCRIPTS/playwright_instahyre_apply.py" $DRY_RUN 2>&1 | tee -a "$LOG_FILE"
echo ""
echo "✅ Instahyre pipeline complete"
echo ""
sleep 5

# --- STEP 4: Naukri Discovery + Apply ---
echo "============================================================"
echo "STEP 4: Naukri Job Discovery + Apply"
echo "============================================================"
python3 "$SCRIPTS/playwright_naukri_discover_apply.py" $DRY_RUN --max-apply 15 2>&1 | tee -a "$LOG_FILE"
echo ""
echo "✅ Naukri pipeline complete"
echo ""

echo "============================================================"
echo "ALL PORTALS COMPLETE — $(date)"
echo "Full log: $LOG_FILE"
echo "Tracker: $VAULT_ROOT/active_application_context/job_applications_tracker.md"
echo "============================================================"
