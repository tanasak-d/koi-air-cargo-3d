import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-scene']);
const SC = ctx.KoiScene;
const D = ctx.KoiData;
const L = ctx.KoiLogic;

test('boxTarget: ทุกขั้น 0..16 มีตำแหน่งอยู่ในกรอบ [-10,10]', () => {
  for (let i = 0; i < 17; i++) {
    const p = SC.boxTarget(i);
    assert.ok(Math.abs(p.x) <= 10 && Math.abs(p.z) <= 10, 'ขั้น ' + i);
  }
});

test('boxTarget: ขั้นต่อเนื่องในสถานีเดียวกันอยู่คนละจุด', () => {
  for (let i = 0; i < 16; i++) {
    if (L.stationOf(i) !== L.stationOf(i + 1)) continue;
    const a = SC.boxTarget(i), b = SC.boxTarget(i + 1);
    assert.ok(a.x !== b.x || a.z !== b.z, 'ขั้น ' + i + ' กับ ' + (i + 1) + ' ซ้ำจุด');
  }
});

test('easeInOut: 0→0, 1→1, 0.5→0.5 และเพิ่มขึ้นเสมอ', () => {
  assert.equal(SC.easeInOut(0), 0);
  assert.equal(SC.easeInOut(1), 1);
  assert.ok(Math.abs(SC.easeInOut(0.5) - 0.5) < 1e-9);
  let prev = -1;
  for (let t = 0; t <= 1.0001; t += 0.05) {
    const v = SC.easeInOut(Math.min(t, 1));
    assert.ok(v >= prev);
    prev = v;
  }
});

test('easeInOut: ค่านอกช่วง 0..1 ถูกบีบให้อยู่ในช่วง', () => {
  assert.equal(SC.easeInOut(-5), 0);
  assert.equal(SC.easeInOut(5), 1);
});

test('lerpPose: ปลายทาง t=0 / t=1 ตรงจุด และกลางทางเป็นค่าเฉลี่ย', () => {
  const a = { x: -4, z: 2 }, b = { x: 6, z: -2 };
  assert.deepEqual(JSON.parse(JSON.stringify(SC.lerpPose(a, b, 0))), a);
  assert.deepEqual(JSON.parse(JSON.stringify(SC.lerpPose(a, b, 1))), b);
  const m = SC.lerpPose(a, b, 0.5);
  assert.equal(m.x, 1); assert.equal(m.z, 0);
});

test('blinkOn: กระพริบช้า ไม่เกิน 2 ครั้ง/วินาที (นับการเปลี่ยนค่า ≤ 4 ใน 1 วินาที)', () => {
  let changes = 0, last = SC.blinkOn(0, false);
  for (let t = 10; t <= 1000; t += 10) {
    const v = SC.blinkOn(t, false);
    if (v !== last) changes++;
    last = v;
  }
  assert.ok(changes <= 4, 'เปลี่ยน ' + changes + ' ครั้ง');
  assert.ok(changes >= 1, 'ต้องกระพริบจริง');
});

test('blinkOn: reduced-motion ค้างสถานะ "เปิด" (ไม่กระพริบ) ทุกเวลา', () => {
  for (let t = 0; t < 3000; t += 137) assert.equal(SC.blinkOn(t, true), true);
});

test('supported() ใน Node (ไม่มีเบราว์เซอร์) เป็น false และไม่ throw', () => {
  assert.equal(SC.supported(), false);
});

test('NO_WEBGL_MESSAGE ตรงข้อความที่ตกลงไว้', () => {
  assert.equal(SC.NO_WEBGL_MESSAGE, 'เครื่องนี้แสดงภาพ 3 มิติไม่ได้ ยังดูขั้นตอนได้ตามปกติ');
});

// ---- Task 8: ป้ายชื่อในฉากสถานี (ข้อมูลล้วน ทดสอบใน Node ได้) ----
test('STATION_LABELS สถานี 1–3: ป้ายมีข้อความ อยู่ในกรอบ และมีป้ายอย่างน้อยเท่าจำนวนขั้น', () => {
  for (let i = 0; i <= 2; i++) {
    const labels = SC.STATION_LABELS[i];
    assert.ok(labels && labels.length >= D.STATIONS[i].last - D.STATIONS[i].first + 1, 'สถานี ' + i);
    for (const l of labels) {
      assert.ok(typeof l.text === 'string' && l.text.length > 0);
      assert.ok(Math.abs(l.x) <= 10 && Math.abs(l.z) <= 10, l.text);
    }
  }
});

test('ทุกขั้นของสถานี 1–3 มีป้ายอยู่ใกล้จุดวางกล่อง (ห่างไม่เกิน 3 หน่วย) ให้ผู้ชมรู้ว่าอยู่ตรงไหน', () => {
  for (let step = 0; step <= 8; step++) {
    const st = L.stationOf(step), p = SC.boxTarget(step);
    const near = SC.STATION_LABELS[st].some(l => Math.hypot(l.x - p.x, l.z - p.z) <= 3);
    assert.ok(near, 'ขั้น ' + (step + 1) + ' ไม่มีป้ายใกล้จุดวาง');
  }
});

test('ป้ายสถานี 3 ระบุว่าผู้ดูแลปลานั่งในห้องโดยสาร (ไม่เข้าห้องสัมภาระ)', () => {
  const txt = SC.STATION_LABELS[2].map(l => l.text).join(' ');
  assert.match(txt, /ห้องโดยสาร/);
});

// ---- Task 9: ป้ายสถานี 4–6 ----
test('STATION_LABELS ครบทั้ง 6 สถานี และทุกขั้น 1–17 มีป้ายใกล้จุดวางกล่อง', () => {
  assert.equal(SC.STATION_LABELS.length, 6);
  for (let step = 0; step < 17; step++) {
    const st = L.stationOf(step), p = SC.boxTarget(step);
    assert.ok(SC.STATION_LABELS[st].some(l => Math.hypot(l.x - p.x, l.z - p.z) <= 3), 'ขั้น ' + (step + 1));
  }
  for (let i = 3; i <= 5; i++) {
    const labels = SC.STATION_LABELS[i];
    assert.ok(labels.length >= D.STATIONS[i].last - D.STATIONS[i].first + 1);
    for (const l of labels) assert.ok(l.text.length > 0 && Math.abs(l.x) <= 10 && Math.abs(l.z) <= 10, l.text);
  }
});

test('ป้ายสถานี 5 ใช้ถ้อยคำกักกันที่ล็อกไว้ และไม่มีจำนวนวัน', () => {
  const txt = SC.STATION_LABELS[4].map(l => l.text).join(' ');
  assert.match(txt, /จนกว่า DOF จะตรวจและอนุญาตให้ปล่อย/);
  assert.doesNotMatch(txt, /\d+\s*วัน/);
});

test('overviewTile: ตำแหน่งกระเบื้อง 6 สถานีเรียงซ้ายไปขวา ไม่ซ้อนกัน และอยู่ในกรอบ', () => {
  const xs = [0, 1, 2, 3, 4, 5].map(i => SC.overviewTile(i).x);
  for (let i = 1; i < 6; i++) assert.ok(xs[i] - xs[i - 1] >= 3.5, 'กระเบื้อง ' + i + ' ชิดเกินไป');
  assert.ok(Math.abs(xs[0]) <= 12 && Math.abs(xs[5]) <= 12);
});
