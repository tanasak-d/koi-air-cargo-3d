// เทสต์หน้าจอ V6 (หน้าติดตามพัสดุ โทนดำขาว) · แผน docs/superpowers/plans/2026-11-01-ui-v6.md
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, L = ctx.KoiLogic, D = ctx.KoiData;
const css = /<style>([\s\S]*?)<\/style>/.exec(readHtml())[1];
const walk = (S, n = 50) => { for (let i = 0; i < n && L.canAdvance(S); i++) L.next(S); return S; };
const count = (s, re) => (s.match(re) || []).length;

// ---- Task 2: แถบเส้นทาง 6 สถานี ----
test('renderRoute: ตอน hold ปุ่มสถานีกดไม่ได้ทั้ง 6', () => {
  const S = walk(L.newState(1));
  assert.equal(count(UI.renderRoute(S), /disabled/g), 6);
});
test('renderRoute: ภาพรวม (overview) ไม่มี aria-current', () => {
  const S = L.newState(0); S.overview = true;
  assert.equal(count(UI.renderRoute(S), /aria-current/g), 0);
});
test('CSS .route: แถบไม่กว้างเกินจอ (min-width:0)', () => {
  assert.match(css, /\.route\{[^}]*min-width:0/);
});
test('focusSelector: ปุ่มสถานีคืนโฟกัสได้หลังวาดใหม่', () => {
  assert.equal(UI.focusSelector({ station: '2' }), '[data-station="2"]');
});

