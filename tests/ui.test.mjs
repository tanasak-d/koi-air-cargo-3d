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

test('renderHold: ใน hold มีคำ HOLD, ✕ และปุ่ม VERIFY; ไม่พึ่งสีอย่างเดียว', () => {
  const S = walk(L.newState(1));
  const h = UI.renderHold(S);
  assert.match(h, /HOLD/);
  assert.match(h, /i-x"\/><\/svg>/);
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
  assert.match(h, /i-x"\/><\/svg>/);
  assert.match(h, /สูญเสีย/);
  const ok = walk(L.newState(0));
  assert.match(UI.renderEnd(ok), /i-check"\/><\/svg>/);
  assert.equal(UI.renderEnd(L.newState(0)), '');
});

test('renderFacts/renderMore (V6 แทนแท็บ): ความเสี่ยง, ใคร/ทำอะไร, เอกสาร, 4-Flow', () => {
  const S = L.newState(0); L.goTo(S, 3); // ขั้น 4 บรรจุถุง
  const facts = UI.renderFacts(S);
  assert.match(facts, /ถุงรั่ว/);
  assert.match(facts, /Lucky Koi House/);
  assert.match(facts, /1 ตัว : 1 ถุง : 1 กล่อง/);
  assert.match(facts, /Packing List/);
  const flow = UI.renderMore(S);
  assert.equal(count(flow, /data-lane="/g), 4);
});

test('renderMore 4-Flow: เลนที่มีปัญหาแสดง ✕ ไม่ใช่สีอย่างเดียว', () => {
  const S = walk(L.newState(1));
  const flow = UI.renderMore(S);
  assert.match(flow, /i-x"\/><\/svg>/);
  assert.match(flow, /i-check"\/><\/svg>/);
});

test('ข้อมูลที่มี HTML ถูก escape', () => {
  const f = fresh();
  f.D.STEPS[0].name = '<script>alert(1)</script>';
  const S = f.L.newState(0);
  const h = f.UI.renderChecklist(S) + f.UI.renderFacts(S) + f.UI.renderCard(S);
  assert.doesNotMatch(h, /<script>alert/);
  assert.match(h, /&lt;script&gt;/);
});

test('renderTimeBadge: ขั้นประมาณการมีคำ "โดยประมาณ" และแสดงอายุถุงหลังปิดผนึก', () => {
  const S = L.newState(0); L.goTo(S, 10); // ขั้น 11 approx
  assert.match(UI.renderTimeBadge(S), /โดยประมาณ/);
  assert.match(UI.renderTimeBadge(S), /18/);   // เส้นตาย SOP 18 ชม.
  const early = L.newState(0);
  assert.doesNotMatch(UI.renderTimeBadge(early), /อายุถุง/); // ยังไม่ปิดผนึก
});

test('renderTimeBadge: ถุงเกินเส้นตาย 18 ชม. แสดง ✕ พร้อมข้อความ และไม่เกินแสดง ✓', () => {
  const S = walk(L.newState(0)); // จบที่ขั้น 17 อายุถุง 16 ชม. ยังไม่เกิน
  assert.equal(L.bagStatus(S), 'ok');
  assert.match(UI.renderTimeBadge(S), /i-check"\/><\/svg> ไม่เกิน 18 ชม\./);
  S.shift = 121; S.shiftFrom = 0; // เลื่อนจนเกิน 1080 นาที
  assert.equal(L.bagStatus(S), 'over');
  const h = UI.renderTimeBadge(S);
  assert.match(h, /i-x"\/><\/svg>/);
  assert.match(h, /เกิน 18 ชม\./);
});

test('renderGlossary: ห่อศัพท์ครั้งแรกด้วย abbr, ครั้งที่สองไม่ห่อ, และ escape ข้อความ', () => {
  const h = UI.renderGlossary('NOTOC คือ <b>ใบแจ้ง</b> NOTOC');
  assert.equal(count(h, /<abbr /g), 1);
  assert.match(h, /title="[^"]+"/);
  assert.doesNotMatch(h, /<b>/);
  assert.match(h, /&lt;b&gt;/);
  assert.equal(UI.renderGlossary('สวัสดี'), 'สวัสดี');
});

test('renderScrub: ปุ่มถัดไปปิดเมื่อค้าง hold และเปิดตอนปกติ', () => {
  const S = walk(L.newState(1));
  assert.match(UI.renderScrub(S, false), /data-act="next"[^>]*disabled/);
  assert.doesNotMatch(UI.renderScrub(L.newState(0), false), /data-act="next"[^>]*disabled/);
});

test('บอกสถานะขั้นปัจจุบัน "ขั้น n/17"', () => {
  const S = L.newState(0); L.goTo(S, 4);
  assert.match(UI.renderScrub(S, false), /ขั้น 5 \/17/);
});

test('renderScenarioMenu: เหตุการณ์ครบ 6 แบบ aria-pressed ถูกตัว และหัวเมนูบอกชื่อเหตุการณ์ที่เลือก', () => {
  const h = UI.renderScenarioMenu(L.newState(2));
  assert.equal(count(h, /data-sc="/g), 6);
  assert.match(h, /data-sc="2" aria-pressed="true"/);
  assert.equal(count(h, /aria-pressed="true"/g), 1);
  assert.match(h, /<summary[^>]*>(?:(?!<\/summary>)[\s\S])*พลาด cut-off[\s\S]*?<\/summary>/);   // V7 หัวเมนูมีไอคอน svg นำหน้า
});

test('renderCard: บอก "ขั้น n" ชื่อขั้น และ "ใครทำ" ของขั้นปัจจุบัน; ตอน hold มี ✕ HOLD', () => {
  const S = L.newState(0); L.goTo(S, 3);
  const h = UI.renderCard(S);
  assert.match(h, /ขั้น 4/);
  assert.match(h, /บรรจุถุง 3 ชั้น/);
  assert.match(h, /ใครทำ/);
  assert.match(h, /Lucky Koi House/);
  assert.doesNotMatch(h, /HOLD/);
  assert.match(UI.renderCard(walk(L.newState(1))), /i-x"\/><\/svg> HOLD/);
});

// ---- Task 9: ดูทั้งเส้นทาง ----
test('renderScrub: ปุ่ม overview เปลี่ยนข้อความตามโหมด', () => {
  const S = L.newState(0);
  assert.match(UI.renderScrub(S, false), /ดูทั้งเส้นทาง/);
  S.overview = true;
  assert.match(UI.renderScrub(S, false), /กลับสู่สถานี/);
});

// ---- Task 10: ภาพความเสี่ยง ----
test('ทุกเหตุการณ์ 1–5 ที่เข้า hold: แผงแสดง HOLD + ✕ + สาเหตุ ไม่พึ่งสีอย่างเดียว', () => {
  for (let id = 1; id <= 5; id++) {
    const S = walk(L.newState(id));
    const h = UI.renderHold(S);
    assert.match(h, /HOLD/, 'เหตุการณ์ ' + id);
    assert.match(h, /i-x"\/><\/svg>/);
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

test('presentLabel: ปุ่มโหมดนำเสนอบนแถบบนเปลี่ยนข้อความตามโหมด', () => {
  assert.equal(UI.presentLabel(false), 'โหมดนำเสนอ');
  assert.equal(UI.presentLabel(true), 'ออกจากโหมดนำเสนอ');
});

// ---- Final review fix: คงโฟกัสคีย์บอร์ดหลังวาดหน้าใหม่ ----
test('focusSelector: สร้าง selector ของปุ่มจาก data-* เพื่อคืนโฟกัสหลัง render', () => {
  assert.equal(UI.focusSelector({ act: 'next' }), '[data-act="next"]');
  assert.equal(UI.focusSelector({ opt: '2' }), '[data-opt="2"]');
  assert.equal(UI.focusSelector({ station: '3' }), '[data-station="3"]');
  assert.equal(UI.focusSelector({ sheet: 'risk' }), '[data-sheet="risk"]');
  assert.equal(UI.focusSelector({ step: '4' }), '[data-step="4"]');
  assert.equal(UI.focusSelector({ sc: '1' }), '[data-sc="1"]');
  assert.equal(UI.focusSelector({}), null);
});

// ---- รุ่น 2 Task 11: เล่นอัตโนมัติรอให้อนิเมชันของขั้นจบก่อน ----
test('playDelayMs: รอจนช็อตของขั้นจบแล้วพักอีกนิด (โหมดนำเสนอพักนานกว่า ให้ผู้พูดอธิบาย)', () => {
  assert.equal(UI.playDelayMs(6, false), 6800);
  assert.equal(UI.playDelayMs(6, true), 8500);
  assert.equal(UI.playDelayMs(undefined, false), UI.playIntervalMs(false));   // ไม่รู้ความยาวช็อต ใช้ค่าเดิม
});

// ---- V4 หน้าตาแบบ "ติดตามการขนส่ง" (มาร์ชอนุมัติร่าง 2026-10-18) ----
test('renderStatus: แถบบนบอกสถานะการขนส่ง ปกติ ✓ / HOLD ✕ / สูญเสีย ✕ / ถึงผู้รับ ✓ (ไม่พึ่งสีอย่างเดียว)', () => {
  assert.match(UI.renderStatus(L.newState(0)), /i-check"\/><\/svg> สถานะปกติ/);
  const held = walk(L.newState(2));
  assert.match(UI.renderStatus(held), /i-x"\/><\/svg> HOLD · ขั้น 7/);
  L.verify(held); L.correct(held, D.SCENARIOS[2].opts.findIndex(o => !o.good));
  assert.match(UI.renderStatus(held), /i-x"\/><\/svg> สูญเสีย/);
  assert.match(UI.renderStatus(walk(L.newState(0))), /i-check"\/><\/svg> ถึงมือผู้รับ/);
});

test('renderScrub V6: มีแถบความคืบหน้าของขั้น (ฉาก 3 มิติเติมความยาวเอง)', () => {
  assert.match(UI.renderScrub(L.newState(0), false), /id="step-progress"/);
});
