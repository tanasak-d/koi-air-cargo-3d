// design-pipeline Stage 4: เก็บงานตาม checklist (unslop + ui-ux-pro-max)
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, L = ctx.KoiLogic;
const html = readHtml();
const css = /<style>([\s\S]*?)<\/style>/.exec(html)[1];

test('ป้าย HP ทุกที่เป็นตราประทับ: มุม 6 ขอบ 2px น้ำหนัก 600 (ทางเลือก C ข้อ 5)', () => {
  const r = /\n\.hp-tag\{([^}]*)\}/.exec(css)[1];
  assert.match(r, /border-radius:6px/);
  assert.match(r, /border:2px solid/);
  assert.match(r, /font-weight:600/);
});

test('ลิงก์ข้ามไปเนื้อหา: อยู่ต้น #app และเห็นเมื่อโฟกัส', () => {
  assert.match(html, /<div id="app">\s*<a class="skip" href="#panel">/);
  assert.match(css, /\.skip:focus\{[^}]*(top|transform)/);
});

test('ปุ่มธีมบอกสถานะ aria-pressed', () => {
  assert.match(html, /<button id="theme-btn"[^>]*aria-pressed="false"/);
  assert.match(html, /setAttribute\('aria-pressed'/);
});

test('เช็กลิสต์บอกโปรแกรมอ่านจอว่าขั้นไหนผ่านแล้ว', () => {
  const S = L.newState(0); L.goTo(S, 3);
  const h = UI.renderChecklist(S);
  assert.equal((h.match(/<span class="sr-only">ผ่านแล้ว: <\/span>/g) || []).length, 3);
});