// ---- Task 3: การ์ดข้อมูลแบบไอคอน (แทนแท็บ) ----
test('renderFacts: มี 4 การ์ด ใครทำ/ทำอะไร/เอกสาร/ความเสี่ยง และชื่อขั้นปัจจุบัน', () => {
  const S = L.newState(0); L.goTo(S, 3);
  const h = UI.renderFacts(S);
  assert.equal(count(h, /class="fact[ "]/g), 4);
  for (const w of ['ใครทำ', 'ทำอะไร', 'เอกสาร', 'ความเสี่ยง']) assert.match(h, new RegExp(w));
  assert.match(h, /ขั้นที่ 4/);
  assert.match(h, /สถานี 1 ฟาร์มผู้ส่ง/);
  assert.match(h, /บรรจุถุง 3 ชั้น/);
});
test('renderFacts: มาตรวัดอายุถุงบอกเป็นตัวเลขและ ✓/✕ ไม่ใช่สีอย่างเดียว', () => {
  const S = L.newState(0); L.goTo(S, 8);
  const h = UI.renderFacts(S);
  assert.match(h, /\/ 24 ชม\./);
  assert.match(h, /[✓✕]/);
  assert.match(h, /role="meter"/);
});
test('renderFacts: ก่อนปิดผนึกถุงไม่มีมาตรวัด', () => {
  assert.doesNotMatch(UI.renderFacts(L.newState(0)), /class="meter/);
});
test('renderMore: พับได้ มีทำไมสำคัญ ถ้าผ่าน/ไม่ผ่าน และ 4-Flow ครบทุกเลน', () => {
  const h = UI.renderMore(L.newState(0));
  assert.match(h, /^<details class="more"/);
  assert.match(h, /ทำไมสำคัญ/);
  assert.match(h, /ถ้าผ่าน \/ ไม่ผ่าน/);
  assert.equal(count(h, /data-lane="/g), D.FOURFLOW.length);
});
test('V6: เลิกใช้แท็บและป้ายสถานีบนภาพ', () => {
  assert.equal(UI.renderTab, undefined);
  assert.equal(UI.renderTabBar, undefined);
  assert.equal(UI.renderStationBadge, undefined);
});

// ---- Task 4: แถบเล่น + แถบเวลา 17 ขีด และรายการขั้นในสถานี ----
test('renderScrub: 17 ขีด ขีดที่ผ่านแล้ว/ตอนนี้แยกด้วยคลาส และบอก "ขั้น 5 /17"', () => {
  const S = L.newState(0); L.goTo(S, 4);
  const h = UI.renderScrub(S, false);
  assert.equal(count(h, /data-step="/g), 17);
  assert.match(h, /data-step="4"[^>]*class="tick now"/);
  assert.match(h, /data-step="0"[^>]*class="tick done"/);
  assert.match(h, /ขั้น 5 \/17/);
  assert.match(h, /data-act="play"[^>]*aria-label="เล่น"/);
  assert.match(UI.renderScrub(S, true), /data-act="play"[^>]*aria-label="หยุด"/);
});
test('renderScrub: ตอน hold ขีดและปุ่มเดินหน้ากดไม่ได้', () => {
  const S = walk(L.newState(1));
  const h = UI.renderScrub(S, false);
  assert.equal(count(h, /data-step="[^"]*"[^>]*disabled/g), 17);
  assert.match(h, /data-act="next"[^>]*disabled/);
});
test('V6: เลิกใช้ renderStageControls', () => {
  assert.equal(UI.renderStageControls, undefined);
});

// ---- Task 5: หน้าต้อนรับ ----
test('renderWelcome: บอกเส้นทาง จำนวนสถานี/ขั้น/สถานการณ์เสี่ยง และมีปุ่มเริ่ม + นำเสนอ', () => {
  const h = UI.renderWelcome();
  assert.match(h, /NRT/); assert.match(h, /BKK/); assert.match(h, /JL707/);
  assert.match(h, /<b>6<\/b><span>สถานี/);
  assert.match(h, /<b>17<\/b><span>ขั้นตอน/);
  assert.match(h, new RegExp('<b>' + (D.SCENARIOS.length - 1) + '</b><span>สถานการณ์เสี่ยง'));
  assert.match(h, /data-act="start"/); assert.match(h, /data-act="present"/);
  assert.match(h, /<h1/);
});
test('parseStepHash: #step=5 → 4 · ค่าผิด/นอกช่วง → null', () => {
  assert.equal(UI.parseStepHash('#step=5'), 4);
  assert.equal(UI.parseStepHash('#step=17'), 16);
  assert.equal(UI.parseStepHash('#step=0'), null);
  assert.equal(UI.parseStepHash('#step=99'), null);
  assert.equal(UI.parseStepHash('#step=abc'), null);
  assert.equal(UI.parseStepHash(''), null);
});
test('keyToAction: Enter = start', () => {
  assert.equal(UI.keyToAction('Enter'), 'start');
});
test('focusSelector: ปุ่มเริ่มบนหน้าต้อนรับ', () => {
  assert.equal(UI.focusSelector({ act: 'start' }), '[data-act="start"]');
});

// ---- Task 6: โหมดนำเสนอ (โปรเจกเตอร์) ----
test('renderPresentSide: ขั้นที่ 4 จาก 17 · สถานี 1 จาก 6 · ความคืบหน้า 24% · มีคีย์ลัด Esc', () => {
  const S = L.newState(0); L.goTo(S, 3);
  const h = UI.renderPresentSide(S);
  assert.match(h, /ขั้นที่ 4 จาก 17/);
  assert.match(h, /สถานี 1 จาก 6/);
  assert.match(h, /width:24%/);
  assert.match(h, /Esc/);
  for (const w of ['ใครทำ', 'เอกสาร', 'ความเสี่ยง']) assert.match(h, new RegExp(w));
});
test('renderPresentSide: ขั้นสุดท้ายความคืบหน้า 100%', () => {
  const S = L.newState(0); L.goTo(S, 16);
  assert.match(UI.renderPresentSide(S), /width:100%/);
});
test('renderPresentSide: ตอน hold แสดง ✕ HOLD และปุ่ม VERIFY', () => {
  const h = UI.renderPresentSide(walk(L.newState(1)));
  assert.match(h, /✕ HOLD/);
  assert.match(h, /data-act="verify"/);
});
test('renderPresentSide: มีปุ่มออกจากโหมดนำเสนอให้คนใช้เมาส์', () => {
  assert.match(UI.renderPresentSide(L.newState(0)), /data-act="present"/);
});

// ---- Task 7: จัดหน้าตามขนาดจอ + แผ่นข้อมูลมือถือ ----
test('sheetSnap: ลากขึ้นเกิน 20% = เปิด · ลากลงเกิน 20% = ปิด · น้อยกว่านั้นคงเดิม', () => {
  assert.equal(UI.sheetSnap(-100, 400, false), true);
  assert.equal(UI.sheetSnap(100, 400, true), false);
  assert.equal(UI.sheetSnap(-40, 400, false), false);
  assert.equal(UI.sheetSnap(40, 400, true), true);
  assert.equal(UI.sheetSnap(-100, 0, false), false);   // ยังวัดความสูงไม่ได้ = คงเดิม
});
test('renderSheetTabs: 3 แท็บ และแท็บที่เลือก aria-selected', () => {
  const h = UI.renderSheetTabs('route');
  assert.equal(count(h, /data-sheet="/g), 3);
  assert.match(h, /data-sheet="route"[^>]*aria-selected="true"/);
  assert.equal(count(h, /aria-selected="true"/g), 1);
  for (const w of ['รายละเอียด', 'เส้นทาง 17 ขั้น', 'สถานการณ์เสี่ยง']) assert.match(h, new RegExp(w));
});
test('renderSheetHead: สถานี ชื่อขั้น เวลา และปุ่มเปิดแผ่นบอก aria-expanded', () => {
  const S = L.newState(0); L.goTo(S, 3);
  const h = UI.renderSheetHead(S, false);
  assert.match(h, /ขั้น 4 จาก 17/);
  assert.match(h, /บรรจุถุง 3 ชั้น/);
  assert.match(h, /data-act="sheet"[^>]*aria-expanded="false"/);
  assert.match(UI.renderSheetHead(S, true), /aria-expanded="true"/);
});
test('focusSelector: แท็บแผ่นข้อมูลคืนโฟกัสได้', () => {
  assert.equal(UI.focusSelector({ sheet: 'risk' }), '[data-sheet="risk"]');
});
test('CSS: มีช่วงจอ 1024 / 767 / แนวนอนเตี้ย และใช้ dvh กับมือถือ', () => {
  assert.match(css, /@media \(min-width:1024px\)/);
  assert.match(css, /@media \(max-width:767px\)/);
  assert.match(css, /@media \(max-height:500px\) and \(orientation:landscape\)/);
  assert.match(css, /100dvh/);
  assert.match(css, /safe-area-inset-bottom/);
});
test('CSS: ปิดอนิเมชันแผ่นข้อมูลเมื่อ prefers-reduced-motion', () => {
  assert.match(css, /prefers-reduced-motion[^{]*\{[^}]*\.sheet/);
});
test('มือถือ: ตัวเลือกจอมือถือใน JS ตรงกับใน CSS', () => {
  assert.ok(css.includes('@media ' + UI.MOBILE_MQ + '{'), UI.MOBILE_MQ);
});
test('การ์ดความเสี่ยงไม่ใช้คลาส risk (ชนกับเมนูเหตุการณ์ที่ลอยมุมขวาบน)', () => {
  assert.doesNotMatch(UI.renderFacts(L.newState(0)), /class="fact[^"]*\brisk\b/);
});
test('ชิปเส้นทางบนแถบบนไม่ใช้คลาส route (ชนกับแถบเส้นทาง 6 สถานี)', () => {
  assert.doesNotMatch(readHtml(), /class="chip route"/);
});
test('CSS: ปีกกาเปิด/ปิดสมดุล (ปีกกาเกินทำให้กฎถัดไปหายเงียบ ๆ)', () => {
  const body = css.replace(/\/\*[\s\S]*?\*\//g, '');
  let depth = 0;
  for (const ch of body) {
    if (ch === '{') depth++;
    if (ch === '}') { depth--; assert.ok(depth >= 0, 'มี } เกิน'); }
  }
  assert.equal(depth, 0);
});

// ---- Final review fixes ----
const block = (head) => {            // เนื้อในของ @media ที่ขึ้นต้นด้วย head (นับปีกกา)
  const i = css.indexOf(head + '{'); assert.ok(i >= 0, 'ไม่พบ ' + head);
  let d = 0, j = i + head.length;
  for (; j < css.length; j++) { if (css[j] === '{') d++; if (css[j] === '}' && --d === 0) break; }
  return css.slice(i + head.length + 1, j);
};
const PORTRAIT = '@media ' + UI.MOBILE_MQ;
test('R1: โหมดนำเสนอบนมือถือแนวตั้ง ภาพบน แผงล่าง (ไม่บีบแผงเหลือ 40px)', () => {
  const b = block(PORTRAIT);
  // ต้องขึ้นต้นด้วย body เพื่อให้เจาะจงกว่ากฎโหมดนำเสนอหลักที่ประกาศทีหลังในไฟล์
  assert.match(b, /body #app\.present \.layout\{[^}]*grid-template-columns:1fr/);
  assert.match(b, /body #app\.present #stage\{[^}]*position:relative/);
});
test('R2: focusSelector จำกล่องที่ปุ่มอยู่ (data-step ซ้ำ 3 ที่)', () => {
  assert.equal(UI.focusSelector({ step: '2' }, 'station-steps'), '#station-steps [data-step="2"]');
  assert.equal(UI.focusSelector({ step: '2' }), '[data-step="2"]');
  assert.equal(UI.focusSelector({}, 'x'), null);
});
test('R3: ระหว่างหน้าต้อนรับ กดได้แค่ เริ่ม / นำเสนอ / ธีม', () => {
  for (const a of ['start', 'present', 'theme']) assert.equal(UI.welcomeAllows(a), true, a);
  for (const a of ['next', 'prev', 'play', 'overview', 'sheet', undefined]) assert.equal(UI.welcomeAllows(a), false, String(a));
});
test('R4: ปุ่มบนมือถือแนวตั้งสูงอย่างน้อย 44px (ขีดเวลา ที่จับ สถานี แท็บ)', () => {
  const b = block(PORTRAIT);
  assert.match(b, /\.tick\{[^}]*height:44px/);
  assert.match(b, /\.grab\{[^}]*min-height:44px/);
  assert.match(b, /\.stn button\{[^}]*min-height:44px/);
  assert.match(b, /\.sheet-tabs button\{[^}]*min-height:44px/);
});
test('R5: มือถือแนวนอน แถบเล่นเหลือแถวเดียว (ซ่อนตัวนับ ปุ่มเล็กลง)', () => {
  const b = block('@media (max-height:500px) and (orientation:landscape)');
  assert.match(b, /\.stage-ctrl \.count\{display:none\}/);
  assert.match(b, /\.ctl[^{]*\{[^}]*width:36px/);
  assert.match(b, /\.stage-ctrl\{[^}]*flex-wrap:nowrap/);
});
test('R6: แผ่นมือถือเปิดเองเมื่อเข้า HOLD หรือจบ (ไม่งั้นมองไม่เห็นผล)', () => {
  assert.equal(UI.sheetAutoOpen('play', 'hold'), true);
  assert.equal(UI.sheetAutoOpen('hold', 'hold'), false);
  assert.equal(UI.sheetAutoOpen('hold', 'end'), true);
  assert.equal(UI.sheetAutoOpen('play', 'done'), true);
  assert.equal(UI.sheetAutoOpen('done', 'done'), false);
  assert.equal(UI.sheetAutoOpen('play', 'play'), false);
});
test('R1b: มือถือแนวตั้งซ่อนปุ่มโหมดนำเสนอบนหน้าต้อนรับ (มือถือไม่มีคีย์บอร์ดคุมขั้น)', () => {
  assert.match(block(PORTRAIT), /\.cta \.w-ghost\{display:none\}/);
});
