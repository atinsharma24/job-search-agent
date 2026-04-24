#!/usr/bin/env ts-node
import fs from 'fs';
import path from 'path';
import { get_active_page, navigate_page, take_snapshot, click, fill, take_screenshot } from 'functions';

// NOTE: This script is a template and uses the BrowserOS functions object in runtime.
// When executed within BrowserOS, the imported functions will be available in scope.

const ROOT = path.resolve(__dirname, '..');
const APPROVED = path.join(ROOT, 'queue', 'approved.json');
const SENT = path.join(ROOT, 'queue', 'sent.json');
const LOG = path.join(ROOT, 'logs', 'outreach.log');
const ERRORS = path.join(ROOT, 'logs', 'errors.log');

function loadJSON(file: string) {
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function saveJSON(file: string, data: any) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
}

async function humanConfirm(entry: any) {
  process.stdout.write('\nREADY TO SEND:\n');
  process.stdout.write(`${entry.body_compiled}\n`);
  process.stdout.write('\nPress Y to send, any other key to skip: ');
  process.stdin.setRawMode(true);
  return new Promise<boolean>(resolve => {
    process.stdin.once('data', (data) => {
      process.stdin.setRawMode(false);
      const c = data.toString().trim().toLowerCase();
      resolve(c === 'y');
    });
  });
}

async function run() {
  const approved = loadJSON(APPROVED);
  const sent = loadJSON(SENT);
  let dailyCount = 0;
  for (const entry of approved) {
    if (entry.status !== 'approved') continue; // S1
    // DAILY LIMIT check
    const today = new Date().toISOString().slice(0,10);
    const todaysSent = sent.filter((s:any) => s.sent_at && s.sent_at.startsWith(today));
    dailyCount = todaysSent.length;
    if (dailyCount >= 15) {
      console.log('DAILY_LIMIT_REACHED — resume tomorrow.');
      return;
    }

    const ok = await humanConfirm(entry);
    if (!ok) {
      console.log('Skipped by user');
      continue;
    }

    // navigate to profile
    await navigate_page({ page: (await get_active_page()).id, url: entry.linkedin_url });
    // take a snapshot to locate buttons
    const snap = await take_snapshot({ page: (await get_active_page()).id });
    // naive button detection — attempt to find Connect or Message by visible text
    const connectEl = snap.elements.find((e:any) => /connect/i.test(e.text || ''));
    const messageEl = snap.elements.find((e:any) => /message/i.test(e.text || ''));
    if (!connectEl && !messageEl) {
      fs.appendFileSync(ERRORS, `${new Date().toISOString()} BUTTON_NOT_FOUND | ${entry.queue_id} | ${entry.linkedin_url}\n`);
      entry.status = 'failed';
      entry.error = 'BUTTON_NOT_FOUND';
      continue;
    }

    try {
      if (entry.message_type === 'linkedin_connection' && connectEl) {
        await click({ page: (await get_active_page()).id, element: connectEl.id });
        // re-snapshot and find 'Add a note'
        const snap2 = await take_snapshot({ page: (await get_active_page()).id });
        const addNote = snap2.elements.find((e:any) => /add a note/i.test(e.text || ''));
        if (!addNote) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} ADD_NOTE_NOT_FOUND | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'ADD_NOTE_NOT_FOUND';
          continue;
        }
        await click({ page: (await get_active_page()).id, element: addNote.id });
        const snap3 = await take_snapshot({ page: (await get_active_page()).id });
        const textarea = snap3.elements.find((e:any) => e.role === 'textbox' || /note/i.test(e.text || ''));
        if (!textarea) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} TEXTAREA_NOT_FOUND | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'TEXTAREA_NOT_FOUND';
          continue;
        }
        await fill({ page: (await get_active_page()).id, element: textarea.id, text: entry.body_compiled });
        // verify char count
        if ((entry.body_compiled || '').length > 300) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} CONNECTION_EXCEEDS_LIMIT | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'CONNECTION_EXCEEDS_LIMIT';
          continue;
        }
        // find Send button
        const snap4 = await take_snapshot({ page: (await get_active_page()).id });
        const sendBtn = snap4.elements.find((e:any) => /send/i.test(e.text || ''));
        if (!sendBtn) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} SEND_BUTTON_NOT_FOUND | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'SEND_BUTTON_NOT_FOUND';
          continue;
        }
        await click({ page: (await get_active_page()).id, element: sendBtn.id });
      } else {
        // message flow
        const btn = messageEl || connectEl;
        if (!btn) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} BUTTON_NOT_FOUND | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'BUTTON_NOT_FOUND';
          continue;
        }
        await click({ page: (await get_active_page()).id, element: btn.id });
        const snapMsg = await take_snapshot({ page: (await get_active_page()).id });
        const textarea = snapMsg.elements.find((e:any) => e.role === 'textbox' || /message/i.test(e.text || ''));
        if (!textarea) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} MESSAGE_TEXTAREA_NOT_FOUND | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'MESSAGE_TEXTAREA_NOT_FOUND';
          continue;
        }
        await fill({ page: (await get_active_page()).id, element: textarea.id, text: entry.body_compiled });
        if (entry.subject) {
          // try to find subject input
          const subjectEl = snapMsg.elements.find((e:any) => /subject/i.test(e.text || ''));
          if (subjectEl) await fill({ page: (await get_active_page()).id, element: subjectEl.id, text: entry.subject });
        }
        const snapSend = await take_snapshot({ page: (await get_active_page()).id });
        const sendBtn = snapSend.elements.find((e:any) => /send/i.test(e.text || ''));
        if (!sendBtn) {
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} SEND_BUTTON_NOT_FOUND | ${entry.queue_id}\n`);
          entry.status = 'failed';
          entry.error = 'SEND_BUTTON_NOT_FOUND';
          continue;
        }
        await click({ page: (await get_active_page()).id, element: sendBtn.id });
      }

      // success detection — naive wait and snapshot
      const shot = await take_screenshot({ page: (await get_active_page()).id, fullPage: false, path: path.join(ROOT, 'logs', `sent_${entry.queue_id}_${Date.now()}.png`) });
      entry.status = 'sent';
      entry.sent_at = new Date().toISOString();
      sent.push(entry);
      // remove from approved
      const idx = approved.findIndex((a:any) => a.queue_id === entry.queue_id);
      if (idx !== -1) approved.splice(idx, 1);
      fs.appendFileSync(LOG, `${new Date().toISOString()} SENT | ${entry.queue_id} | ${entry.full_name} @ ${entry.company} | ${entry.variant_id}\n`);

      // random delay 45-90s
      const delay = Math.floor(Math.random() * 45000) + 45000;
      await new Promise(r => setTimeout(r, delay));

    } catch (e:any) {
      fs.appendFileSync(ERRORS, `${new Date().toISOString()} SEND_ERROR | ${entry.queue_id} | ${e.message}\n`);
      entry.status = 'failed';
      entry.error = e.message;
      saveJSON(APPROVED, approved);
    }

    // save updated queues
    saveJSON(APPROVED, approved);
    saveJSON(SENT, sent);
  }
}

run().catch(e => { console.error(e); process.exit(1); });
