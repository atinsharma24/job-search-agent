#!/usr/bin/env ts-node
import fs from 'fs';
import path from 'path';
import { discover_server_categories_or_actions, execute_action } from 'functions';

// This script is a one-shot Gmail invoker that uses the connected Gmail Strata integration
// to search for trigger emails (subject configured in agent_config) and, if found, runs the
// agent_runner to prepare+review. It sends start/finish notification emails.

const ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(ROOT, 'agent', 'agent_config.json');

function loadConfig() { return JSON.parse(fs.readFileSync(CONFIG, 'utf8')); }

async function sendNotification(to: string, subject: string, body: string) {
  await execute_action({
    server_name: 'gmail',
    category_name: 'GMAIL_EMAIL',
    action_name: 'gmail_send_email',
    body_schema: JSON.stringify({ to: [to], subject, body }),
    include_output_fields: ['threadId']
  });
}

async function findTriggers(triggerSubject: string) {
  // use gmail search via execute_action
  const query = `subject:"${triggerSubject}" is:unread`;
  const res = await execute_action({
    server_name: 'gmail',
    category_name: 'GMAIL_EMAIL',
    action_name: 'gmail_search_emails',
    body_schema: JSON.stringify({ query })
  });
  return res;
}

async function main() {
  const cfg = loadConfig();
  const to = cfg.notification.notification_email;
  const subject = cfg.notification.trigger_subject || 'RUN OUTREACH';
  console.log(`Searching Gmail for unread messages with subject: "${subject}"`);
  const found = await findTriggers(subject);
  if (!found || !found.length) {
    console.log('No trigger emails found.');
    return;
  }

  console.log(`Found ${found.length} trigger message(s). Sending start notification.`);
  await sendNotification(to, 'Outreach agent starting', `Found ${found.length} trigger emails. Starting prepare+review.`);

  // run agent_runner
  const { spawnSync } = await import('child_process');
  const runner = spawnSync('ts-node', ['--esm', path.join(ROOT, 'scripts', 'agent_runner.ts')], { stdio: 'inherit' });
  if (runner.status !== 0) {
    await sendNotification(to, 'Outreach agent error', `Agent runner exited with code ${runner.status}`);
    return;
  }

  await sendNotification(to, 'Outreach agent finished', `Prepare and review completed. Check queue/approved.json and run send when ready.`);

  console.log('Invoker finished.');
}

main().catch(e => { console.error(e); process.exit(1); });
