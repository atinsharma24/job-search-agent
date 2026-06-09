import json
import re

def refine_note(name, note):
    # Fix greeting for D P Siddharth
    if name == "D P Siddharth":
        note = note.replace("Hey D ", "Hey Siddharth, ")
        note = note.replace("Hey D,", "Hey Siddharth,")

    # Match patterns like "Hey Name I work" or "Hey Name I build" or "Hey Name I am"
    # and change to "Hey Name, I work"
    first_name = name.split()[0]
    
    # Pattern: Hey Firstname [verb/pronoun]
    pattern = rf"^Hey\s+{re.escape(first_name)}\s+([a-zA-Z])"
    match = re.match(pattern, note)
    if match:
        next_char = match.group(1)
        # Check if the next word is a pronoun or verb (e.g. I, we, is, own, build)
        note = re.sub(pattern, f"Hey {first_name}, \\1", note)

    # Clean double spaces
    note = re.sub(r'\s+', ' ', note).strip()
    
    # Character limit check
    if len(note) > 300:
        note = note[:300].strip()
        last_space = note.rfind(' ')
        if last_space > 280:
            note = note[:last_space].strip()
        if not note.endswith(('.', '!', '?')):
            note += '.'
        note = note[:300].strip()
        
    return note

def main():
    json_path = 'active_application_context/proposed_batch6.json'
    with open(json_path, 'r') as f:
        data = json.load(f)

    for entry in data:
        entry['note'] = refine_note(entry['name'], entry['note'])

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print("Refined Batch 6 JSON successfully.")

if __name__ == '__main__':
    main()
