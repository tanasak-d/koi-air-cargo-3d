// unslop polish (18 พ.ย. 2026): 9 ข้อจากผลตรวจ V12 · ไม่แตะข้อมูล
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, L = ctx.KoiLogic;
const html = readHtml();
const css = /<style>([\s\S]*?)<\/style>/.exec(html)[1].replace(/\/\*[\s\S]*?\*\//g, '');
const uiSrc = /<script id="koi-ui">([\s\S]*?)<\/script>/.exec(html)[1];
const vals = re => [...css.matchAll(re)].map(m => m[1]);

test('1 · น้ำหนักตัวอักษรไม่เกิน 600 ทั้งไฟล์ · eyebrow ไม่ถ่างตัวอักษร', () => {
  assert.deepEqual(vals(/font-weight:(\d+)/g).filter(w => +w > 600), []);
  assert.doesNotMatch(/\.eyebrow\{[^}]*\}/.exec(css)[0], /letter-spacing/);
});

test('2 · ป้ายข้อมูล (ไม่ใช่ปุ่ม) มุม 8 ไม่ใช่แคปซูล', () => {
  assert.match(css, /\n\.chip,\.status\{[^}]*border-radius:8px/);
  assert.match(css, /\n\.pill\{[^}]*border-radius:8px/);
});

test('3 · ไม่มีสัญลักษณ์ ✓ ✕ ⚠ ▲ ● ในข้อความที่แสดง ใช้ไอคอน SVG ชุดเดียวแทน', () => {
  const code = uiSrc.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
  assert.doesNotMatch(code, /[✓✕⚠▲●]/);
  assert.match(UI.renderStatus(L.newState(0)), /#i-check[\s\S]*สถานะปกติ/);
  assert.match(css, /\.mk\{[^}]*width:1em/);
});

test('4 · ระยะ (padding/margin/gap/inset) เป็นเลขคู่ ไม่มี 3/5/7/9/11/13/15/19/25px', () => {
  const bad = [];
  for (const m of css.matchAll(/(?:^|[;{\s])((?:padding|margin|gap|row-gap|column-gap|inset|top|left|right|bottom)(?:-[a-z]+)?):([^;}]*)/g)) {
    for (const px of m[2].matchAll(/(-?\d+)px/g)) if (Math.abs(+px[1]) % 2 === 1 && Math.abs(+px[1]) !== 1) bad.push(m[1] + ':' + m[2]);
  }
  assert.deepEqual(bad, []);
});

test('5 · ขนาดตัวอักษรเป็นสเกลเดียว (rem ไม่เกิน 9 ค่า)', () => {
  const rem = new Set(vals(/font-size:([\d.]+rem)/g));
  assert.ok(rem.size <= 9, [...rem].join(' '));
  for (const v of rem) assert.ok(['.75rem', '.8125rem', '.875rem', '1rem', '1.125rem', '1.25rem', '1.5rem', '2rem'].includes(v), v);
});

test('6 · มุมโค้งอยู่ในสเกล 4/6/8/12/16/24 + แคปซูล/วงกลม', () => {
  const ok = new Set(['0', '4px', '6px', '8px', '12px', '16px', '24px', '999px', '50%']);
  const bad = [];
  for (const v of vals(/border-radius:([^;}]+)/g)) for (const p of v.trim().split(/\s+/)) if (!ok.has(p)) bad.push(v);
  assert.deepEqual(bad, []);
});

test('7 · หน้าต้อนรับ: ป้ายเหนือหัวเรื่องเป็นข้อความจาง ไม่ใช่แคปซูล', () => {
  const k = /\.welcome \.kicker\{[^}]*\}/.exec(css)[0];
  assert.doesNotMatch(k, /border-radius|border:|background:/);
});

test('8 · จอคอม: ฉากยืดเต็มความสูงที่เหลือ ไม่มีแถบว่างด้านล่าง', () => {
  assert.match(css, /#app:not\(\.present\)\{[^}]*min-height:100dvh;grid-template-rows:auto auto minmax\(0,1fr\)/);
  assert.doesNotMatch(css, /height:calc\(100dvh - 250px\)/);
});

test('9 · กระจกไม่มีเส้นขาวด้านใน (inset highlight)', () => {
  assert.doesNotMatch(css, /inset 0 1px 0 var\(--glass-edge\)/);
});
