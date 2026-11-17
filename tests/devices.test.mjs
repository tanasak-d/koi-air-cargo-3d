// จำลองอุปกรณ์จริง (18 พ.ย. 2026): โปรเจกเตอร์ 1024×768 / 1280×720 / 1920×1080 · มือถือ 360–412
import test from 'node:test';
import assert from 'node:assert/strict';
import { readHtml } from './helpers/load.mjs';

const css = /<style>([\s\S]*?)<\/style>/.exec(readHtml())[1].replace(/\/\*[\s\S]*?\*\//g, '');
const block = q => { const i = css.indexOf(q); assert.ok(i >= 0, 'ไม่พบ ' + q); let d = 0; const j = css.indexOf('{', i); for (let k = j; k < css.length; k++) { if (css[k] === '{') d++; else if (css[k] === '}' && --d === 0) return css.slice(j, k); } };

test('โปรเจกเตอร์ 1024×768: แถบบนห้ามบังคับบรรทัดเดียว (ปุ่มล้นจอ) · บรรทัดเดียวเฉพาะจอ ≥1280', () => {
  assert.doesNotMatch(block('@media (min-width:1024px)'), /\.topbar\{flex-wrap:nowrap\}/);
  assert.match(block('@media (min-width:1280px)'), /\.topbar\{flex-wrap:nowrap\}/);
});

test('โปรเจกเตอร์ 1024–1279: ปุ่ม "ดูทั้งเส้นทาง" เหลือไอคอน แถบเล่นไม่ตกบรรทัด', () => {
  const b = block('@media (min-width:1024px) and (max-width:1279px)');
  assert.match(b, /\.stage-ctrl \.ov-btn\{[^}]*font-size:0/);
  assert.match(b, /\.stage-ctrl\{[^}]*flex-wrap:nowrap/);
});

test('ภาพ 3 มิติไม่ดันความสูงหน้า: canvas วางแบบ absolute เต็มกรอบฉาก', () => {
  assert.match(css, /#stage canvas\{[^}]*position:absolute;inset:0/);
});

test('โหมดนำเสนอบนโปรเจกเตอร์: ป้ายหัวข้อเล็ก (ใครทำ/เอกสาร/ความเสี่ยง) ไม่ต่ำกว่า .75em', () => {
  const m = /\.big-facts small\{[^}]*font-size:([\d.]+)em/.exec(css);
  assert.ok(m && +m[1] >= 0.75, m && m[1]);
});
