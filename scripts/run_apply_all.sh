#!/usr/bin/env bash
# =============================================================================
# MASTER APPLY ORCHESTRATOR — LinkedIn + Cutshort + Instahyre + Naukri
# Connects to a Chrome running with CDP on port 9222.
#
# Usage:
#   bash scripts/run_apply_all.sh [--dry-run] [--background] [--max-apply N]
#                                 [--skip-preflight]
#
# Compensation, notice period and experience are read from
# core_vault/JobApplyFiles/ via scripts/vault_config.py. Nothing is hardcoded here.
#
# Exit codes:
#   0   every step succeeded
#   1   at least one step failed (other steps still ran)
#   10  CAPTCHA / security challenge — run aborted
#   12  session expired — run aborted
#   13  pre-flight failed — nothing ran
# =============================================================================

set -uo pipefail   # NOT -e: a single portal failure must not kill the whole run

VAULT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS="$VAULT_ROOT/scripts"
LOG_DIR="$VAULT_ROOT/output/logs"
mkdir -p "$LOG_DIR"

DRY_RUN=""
AUTO_CHROME="false"
AUTO_CHROME_MSG=""
SKIP_PREFLIGHT="false"
MAX_APPLY="15"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN="--dry-run"
            echo "⚠️  DRY RUN — forms are filled but NOT submitted"
            ;;
        --background|--auto-chrome)
            AUTO_CHROME="true"
            AUTO_CHROME_MSG="(background Chrome)"
            echo "🌙 BACKGROUND MODE — Chrome runs headless, no window focus stolen"
            ;;
        --skip-preflight)
            SKIP_PREFLIGHT="true"
            echo "⚠️  Pre-flight checks SKIPPED — you are flying blind"
            ;;
        --max-apply)
            shift; MAX_APPLY="${1:-15}"
            ;;
        *) ;;
    esac
    shift
done

TIMESTAMP=$(date "+%Y-%m-%d_%H-%M")
LOG_FILE="$LOG_DIR/apply_all_${TIMESTAMP}.log"
FAILED_STEPS=()

echo "============================================================"
echo "MULTI-PORTAL APPLY PIPELINE"
echo "Mode: ${DRY_RUN:-LIVE} ${AUTO_CHROME_MSG}"
echo "Max apply per portal: $MAX_APPLY"
echo "Log:  $LOG_FILE"
echo "Time: $(date)"
echo "============================================================"

# --- Chrome CDP ------------------------------------------------------------
if ! curl -s http://localhost:9222/json/version > /dev/null 2>&1; then
    if [[ "$AUTO_CHROME" == "true" ]]; then
        echo "🚀 Launching Chrome in the background (--headless=new)..."
        bash "$SCRIPTS/run_chrome_background.sh"
    else
        echo "❌ Chrome not reachable on port 9222."
        echo "   bash scripts/run_chrome_background.sh"
        echo "   or pass --background to launch it automatically."
        exit 1
    fi
fi
echo "✅ Chrome CDP connected (port 9222)"
echo ""

# --- Pre-flight ------------------------------------------------------------
# Guards against the class of defect that produced hundreds of applications
# carrying the wrong salary, 0 years of experience, and an unreadable resume.
if [[ "$SKIP_PREFLIGHT" != "true" ]]; then
    python3 "$SCRIPTS/preflight_check.py" 2>&1 | tee -a "$LOG_FILE"
    PF=${PIPESTATUS[0]}
    if [[ $PF -eq 1 ]]; then
        echo ""
        echo "🛑 Pre-flight FAILED. Nothing was submitted."
        echo "   Fix the items above, or re-run with --skip-preflight to override."
        exit 13
    fi
fi

# --- Step runner -----------------------------------------------------------
# tee would otherwise mask the python exit code, so read PIPESTATUS[0].
run_step() {
    local name="$1"; local script="$2"; shift 2
    echo "============================================================"
    echo "$name"
    echo "============================================================"
    python3 "$script" "$@" 2>&1 | tee -a "$LOG_FILE"
    local rc=${PIPESTATUS[0]}
    case $rc in
        0)  echo "✅ $name complete" ;;
        10) echo "🛑 $name: CAPTCHA / security challenge — aborting the whole run."
            echo "   Continuing would further flag this IP or profile."
            exit 10 ;;
        12) echo "🛑 $name: session expired — aborting."
            echo "   Re-run: bash scripts/setup_browser_sessions.sh"
            exit 12 ;;
        13) echo "🛑 $name: configuration error — aborting."; exit 13 ;;
        *)  echo "⚠️  $name failed (exit $rc) — continuing with remaining portals"
            FAILED_STEPS+=("$name") ;;
    esac
    echo ""
}

run_step "STEP 1: LinkedIn Discovery + Easy Apply" \
         "$SCRIPTS/playwright_linkedin_discover_apply.py" $DRY_RUN --max-apply "$MAX_APPLY"
sleep 5
run_step "STEP 2: Cutshort Applications" \
         "$SCRIPTS/playwright_cutshort_apply.py" $DRY_RUN
sleep 5
run_step "STEP 3: Instahyre Applications" \
         "$SCRIPTS/playwright_instahyre_apply.py" $DRY_RUN
sleep 5
run_step "STEP 4: Naukri Discovery + Apply" \
         "$SCRIPTS/playwright_naukri_discover_apply.py" $DRY_RUN --max-apply "$MAX_APPLY"

# --- Summary ---------------------------------------------------------------
echo "============================================================"
if [[ ${#FAILED_STEPS[@]} -eq 0 ]]; then
    echo "ALL PORTALS COMPLETE — $(date)"
else
    echo "COMPLETED WITH FAILURES — $(date)"
    printf '  ✗ %s\n' "${FAILED_STEPS[@]}"
fi
echo "Full log: $LOG_FILE"
echo "Tracker:  $VAULT_ROOT/active_application_context/job_applications_tracker.md"
echo "============================================================"

[[ ${#FAILED_STEPS[@]} -eq 0 ]] || exit 1
