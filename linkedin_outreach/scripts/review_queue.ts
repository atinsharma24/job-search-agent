#!/usr/bin/env ts-node
import fs from 'fs';
import path from 'path';
import { prompt } from 'enquirer';
import os from 'os';

const ROOT = path.resolve(__dirname, '..');
const PENDING = path.join(ROOT, 'queue', 'pending.json');
const APPROVED = path.join(ROOT, 'queue', 'approved.json');
const BLACKLIST = path.join(ROOT, 'queue', 'blacklist.json');
const LOGS = path.join(ROOT, 'logs', 'outreach.log');
const ERRORS = path.join(ROOT, 'logs', 'errors.log');

function loadJSON(file: string) {
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function saveJSON(file: string, data: any) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

async function editInEditor(initial: string): Promise<string> {
  const tmp = path.join(os.tmpdir(), `outreach_edit_${Date.now()}.txt`);
  fs.writeFileSync(tmp, initial);
  const editor = process.env.EDITOR || 'nano';
  const { spawnSync } = await import('child_process');
  spawnSync(editor, [tmp], { stdio: 'inherit' });
  const updated = fs.readFileSync(tmp, 'utf8');
  fs.unlinkSync(tmp);
  return updated;
}

async function main() {
  const pending = loadJSON(PENDING);
  const approved = loadJSON(APPROVED);
  let index = 0;
  let sessionApproved = 0;
  while (index < pending.length) {
    const entry = pending[index];
    console.clear();
    console.log('════════════════════════════════════════════════════════');
    console.log(`OUTREACH REVIEW  [${index+1} of ${pending.length}]`);
    console.log('════════════════════════════════════════════════════════');
    console.log(`Contact    :  ${entry.full_name} @ ${entry.company}`);
    // persona_name isn't stored in entry; read from templates header if needed — simplified here
    console.log(`Variant    :  ${entry.variant_id}  (${entry.message_type})`);
    console.log(`LinkedIn   :  ${entry.linkedin_url}`);
    console.log(`Priority   :  ${entry.priority}`);
    console.log('────────────────────────────────────────────────────────');
    console.log('MESSAGE PREVIEW:');
    console.log('────────────────────────────────────────────────────────');
    console.log(entry.body_compiled);
    console.log('────────────────────────────────────────────────────────');
    console.log(`Char count :  ${entry.body_compiled.length}${entry.message_type==='linkedin_connection' && entry.body_compiled.length>300 ? '  ⚠ EXCEEDS 300 for connection' : ''}`);
    console.log('════════════════════════════════════════════════════════');

    const response = await prompt({
      type: 'select',
      name: 'action',
      message: 'Choose action',
      choices: ['Approve and queue for sending', 'Edit message before approving', 'Skip this contact (this session)', 'Blacklist contact (never send)', 'Exit review']
    }) as any;

    if (response.action === 'Approve and queue for sending') {
      entry.approved_at = new Date().toISOString();
      approved.push(entry);
      pending.splice(index, 1);
      fs.appendFileSync(LOGS, `${new Date().toISOString()} APPROVED | ${entry.queue_id} | ${entry.full_name} @ ${entry.company}\n`);
      sessionApproved++;
      // save state
      saveJSON(PENDING, pending);
      saveJSON(APPROVED, approved);
      continue; // do not increment index, as array has shifted
    } else if (response.action === 'Edit message before approving') {
      const updated = await editInEditor(entry.body_compiled);
      entry.body_compiled = updated;
      // re-validate length for linkedin
      if (entry.message_type === 'linkedin_connection' && entry.body_compiled.length > 300) {
        console.log('Edited message exceeds 300 chars for a connection request. Press enter to continue and edit again.');
        await prompt({ type: 'input', name: 'continue', message: 'Press Enter to continue' });
        continue; // stay on same entry
      }
      continue; // back to preview
    } else if (response.action === 'Skip this contact (this session)') {
      index++;
      continue;
    } else if (response.action === 'Blacklist contact (never send)') {
      let blacklist = [] as string[];
      if (fs.existsSync(BLACKLIST)) blacklist = JSON.parse(fs.readFileSync(BLACKLIST, 'utf8'));
      blacklist.push(entry.contact_id);
      fs.writeFileSync(BLACKLIST, JSON.stringify(blacklist, null, 2));
      fs.appendFileSync(LOGS, `${new Date().toISOString()} BLACKLISTED | ${entry.contact_id} | ${entry.full_name}\n`);
      pending.splice(index, 1);
      saveJSON(PENDING, pending);
      continue;
    } else if (response.action === 'Exit review') {
      break;
    }
  }

  console.log('\nSession summary:');
  console.log(`Approved this session: ${sessionApproved}`);
  console.log(`Remaining in pending: ${pending.length}`);
}

main().catch(e => { console.error(e); process.exit(1); });
