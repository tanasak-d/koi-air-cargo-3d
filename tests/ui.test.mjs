import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

function fresh() {
  const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
  return { UI: ctx.KoiUI, L: ctx.KoiLogic, D: ctx.KoiData };
}
const { UI, L, D } = fresh();
const walk = (S, n = 50) => { for (let i = 0; i < n && L.canAdvance(S); i++) L.next(S); return S; };
const count = (s, re) => (s.match(re) || []).length;

test('renderStrip: 6 ปุ่มสถานี และสถานีปัจจุบันมี aria-current="step"', () => {
  const S = L.newState(0);
  const h = UI.renderStrip(S);
  assert.equal(count(h, /data-station="/g), 6);
  assert.equal(count(h, /aria-current="step"/g), 1);
  assert.match(h, /ผู้ส่ง/);
  // เดินไปสถานี NRT (ขั้น 7 = index 6)
  L.goTo(S, 6);
  const h2 = UI.renderStrip(S);
  assert.match(h2, /data-station="1"[^>]*aria-current="step"/);
  assert.match(h2, /data-station="0"[^>]*class="pill passed"/);
});

test('renderStepList: แสดงเฉพาะขั้นของสถานีปัจจุบัน ขั้นที่ผ่านมีเครื่องหมาย ✓', () => {
  const S = L.newState(0);
  L.goTo(S, 2);
  const h = UI.renderStepList(S);
  assert.equal(count(h, /data-step="/g), 6); // สถานี 1 มี 6 ขั้น
  assert.equal(count(h, /✓/g), 2);            // ผ่านขั้น 1,2
  assert.equal(count(h, /aria-current="step"/g), 1);
});

test('renderHold: ใน hold มีคำ HOLD, ✕ และปุ่ม VERIFY; ไม่พึ่งสีอย่างเดียว', () => {
  const S = walk(L.newState(1));
  const h = UI.renderHold(S);
  assert.match(h, /HOLD/);
  assert.match(h, /✕/);
  assert.match(h, /data-act="verify"/);
  assert.match(h, new RegExp(D.SCENARIOS[1].cause.slice(0, 10)));
  assert.doesNotMatch(h, /data-opt=/); // ยังไม่ VERIFY ยังเลือกวิธีแก้ไม่ได้
});

test('renderHold: หลัง VERIFY แสดงตัวเลือกวิธีแก้ (CORRECT) ครบทุกข้อ', () => {
  const S = walk(L.newState(1));
  L.verify(S);
  const h = UI.renderHold(S);
  assert.equal(count(h, /data-opt="/g), D.SCENARIOS[1].opts.length);
});

test('renderHold: ไม่ hold ก็ไม่แสดงอะไร', () => {
  assert.equal(UI.renderHold(L.newState(0)), '');
});

test('renderEnd: กรณีสูญเสีย มีข้อความสรุปและ ✕, กรณีปกติมี ✓', () => {
  const S = walk(L.newState(1));
  L.verify(S); L.correct(S, D.SCENARIOS[1].opts.findIndex(o => !o.good));
  const h = UI.renderEnd(S);
  assert.match(h, /✕/);
  assert.match(h, /สูญเสีย/);
  const ok = walk(L.newState(0));
  assert.match(UI.renderEnd(ok), /✓/);
  assert.equal(UI.renderEnd(L.newState(0)), '');
});

test('renderTab: ความเสี่ยงของขั้นปัจจุบัน, ใคร/ทำอะไร, เอกสาร, 4-Flow', () => {
  const S = L.newState(0); L.goTo(S, 3); // ขั้น 4 บรรจุถุง
  assert.match(UI.renderTab('risk', S), /ถุงรั่ว/);
  assert.match(UI.renderTab('who', S), /ฟาร์มผู้ขาย/);
  assert.match(UI.renderTab('what', S), /1:2/);
  assert.match(UI.renderTab('docs', S), /Packing list/);
  const flow = UI.renderTab('flow', S);
  assert.equal(count(flow, /data-lane="/g), 4);
});

test('renderTab flow: เลนที่มีปัญหาแสดง ✕ ไม่ใช่สีอย่างเดียว', () => {
  const S = walk(L.newState(1));
  const flow = UI.renderTab('flow', S);
  assert.match(flow, /✕/);
  assert.match(flow, /✓/);
});

test('ข้อมูลที่มี HTML ถูก escape', () => {
  const f = fresh();
  f.D.STEPS[0].name = '<script>alert(1)</script>';
  const S = f.L.newState(0);
  const h = f.UI.renderStepList(S) + f.UI.renderTab('what', S) + f.UI.renderStrip(S);
  assert.doesNotMatch(h, /<script>alert/);
  assert.match(h, /&lt;script&gt;/);
});

test('renderTimeBadge: ขั้นประมาณการมีคำ "โดยประมาณ" และแสดงอายุถุงหลังปิดผนึก', () => {
  const S = L.newState(0); L.goTo(S, 10); // ขั้น 11 approx
  assert.match(UI.renderTimeBadge(S), /โดยประมาณ/);
  assert.match(UI.renderTimeBadge(S), /21/);
  const early = L.newState(0);
  assert.doesNotMatch(UI.renderTimeBadge(early), /อายุถุง/); // ยังไม่ปิดผนึก
});

test('renderTimeBadge: ถุงเกิน 21 ชม. แสดง ✕ พร้อมข้อความ', () => {
  const S = walk(L.newState(4));
  L.verify(S); L.correct(S, D.SCENARIOS[4].opts.findIndex(o => o.good));
  walk(S); // จบที่ขั้น 17 (index 16)
  assert.equal(L.bagStatus(S), 'over');
  const h = UI.renderTimeBadge(S);
  assert.match(h, /✕/);
  assert.match(h, /เกิน/);
});

test('renderGlossary: ห่อศัพท์ครั้งแรกด้วย abbr, ครั้งที่สองไม่ห่อ, และ escape ข้อความ', () => {
  const h = UI.renderGlossary('NOTOC คือ <b>ใบแจ้ง</b> NOTOC');
  assert.equal(count(h, /<abbr /g), 1);
  assert.match(h, /title="[^"]+"/);
  assert.doesNotMatch(h, /<b>/);
  assert.match(h, /&lt;b&gt;/);
  assert.equal(UI.renderGlossary('สวัสดี'), 'สวัสดี');
});

test('renderControls: ปุ่มถัดไปปิดเมื่อค้าง hold และมีเหตุการณ์ให้เลือกครบ 6 แบบ', () => {
  const S = walk(L.newState(1));
  const h = UI.renderControls(S, false);
  assert.match(h, /data-act="next"[^>]*disabled/);
  assert.equal(count(h, /data-sc="/g), 6);
  assert.doesNotMatch(UI.renderControls(L.newState(0), false), /data-act="next"[^>]*disabled/);
});

test('บอกสถานะขั้นปัจจุบัน "ขั้น n/17"', () => {
  const S = L.newState(0); L.goTo(S, 4);
  assert.match(UI.renderControls(S, false), /ขั้น 5\/17/);
});

// ---- Task 9: ดูทั้งเส้นทาง ----
test('renderStrip ตอน overview: มีปุ่ม "กลับสู่สถานี" และไม่มีสถานีใดเป็น aria-current', () => {
  const S = L.newState(0); S.overview = true;
  const h = UI.renderStrip(S);
  assert.match(h, /กลับสู่สถานี/);
  assert.equal(count(h, /aria-current="step"/g), 0);
});

test('renderControls: ปุ่ม overview เปลี่ยนข้อความตามโหมด', () => {
  const S = L.newState(0);
  assert.match(UI.renderControls(S, false), /ดูทั้งเส้นทาง/);
  S.overview = true;
  assert.match(UI.renderControls(S, false), /กลับสู่สถานี/);
});

// ---- Task 10: ภาพความเสี่ยง ----
test('ทุกเหตุการณ์ 1–5 ที่เข้า hold: แผงแสดง HOLD + ✕ + สาเหตุ ไม่พึ่งสีอย่างเดียว', () => {
  for (let id = 1; id <= 5; id++) {
    const S = walk(L.newState(id));
    const h = UI.renderHold(S);
    assert.match(h, /HOLD/, 'เหตุการณ์ ' + id);
    assert.match(h, /✕/);
    assert.ok(h.includes(UI.esc(D.SCENARIOS[id].cause)), 'ไม่มีสาเหตุของเหตุการณ์ ' + id);
  }
});

test('หลังแก้ถูกแผง HOLD หายและไม่ค้างแล้ว', () => {
  const S = walk(L.newState(3));
  L.verify(S); L.correct(S, D.SCENARIOS[3].opts.findIndex(o => o.good));
  assert.equal(UI.renderHold(S), '');
  assert.equal(L.heldAtCheckpoint(S), false);
});

// ---- Task 11: โหมดนำเสนอ + คีย์ลัด ----
test('keyToAction: แปลงปุ่มเป็นคำสั่ง', () => {
  assert.equal(UI.keyToAction('ArrowRight'), 'next');
  assert.equal(UI.keyToAction('ArrowLeft'), 'prev');
  assert.equal(UI.keyToAction(' '), 'play');
  assert.equal(UI.keyToAction('p'), 'present');
  assert.equal(UI.keyToAction('P'), 'present');
  assert.equal(UI.keyToAction('t'), 'theme');
  assert.equal(UI.keyToAction('o'), 'overview');
  assert.equal(UI.keyToAction('Escape'), 'present');
  assert.equal(UI.keyToAction('x'), null);
  assert.equal(UI.keyToAction(undefined), null);
});

test('playIntervalMs: โหมดนำเสนอช้าลงเป็น 2 เท่า (ผู้พูดทัน)', () => {
  assert.equal(UI.playIntervalMs(false), 1100);
  assert.equal(UI.playIntervalMs(true), 2200);
});

test('runAction: ใน hold คำสั่ง next/prev จากคีย์บอร์ดไม่ขยับ (ใช้ canAdvance)', () => {
  const S = walk(L.newState(1));
  const at = S.idx;
  UI.runAction(S, 'next'); UI.runAction(S, 'prev');
  assert.equal(S.idx, at);
  const T = L.newState(0);
  UI.runAction(T, 'next');
  assert.equal(T.idx, 1);
  UI.runAction(T, 'prev');
  assert.equal(T.idx, 0);
});

test('renderControls: มีปุ่มโหมดนำเสนอ (เปลี่ยนข้อความตามโหมด) และข้อความบอกคีย์ลัด', () => {
  const S = L.newState(0);
  const a = UI.renderControls(S, false, false);
  assert.match(a, /data-act="present"[^>]*>[^<]*โหมดนำเสนอ/);
  assert.match(a, /Space/);
  assert.match(UI.renderControls(S, false, true), /ออกจากโหมดนำเสนอ/);
});

// ---- Final review fix: คงโฟกัสคีย์บอร์ดหลังวาดหน้าใหม่ ----
test('focusSelector: สร้าง selector ของปุ่มจาก data-* เพื่อคืนโฟกัสหลัง render', () => {
  assert.equal(UI.focusSelector({ act: 'next' }), '[data-act="next"]');
  assert.equal(UI.focusSelector({ opt: '2' }), '[data-opt="2"]');
  assert.equal(UI.focusSelector({ station: '3' }), '[data-station="3"]');
  assert.equal(UI.focusSelector({ tab: 'risk' }), '[data-tab="risk"]');
  assert.equal(UI.focusSelector({ step: '4' }), '[data-step="4"]');
  assert.equal(UI.focusSelector({ sc: '1' }), '[data-sc="1"]');
  assert.equal(UI.focusSelector({}), null);
});
