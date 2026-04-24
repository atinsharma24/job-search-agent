#!/usr/bin/env ts-node
import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';
import { v4 as uuidv4 } from 'uuid';
import writeFileAtomic from 'write-file-atomic';

type TargetRow = Record<string, string>;

const ROOT = path.resolve(__dirname, '..');
const CONTACTS = path.join(ROOT, 'contacts', 'targets.csv');
const TEMPLATES_DIR = path.join(ROOT, 'templates');
const PENDING = path.join(ROOT, 'queue', 'pending.json');
const ERRORS = path.join(ROOT, 'logs', 'errors.log');

function readCSV(file: string): Promise<TargetRow[]> {
  const raw = fs.readFileSync(file, 'utf8');
  const parsed = Papa.parse<TargetRow>(raw, { header: true, skipEmptyLines: true });
  if (parsed.errors.length) throw new Error('CSV parse errors: ' + JSON.stringify(parsed.errors));
  return Promise.resolve(parsed.data as TargetRow[]);
}

function readTemplate(personaId: string): string {
  const files = fs.readdirSync(TEMPLATES_DIR);
  const file = files.find(f => f.startsWith(`persona_${personaId}_`));
  if (!file) throw new Error(`Template for persona ${personaId} not found`);
  return fs.readFileSync(path.join(TEMPLATES_DIR, file), 'utf8');
}

function extractVariant(templateContent: string, variantId: string): { body: string; subject: string | null; body_raw: string; } {
  const variantHeader = `## VARIANT ${variantId}`;
  const idx = templateContent.indexOf(variantHeader);
  if (idx === -1) throw new Error(`Variant ${variantId} not found in template`);
  const slice = templateContent.slice(idx);
  // body is between the first --- after header and the next ---
  const parts = slice.split('\n---\n');
  if (parts.length < 2) throw new Error('Template parsing error');
  // parts[1] should contain body and trailing ---
  const body = parts[1].trim().replace(/^---\n|\n---$/g, '');
  // subject line exists in the header area
  const headerBlock = slice.split('\n---\n')[0];
  const subjMatch = headerBlock.match(/SUBJECT:\s*(.*)/);
  const subject = subjMatch ? subjMatch[1].trim() : null;
  return { body, subject, body_raw: body };
}

function resolvePlaceholders(body: string, row: TargetRow): { compiled: string; used: Record<string,string>; } {
  const used: Record<string,string> = {};
  let compiled = body;
  const placeholderPattern = /\[([^\]]+)\]/g;
  compiled = compiled.replace(placeholderPattern, (m, p) => {
    // map common placeholder variations to CSV columns
    const key = p.trim();
    const mapping: Record<string,string> = {
      'Company': 'placeholder_company',
      'Company Name': 'placeholder_company',
      'Specific Feature/News': 'placeholder_feature_or_news',
      'Specific Feature/Product': 'placeholder_feature_or_news',
      'Specific Reason': 'placeholder_specific_reason',
      'their answer': 'placeholder_technical_thing',
      'Name': 'full_name',
      'their answer': 'placeholder_specific_reason'
    };
    const col = mapping[key] || Object.keys(row).find(k => k.toLowerCase().includes(key.toLowerCase())) || null;
    const val = col ? (row[col] || '') : '';
    used[`[${key}]`] = val;
    return val || `[${key}]`;
  });
  return { compiled, used };
}

async function main() {
  const rows = await readCSV(CONTACTS);
  const processed: number = rows.length;
  let queued = 0;
  let skipped = 0;
  const skippedReasons: string[] = [];

  let pending: any[] = [];
  try {
    if (fs.existsSync(PENDING)) {
      pending = JSON.parse(fs.readFileSync(PENDING, 'utf8'));
    }
  } catch (e) {
    // ignore, start fresh
    pending = [];
  }

  for (const row of rows) {
    if ((row.status || '').toLowerCase() !== 'pending') continue;
    try {
      const personaId = row.persona_id;
      const variantId = row.variant_id;
      const templateContent = readTemplate(personaId);
      const variant = extractVariant(templateContent, variantId);
      const { compiled, used } = resolvePlaceholders(variant.body_raw, row);
      // validation
      if (variant.body_raw.includes('LinkedIn Connection') || variantId.endsWith('A')) {
        // approximate check for connection types
        if (compiled.length > 300) {
          skipped++;
          skippedReasons.push(`${row.full_name}: CONNECTION_EXCEEDS_LIMIT`);
          fs.appendFileSync(ERRORS, `${new Date().toISOString()} UNRESOLVED: CONNECTION_EXCEEDS_LIMIT for ${row.full_name}\n`);
          continue;
        }
      }
      if (compiled.includes('[')) {
        skipped++;
        skippedReasons.push(`${row.full_name}: UNRESOLVED_PLACEHOLDER`);
        fs.appendFileSync(ERRORS, `${new Date().toISOString()} UNRESOLVED_PLACEHOLDER for ${row.full_name}\n`);
        continue;
      }
      const entry = {
        queue_id: uuidv4(),
        contact_id: row.contact_id,
        full_name: row.full_name,
        company: row.company,
        linkedin_url: row.linkedin_url,
        persona_id: Number(row.persona_id),
        variant_id: row.variant_id,
        message_type: variant.subject ? 'cold_email' : 'linkedin_connection',
        subject: variant.subject || null,
        body_raw: variant.body_raw,
        body_compiled: compiled,
        placeholders_used: used,
        status: 'pending',
        priority: (row.priority as any) || 'MEDIUM',
        created_at: new Date().toISOString(),
        approved_at: null,
        sent_at: null,
        error: null
      };
      pending.push(entry);
      queued++;
    } catch (e:any) {
      skipped++;
      skippedReasons.push(`${row.full_name}: ERROR_${e.message}`);
      fs.appendFileSync(ERRORS, `${new Date().toISOString()} ERROR for ${row.full_name}: ${e.message}\n`);
    }
  }

  // write pending atomically
  writeFileAtomic.sync(PENDING, JSON.stringify(pending, null, 2));

  console.log(`Processed: ${processed} rows`);
  console.log(`Queued:    ${queued} entries`);
  console.log(`Skipped:   ${skipped} (${skippedReasons.join('; ')})`);
}

main().catch(e => { console.error(e); process.exit(1); });
