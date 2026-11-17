// (। and ॥ are shared punctuation and allowed everywhere.)
// Flags strings that mix in letters from another Indic script (e.g. Malayalam letters inside Tamil text).
import { readdirSync } from 'node:fs';
const BLOCKS = { kn: [0x0c80, 0x0cff], tcy: [0x0c80, 0x0cff], hi: [0x0900, 0x097f], kok: [0x0900, 0x097f], ml: [0x0d00, 0x0d7f],
  ta: [0x0b80, 0x0bff], te: [0x0c00, 0x0c7f], bn: [0x0980, 0x09ff], as: [0x0980, 0x09ff] };
const dir = new URL('../src/i18n/', import.meta.url);
let bad = 0;
for (const f of readdirSync(dir).filter((x) => x.endsWith('.js'))) {
  const code = f.replace('.js', '');
  if (!BLOCKS[code]) continue;
  const [lo, hi] = BLOCKS[code];
  const walk = (o, p) => Object.entries(o).forEach(([k, v]) => {
    if (v && typeof v === 'object') return walk(v, `${p}${k}.`);
    const odd = [...String(v)].filter((c) => { const n = c.codePointAt(0); return n >= 0x0900 && n <= 0x0dff && n !== 0x0964 && n !== 0x0965 && (n < lo || n > hi); });
    if (odd.length) { bad++; console.error(`${code}: ${p}${k} has foreign-script letters: ${odd.join('')}  →  ${v}`); }
  });
  walk((await import(new URL(f, dir))).default, '');
}
console.log(bad ? `${bad} string(s) mix scripts` : 'scripts OK: no mixed-script strings');
process.exit(bad ? 1 : 0);
