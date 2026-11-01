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
