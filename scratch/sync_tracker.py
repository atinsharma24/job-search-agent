import json
import re
from pathlib import Path
from datetime import datetime

TRACKER_PATH = Path("/Users/atinsharma/job_search_vault/active_application_context/job_applications_tracker.md")
SENT_PATH = Path("/Users/atinsharma/job_search_vault/linkedin_outreach/queue/sent.json")

def main():
    if not TRACKER_PATH.exists() or not SENT_PATH.exists():
        print("Required files do not exist.")
        return

    # Read current tracker content
    tracker_content = TRACKER_PATH.read_text(encoding="utf-8")
    
    # Parse existing names
    existing_names = set()
    for line in tracker_content.splitlines():
        if "Referral Outreach (" in line:
            parts = line.split("Referral Outreach (", 1)
            if len(parts) > 1:
                name_part = parts[1]
                if ") |" in name_part:
                    name = name_part.split(") |", 1)[0].strip()
                    existing_names.add(name.lower())

    print(f"Loaded {len(existing_names)} existing names from tracker.")

    # Read sent.json
    with open(SENT_PATH) as f:
        sent_data = json.load(f)

    new_lines = []
    for entry in sent_data:
        if entry.get("status") != "sent":
            continue
            
        name = entry.get("name", "").strip()
        if not name:
            continue
            
        if name.lower() in existing_names:
            continue
            
        company = entry.get("company", "").strip()
        sent_at_str = entry.get("sent_at")
        
        # Parse date
        date_str = "2026-06-09"
        if sent_at_str:
            try:
                dt = datetime.fromisoformat(sent_at_str.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except Exception:
                pass
                
        # Format the markdown line
        line = f"- [{date_str}] **Company:** {company} | **Role:** Referral Outreach ({name}) | **Status:** Invite Sent | **Note:** SENT (Outreach Batch 6)"
        new_lines.append(line)
        existing_names.add(name.lower())

    if new_lines:
        print(f"Adding {len(new_lines)} new entries to tracker...")
        # Add new lines to the tracker content before the trailing empty lines
        lines = tracker_content.splitlines()
        # Find where to append. We want to append at the end of the list.
        # Let's just append at the end of the file, keeping formatting neat.
        while lines and not lines[-1].strip():
            lines.pop()
        
        for nl in new_lines:
            lines.append(nl)
            
        lines.append("") # trailing empty line
        TRACKER_PATH.write_text("\n".join(lines), encoding="utf-8")
        print("Tracker successfully updated.")
    else:
        print("No new entries to add.")

if __name__ == "__main__":
    main()
