import json
import csv
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/atinsharma/job_search_vault")
APPROVED_JSON = ROOT / "linkedin_outreach" / "queue" / "approved.json"
SENT_JSON = ROOT / "linkedin_outreach" / "queue" / "sent.json"
TRACKER_FILE = ROOT / "active_application_context" / "job_applications_tracker.md"
INPUT_CSV = ROOT / "linkedin_outreach" / "contacts" / "batch6_referral.csv"

PRIORITY_ORDER = {
    "juspay": 1,
    "decentro": 2,
    "browserstack": 3,
    "signzy": 4,
    "lambdatest": 5,
    "qure.ai": 6,
    "swiggy": 7,
    "yellow.ai": 8,
    "sarvam": 9,
    "babblebots": 10
}

def get_company_priority(company: str) -> int:
    co = company.lower()
    for key, val in PRIORITY_ORDER.items():
        if key in co:
            return val
    return 100

def get_slug(url: str) -> str:
    if not url:
        return ''
    url = url.split('?')[0].rstrip('/')
    return url.split('/')[-1].lower()

def load_already_sent_targets():
    sent_slugs = set()
    sent_names = set()

    # 1. Parse tracker markdown
    if TRACKER_FILE.exists():
        try:
            content = TRACKER_FILE.read_text(encoding='utf-8')
            for line in content.splitlines():
                if 'Referral Outreach' in line or 'Invite Sent' in line:
                    match = re.search(r'Referral Outreach \(([^)]+)\)', line)
                    if match:
                        sent_names.add(match.group(1).strip().lower())
                    urls = re.findall(r'https?://[^\s|]+', line)
                    for u in urls:
                        slug = get_slug(u)
                        if slug:
                            sent_slugs.add(slug)
        except Exception as e:
            print(f"Error reading tracker file: {e}")

    # 2. Parse progress files
    context_dir = ROOT / "active_application_context"
    if context_dir.exists():
        for p in context_dir.glob('linkedin_*progress*.json'):
            try:
                data = json.loads(p.read_text(encoding='utf-8'))
                entries = data.values() if isinstance(data, dict) else data
                for entry in entries:
                    status = entry.get('status', '').upper()
                    if status in ['SENT', 'SENT_INVITE', 'INVITE SENT', 'DRY_RUN_SUCCESS']:
                        name = entry.get('name')
                        url = entry.get('url')
                        if name:
                            sent_names.add(name.strip().lower())
                        if url:
                            slug = get_slug(url)
                            if slug:
                                sent_slugs.add(slug)
            except Exception as e:
                pass

    # 3. Parse sent.json
    if SENT_JSON.exists():
        try:
            sent_data = json.loads(SENT_JSON.read_text(encoding='utf-8'))
            for entry in sent_data:
                name = entry.get('name')
                url = entry.get('url')
                if name:
                    sent_names.add(name.strip().lower())
                if url:
                    slug = get_slug(url)
                    if slug:
                        sent_slugs.add(slug)
        except Exception as e:
            pass

    return sent_names, sent_slugs

def main():
    print("Running Queue Merger...")
    
    # 1. Load sent lists to prevent importing already-sent targets
    sent_names, sent_slugs = load_already_sent_targets()
    print(f"Sent registry contains: {len(sent_names)} names, {len(sent_slugs)} slugs")

    # 2. Load existing approved queue
    if APPROVED_JSON.exists():
        with open(APPROVED_JSON, "r", encoding="utf-8") as f:
            approved_queue = json.load(f)
    else:
        approved_queue = []

    # Map existing slugs/names in queue to prevent duplicate insertion
    queue_slugs = {get_slug(e["url"]) for e in approved_queue if "url" in e}
    queue_names = {e["name"].strip().lower() for e in approved_queue if "name" in e}

    # 3. Read prospects from CSV
    new_prospects = []
    if INPUT_CSV.exists():
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["name"]
                url = row["url"]
                company = row["company"]
                role = row["role"]
                connection_note = row["connection_note"]
                
                slug = get_slug(url)
                name_clean = name.strip().lower()

                # Check against sent lists and already in queue
                if slug in sent_slugs or name_clean in sent_names:
                    continue
                if slug in queue_slugs or name_clean in queue_names:
                    continue

                new_prospects.append({
                    "name": name,
                    "url": url,
                    "persona": "persona_3_eng_managers" if "manager" in role.lower() or "lead" in role.lower() else "persona_4_senior_engineers",
                    "company": company,
                    "message": connection_note,
                    "personalization_score": 3,
                    "status": "approved",
                    "char_count": len(connection_note),
                    "approved_at": datetime.now(timezone.utc).isoformat()
                })
    else:
        print(f"Error: {INPUT_CSV} not found!")
        sys.exit(1)

    print(f"Loaded {len(new_prospects)} new unsent prospects from CSV.")

    # 4. Sort new prospects by target company priority
    new_prospects.sort(key=lambda x: get_company_priority(x["company"]))

    # 5. Append new sorted prospects to the existing approved_queue
    original_len = len(approved_queue)
    approved_queue.extend(new_prospects)
    
    # Write updated queue back
    with open(APPROVED_JSON, "w", encoding="utf-8") as f:
        json.dump(approved_queue, f, indent=2)

    print(f"Updated {APPROVED_JSON} successfully:")
    print(f"  Existing entries: {original_len}")
    print(f"  New entries added: {len(new_prospects)}")
    print(f"  Total queue size: {len(approved_queue)}")

if __name__ == "__main__":
    main()
