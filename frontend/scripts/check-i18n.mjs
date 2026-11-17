// Verifies every language file in src/i18n has exactly the keys and {placeholders} of en.js.
// `reward` and `achv` are optional per-language overrides of API text.
import { readdirSync } from 'node:fs';

const dir = new URL('../src/i18n/', import.meta.url);
const files = readdirSync(dir).filter((f) => f.endsWith('.js'));
const load = async (f) => (await import(new URL(f, dir))).default;

const OPTIONAL = new Set(['reward', 'achv']);
const flat = (o, p = '') =>
  Object.entries(o).flatMap(([k, v]) => (OPTIONAL.has(k) && !p ? [] : v && typeof v === 'object' ? flat(v, `${p}${k}.`) : [[`${p}${k}`, v]]));
const vars = (s) => [...String(s).matchAll(/\{(\w+)\}/g)].map((m) => m[1]).sort().join(',');

const base = new Map(flat(await load('en.js')));
let problems = 0;
const report = (msg) => (problems++, console.error(msg));
for (const f of files.filter((x) => x !== 'en.js')) {
  const name = f.replace('.js', '');
  const other = new Map(flat(await load(f)));
  for (const [k, v] of base) {
    if (!other.has(k)) report(`${name}: missing ${k}`);
    else if (typeof other.get(k) !== 'string' || !other.get(k).trim()) report(`${name}: empty ${k}`);
    else if (vars(v) !== vars(other.get(k))) report(`${name}: placeholders differ in ${k}`);
  }
  for (const k of other.keys()) if (!base.has(k)) report(`${name}: extra key ${k}`);
}
console.log(problems ? `${problems} i18n problem(s)` : `i18n OK: ${base.size} keys × ${files.length} languages`);
process.exit(problems ? 1 : 0);
