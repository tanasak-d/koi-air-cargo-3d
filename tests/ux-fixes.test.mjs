// ปรับ UX ตามรายงานตรวจ docs/ux-ui-audit-2026-11-06.md โดยใช้ข้อมูลรายงาน 10 หัวข้อ
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, L = ctx.KoiLogic, D = ctx.KoiData;
const css = /<style>([\s\S]*?)<\/style>/.exec(readHtml())[1];
const walk = (S, n = 50) => { for (let i = 0; i < n && L.canAdvance(S); i++) L.next(S); return S; };

test('ข้อ 1: ปุ่มตัดสินใจตอน HOLD อยู่ในแถบติดล่างของแผง (sticky) ไม่เลื่อนหาย', () => {
  const S = walk(L.newState(1));
  assert.match(UI.renderHold(S), /<div class="hold-act">[\s\S]*?data-act="verify"/);
  L.verify(S);
  assert.match(UI.renderHold(S), /<div class="hold-act">[\s\S]*?data-opt="0"/);
  // ปุ่มอยู่ก่อนรายละเอียด (สาเหตุ/ผลกระทบ/ตัวควบคุม) ผู้ชมเห็นทันทีโดยไม่ต้องเลื่อน แม้จอ 360×640
  const h = UI.renderHold(walk(L.newState(1)));
  assert.ok(h.indexOf('class="hold-act"') < h.indexOf('สาเหตุที่เป็นไปได้'), 'ปุ่มต้องมาก่อนรายละเอียด');
});
test('ข้อ 2: เหตุการณ์ถุงรั่ว ระหว่าง HOLD ป้ายถุงบอก "⚠ ต้องตรวจถุง" ไม่ใช่ "ปลอดภัย"', () => {
  const S = walk(L.newState(1));
  const h = UI.renderFacts(S) + UI.renderSheetHead(S, false);
  assert.match(h, /i-alert"\/><\/svg> ต้องตรวจถุง/);
  assert.doesNotMatch(h, /ปลอดภัย/);
});
test('ข้อ 2: เหตุการณ์อื่นตอน HOLD (เอกสารไม่ตรง) ป้ายถุงยังบอกเวลาตามปกติ', () => {
  const S = walk(L.newState(4));
  assert.match(UI.renderFacts(S), /ปลอดภัย · เหลือ/);
});
test('ข้อ 3: หลังเปิดถุง (ขั้น 14 เป็นต้นไป) บอก "เปิดถุงแล้ว" และเวลาในถุงรวม ไม่บอก "เหลือ"', () => {
  const S = L.newState(0); L.goTo(S, 13);
  const h = UI.renderFacts(S);
  assert.match(h, /i-check"\/><\/svg> เปิดถุงแล้ว · อยู่ในถุงรวม 16\.0 ชม\./);
  assert.doesNotMatch(h, /เหลือ/);
  const at13 = L.newState(0); L.goTo(at13, 12);
  assert.match(UI.renderFacts(at13), /เหลือ 2\.0 ชม\./);   // ขั้น 13 ยังนับถอยหลังถึงเปิดถุง
});
test('ข้อ 6: จอสัมผัสไม่แสดงคำแนะนำคีย์บอร์ดบนหน้าต้อนรับ', () => {
  assert.match(css, /@media \(hover:none\)\{[^}]*\.w-keys\{display:none\}/);
});
