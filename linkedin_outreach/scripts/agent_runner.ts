#!/usr/bin/env ts-node
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';

const ROOT = path.resolve(__dirname, '..');
const CONFIG = path.join(ROOT, 'agent', 'agent_config.json');

function loadConfig() {
  return JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
}

function runScript(name: string, cmd: string) {
  console.log(`Running ${name}: ${cmd}`);
  const parts = cmd.split(' ');
  const res = spawnSync(parts[0], parts.slice(1), { stdio: 'inherit' });
  if (res.status !== 0) throw new Error(`${name} failed with code ${res.status}`);
}

async function main() {
  const cfg = loadConfig();
  // prepare
  runScript('prepare', cfg.run_commands.prepare);
  // review (human-in-the-loop)
  console.log('Starting review. Please complete the interactive review session.');
  runScript('review', cfg.run_commands.review);
  console.log('Review complete. Approved queue entries are in queue/approved.json');
  console.log('Send step is not automatic. Run `npm run send` when you want to execute sends (each message requires manual Y confirmation).');
}

main().catch(e => { console.error(e); process.exit(1); });
