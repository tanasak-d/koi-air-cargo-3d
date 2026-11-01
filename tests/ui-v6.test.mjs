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
test('renderRoute: 6 สถานี · ก่อนหน้า = done · ปัจจุบัน = now + ป้าย "ตอนนี้" + aria-current', () => {
  const S = L.newState(0); L.goTo(S, 7);          // ขั้น 8 = สถานี 2
  const h = UI.renderRoute(S);
  assert.equal(count(h, /data-station="/g), 6);
  assert.equal(count(h, /class="stn done"/g), 1);
  assert.match(h, /class="stn now"[\s\S]*?ตอนนี้/);
  assert.equal(count(h, /aria-current="location"/g), 1);
  assert.match(h, /ขั้น 7–8/);
  assert.match(h, /นาริตะ NRT/);
});
test('renderRoute: สถานีที่มีขั้นเดียวแสดงเลขเดียว', () => {
  assert.match(UI.renderRoute(L.newState(0)), /ขั้น 9</);
});
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
  assert.match(h, /เพดาน 24 ชม\./);
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
test('renderStationSteps: แสดงเฉพาะขั้นของสถานีปัจจุบัน ขั้นปัจจุบัน aria-current', () => {
  const S = L.newState(0); L.goTo(S, 3);
  const h = UI.renderStationSteps(S);
  assert.equal(count(h, /data-step="/g), 6);   // สถานี 1 = ขั้น 1–6
  assert.match(h, /data-step="3"[^>]*aria-current="step"/);
  assert.match(h, /ขั้นในสถานีนี้/);
});
test('V6: เลิกใช้ renderStageControls', () => {
  assert.equal(UI.renderStageControls, undefined);
});
