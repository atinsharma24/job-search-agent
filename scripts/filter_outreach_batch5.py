import json
from pathlib import Path
from datetime import datetime

def main():
    vault_root = Path("/Users/atinsharma/job_search_vault")
    active_dir = vault_root / "active_application_context"
    
    # 1. Load profiles from proposed_batch5.json
    profiles_path = active_dir / "proposed_batch5.json"
    profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    
    # 2. Load current progress from linkedin_outreach_progress_batch5.json
    progress_path = active_dir / "linkedin_outreach_progress_batch5.json"
    progress = {}
    if progress_path.exists():
        try:
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
        except:
            pass
            
    # List of indices to skip as low signal (1-indexed based on batch 5)
    low_signal_indices = [22, 23, 26, 28, 29, 30, 31, 32, 35, 36, 38, 39, 40, 41]
    
    print("Applying low-signal filter updates...")
    for p in profiles:
        idx = p["index"]
        if idx in low_signal_indices:
            # Check if not already processed in progress
            if str(idx) not in progress or progress[str(idx)]["status"] in ["FAILED", "Unknown"]:
                progress[str(idx)] = {
                    "name": p["name"],
                    "company": p["company"],
                    "url": p["url"],
                    "status": "SKIPPED_LOW_SIGNAL",
                    "note": "None",
                    "timestamp": datetime.now().isoformat()
                }
                print(f"Filtered out: [{idx}] {p['name']} ({p['company']})")
                
    # Save the updated progress
    progress_path.write_text(json.dumps(progress, indent=2), encoding="utf-8")
    print(f"Updated progress log saved. Total entries now: {len(progress)}/50")

if __name__ == "__main__":
    main()
