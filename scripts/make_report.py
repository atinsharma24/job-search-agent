import json
import os

def main():
    json_path = 'active_application_context/proposed_batch6.json'
    with open(json_path) as f:
        data = json.load(f)

    report_path = '/Users/atinsharma/.gemini/antigravity-cli/brain/6e9ba106-d0b5-443e-9ba1-fd094cd9fd1d/proposed_batch6_report.md'
    lines = [
        "# Proposed Batch 6 Outreach List",
        "",
        "We compiled the next set of target contacts for LinkedIn referral outreach. The database has been fully deduplicated against:",
        "- All previous batch progress files (Batch 1-5, connected outreach)",
        "- `linkedin_outreach/logs/outreach.log`",
        "- `active_application_context/job_applications_tracker.md`",
        "",
        "A total of 35 unique, unprocessed targets remain across our database + 4 new profiles sourced from active application companies.",
        "",
        "| # | Name | Company | Profile URL | Note Length | Note Preview |",
        "|---|------|---------|-------------|-------------|--------------|"
    ]

    for entry in data:
        name = entry['name']
        company = entry['company']
        url = entry['url']
        note = entry['note']
        length = len(note)
        preview = note[:60] + '...' if len(note) > 60 else note
        username = url.split('/in/')[-1].split('/')[0]
        lines.append(f"| {entry['index']} | {name} | {company} | [{username}]({url}) | {length} | {preview} |")

    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))
    print("Report written successfully.")

if __name__ == '__main__':
    main()
