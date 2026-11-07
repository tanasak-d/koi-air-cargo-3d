import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic']);
const L = ctx.KoiLogic;
const D = ctx.KoiData;

// state เปล่า ๆ สำหรับทดสอบเวลา (ของจริงสร้างจาก newState ใน Task 4)
const S0 = (over) => Object.assign({ idx: 0, seal: 60, shift: 0, shiftFrom: 99 }, over);   // ปิดถุง 01:00 JST

test('stationOf แปลงขั้น (เริ่ม 0) เป็นสถานี (เริ่ม 0) ตามที่ล็อกไว้', () => {
  const want = { 0: 0, 5: 0, 6: 1, 7: 1, 8: 2, 9: 3, 10: 4, 13: 4, 14: 5, 16: 5 };
  for (const [step, st] of Object.entries(want)) assert.equal(L.stationOf(+step), st, 'ขั้น ' + step);
});

test('fmtTime: JST / ICT และข้ามวัน', () => {
  assert.equal(L.fmtTime(1105, 'JST'), '18:25');
  assert.equal(L.fmtTime(1105, 'ICT'), '16:25');
  assert.equal(L.fmtTime(1500, 'JST'), '01:00 (+1 วัน)');
  assert.equal(L.fmtTime(60, 'ICT'), '23:00 (−1 วัน)'); // 01:00 JST = 23:00 ICT ของวันก่อน
  assert.equal(L.fmtTime(1380, 'ICT'), '21:00'); // ไม่ข้ามวัน
});

test('เที่ยวบิน NN393 ออก 07:00 JST ถึง 12:00 ICT ตรงกับข้อมูล', () => {
  const s = D.STEPS[8];
  assert.equal(L.fmtTime(s.dep, 'JST'), D.CONST.FLIGHT.depJST);
  assert.equal(L.fmtTime(s.t[1], 'ICT'), D.CONST.FLIGHT.arrICT);
});

test('stepTimeLabel: ขั้นมีเวลา / ขั้นประมาณการ / ขั้นไม่มีเวลา', () => {
  assert.equal(L.stepTimeLabel(5, S0()), '01:00–03:00 JST · 23:00 (−1 วัน)–01:00 ICT');
  assert.match(L.stepTimeLabel(10, S0()), /^โดยประมาณ /); // ขั้น 11 approx
  assert.match(L.stepTimeLabel(0, S0()), /โดยประมาณ/); // ขั้น 1 ไม่มีเวลา
});

test('stepTimeLabel: เวลาเลื่อน (shift) เมื่อ index >= shiftFrom', () => {
  const S = S0({ shift: 120, shiftFrom: 9 });
  assert.equal(L.stepTimeLabel(8, S), '07:00–14:00 JST · 05:00–12:00 ICT'); // ก่อน shiftFrom ไม่เลื่อน
  assert.equal(L.stepTimeLabel(9, S), '16:00–16:50 JST · 14:00–14:50 ICT');
});

test('bagAgeMin: null ก่อนปิดผนึก, ไม่ติดลบ, นับจากเวลาปิดผนึก', () => {
  assert.equal(L.bagAgeMin(S0({ idx: 2 })), null);
  assert.equal(L.bagAgeMin(S0({ idx: 3 })), 0);
  assert.equal(L.bagAgeMin(S0({ idx: 8 })), 780); // ลงจอด 14:00 JST (12:00 ICT) = 840 - 60
  assert.equal(L.bagAgeMin(S0({ idx: 3, seal: 300 })), 0); // ปิดผนึกใหม่หลังเวลาจบขั้น -> ไม่ติดลบ
});

test('bagStatus: ไม่เกินเส้นตาย 18 ชม. (1080 นาที) = ok, เกิน = over', () => {
  assert.equal(L.bagStatus(S0({ idx: 13 })), 'ok'); // เปิดถุง 1020 - 60 = 960 (16 ชม.)
  assert.equal(L.bagAgeMin(S0({ idx: 13 })), 960);
  assert.equal(L.bagStatus(S0({ idx: 13, shift: 120, shiftFrom: 0 })), 'ok'); // 1080 พอดี
  assert.equal(L.bagStatus(S0({ idx: 13, shift: 121, shiftFrom: 0 })), 'over'); // 1081
  assert.equal(L.bagStatus(S0({ idx: 1 })), 'ok'); // ยังไม่ปิดผนึก ไม่ถือว่าเกิน
});
