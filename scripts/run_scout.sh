#!/bin/bash

# --- CONFIGURATION ---
VAULT_PATH="/Users/atinsharma/job_search_vault"
# Models: gemini-3.1-flash-lite-preview (Fast/Cheap), gemini-3-flash-preview (Balanced/Reliable)
SCOUT_MODEL="gemini-3.1-flash-lite-preview"
EXEC_MODEL="gemini-3-flash-preview"

# Ensure the log directory exists
mkdir -p "$VAULT_PATH/logs/run_reports"
LOG_FILE="$VAULT_PATH/logs/run_reports/$(date +%Y-%m-%d_%H-%M-%S).log"

# Navigate to the vault
cd "$VAULT_PATH" || exit

echo "--- [1/2] Scouting Run Started: $(date) ---" >> "$LOG_FILE"
# 1. Run the main scouting and auto-apply logic
# Using Lite model for high-volume scanning to save credits
gemini-cli --model "$SCOUT_MODEL" "@job-scout Execute prompt #01 from $VAULT_PATH/prompts/job-automation-library/01_scout_and_filter.md" >> "$LOG_FILE" 2>&1

echo "--- [2/2] Summary & Sync Started: $(date) ---" >> "$LOG_FILE"
# 2. Sync the tracker and provide a summary of leads
# Using Balanced model for higher reasoning on the summary
gemini-cli --model "$EXEC_MODEL" "@job-scout Analyze the latest run and summarize my pending_review list." >> "$LOG_FILE" 2>&1

echo "--- Run Finished: $(date) ---" >> "$LOG_FILE"
echo "Scout run completed successfully. Log saved to: $LOG_FILE"
