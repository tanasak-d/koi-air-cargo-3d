import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic']);
const L = ctx.KoiLogic;
const D = ctx.KoiData;

// เดินไปข้างหน้าจนกว่าจะหยุด (จบ/hold) หรือครบ n ครั้ง
function walk(S, n = 50) {
  for (let i = 0; i < n && L.canAdvance(S); i++) L.next(S);
  return S;
}

test('สถานการณ์ปกติ: เดินถึงขั้น 17 แล้ว mode=done end=ok', () => {
  const S = walk(L.newState(0));
  assert.equal(S.idx, 16);
  assert.equal(S.mode, 'done');
  assert.equal(S.end, 'ok');
  assert.equal(L.canAdvance(S), false);
});

test('เหตุการณ์ 1–5: เดินถึงขั้นที่กำหนดแล้วเข้า hold และกล่องถูกค้าง', () => {
  for (let id = 1; id <= 5; id++) {
    const S = walk(L.newState(id));
    assert.equal(S.mode, 'hold', 'สถานการณ์ ' + id);
    assert.equal(S.idx, D.SCENARIOS[id].step);
    assert.equal(L.heldAtCheckpoint(S), true);
  }
  assert.equal(L.heldAtCheckpoint(L.newState(0)), false);
});

test('ใน hold: next/prev/goTo ไม่ขยับ และไม่ข้ามด่าน', () => {
  const S = walk(L.newState(1));
  const at = S.idx;
  L.next(S); L.prev(S); L.goTo(S, 16);
  assert.equal(S.idx, at);
  assert.equal(S.mode, 'hold');
  for (let i = 0; i < 100; i++) L.next(S); // กดรัว ๆ
  assert.equal(S.idx, at);
});

test('ต้อง VERIFY ก่อนจึง CORRECT ได้ (HOLD → VERIFY → CORRECT)', () => {
  const S = walk(L.newState(1));
  const good = D.SCENARIOS[1].opts.findIndex(o => o.good);
  L.correct(S, good); // ยังไม่ verify -> ไม่มีผล
  assert.equal(S.mode, 'hold');
  L.verify(S);
  assert.equal(S.hp, 1);
  L.correct(S, good);
  assert.equal(S.resolved, true);
  assert.equal(S.mode, 'run');
  assert.equal(L.heldAtCheckpoint(S), false);
});

test('CORRECT ทางที่ผิด: mode=end, end=loss', () => {
  const S = walk(L.newState(1));
  const bad = D.SCENARIOS[1].opts.findIndex(o => !o.good);
  L.verify(S); L.correct(S, bad);
  assert.equal(S.mode, 'end');
  assert.equal(S.end, 'loss');
  assert.equal(L.canAdvance(S), false);
});

test('เหตุการณ์ 5 ทางถูก: จบแบบควบคุมได้ end=ctl', () => {
  const S = walk(L.newState(5));
  L.verify(S); L.correct(S, D.SCENARIOS[5].opts.findIndex(o => o.good));
  assert.equal(S.mode, 'end');
  assert.equal(S.end, 'ctl');
});

test('แก้ถูกแล้วเดินต่อจนครบ 17 ขั้นได้ทุกเหตุการณ์ (ยกเว้นที่จบด้วย ctl)', () => {
  for (let id = 1; id <= 4; id++) {
    const S = walk(L.newState(id));
    L.verify(S); L.correct(S, D.SCENARIOS[id].opts.findIndex(o => o.good));
    walk(S);
    assert.equal(S.mode, 'done', 'สถานการณ์ ' + id);
    assert.equal(S.idx, 16);
  }
});

test('next กด 100 ครั้งไม่เกินขั้น 17 และ prev ไม่ต่ำกว่าขั้น 1', () => {
  const S = L.newState(0);
  for (let i = 0; i < 100; i++) L.next(S);
  assert.equal(S.idx, 16);
  for (let i = 0; i < 100; i++) L.prev(S);
  assert.equal(S.idx, 0);
  assert.equal(S.mode, 'run');
});

test('newState รับเฉพาะ id ที่มีจริง', () => {
  assert.throws(() => L.newState(99), { name: 'RangeError' }); // เทียบด้วยชื่อ เพราะ vm คนละ realm
});

test('เวลาเลื่อน (shift) มาจากข้อมูล: เหตุการณ์ 2 เลื่อนขั้นถัดไป และอายุถุงคิดจากค่าในข้อมูล', () => {
  const S = walk(L.newState(2));
  L.verify(S); L.correct(S, D.SCENARIOS[2].opts.findIndex(o => o.good));
  const opt = D.SCENARIOS[2].opts.find(o => o.good);
  assert.equal(S.shift, opt.shift);
  assert.equal(S.shiftFrom, D.SCENARIOS[2].shiftFrom);
  assert.equal(S.seal, opt.seal);
  walk(S, 20); // ไปถึงขั้น 14 (index 13) ไม่ได้ ต้องจบที่ 16 ; ตรวจแค่สูตร
  const expect = L.openMin(S) - S.seal;
  const at13 = Object.assign({}, S, { idx: 13 });
  assert.equal(L.bagAgeMin(at13), Math.max(0, expect));
  assert.equal(L.bagStatus(at13), expect > D.CONST.BAG_LIMIT_MIN ? 'over' : 'ok');
});

test('เหตุการณ์ 4 (เอกสารไม่ตรง): แก้แล้วเวลาเลื่อนตามข้อมูล และบันทึกสถานะถุงตรงตามสูตร', () => {
  // เส้นตาย SOP 18 ชม.: เลื่อน +120 นาที -> อายุถุง 18 ชม. พอดี (ยังไม่เกิน) ยังอยู่ในเพดาน
  const S = walk(L.newState(4));
  L.verify(S); L.correct(S, D.SCENARIOS[4].opts.findIndex(o => o.good));
  const at13 = Object.assign({}, S, { idx: 13 });
  assert.equal(L.bagAgeMin(at13), D.CONST.OPEN0 + 120 - D.CONST.SEAL0);
  assert.equal(L.bagStatus(at13), 'ok');
});

// ---- Final review fix: เวลาปิดผนึกใหม่ใช้เฉพาะขั้นหลังบรรจุใหม่ ----
test('เหตุการณ์ 2 หลังแก้: ย้อนไปขั้นก่อนบรรจุใหม่ต้องใช้เวลาปิดผนึกเดิม ไม่แสดงอายุ 0 ปลอม', () => {
  const S = walk(L.newState(2));
  L.verify(S); L.correct(S, D.SCENARIOS[2].opts.findIndex(o => o.good));
  const before = L.bagAgeMin(Object.assign({}, S, { idx: 5, seal: D.CONST.SEAL0, sealFrom: 99 }));
  L.prev(S); // กลับไปขั้นก่อนหน้า (index 5)
  assert.equal(S.idx, 5);
  assert.equal(L.bagAgeMin(S), before);
  assert.ok(L.bagAgeMin(S) > 0);
});

test('เหตุการณ์ 1 หลังแก้: อายุถุงตอนอยู่ขั้นที่ติด HOLD ยังนับจากเวลาปิดผนึกเดิม', () => {
  const S = walk(L.newState(1));
  const held = L.bagAgeMin(S);
  L.verify(S); L.correct(S, D.SCENARIOS[1].opts.findIndex(o => o.good));
  assert.equal(L.bagAgeMin(S), held);
});
