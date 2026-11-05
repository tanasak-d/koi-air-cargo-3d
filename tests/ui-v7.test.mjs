// เทสต์หน้าจอ V7 (เช็กลิสต์ · แคปซูลสถานี · การ์ดข้อมูลใหม่ · Liquid Glass) · แผน docs/superpowers/plans/2026-11-06-ui-v7.md
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, L = ctx.KoiLogic, D = ctx.KoiData;
const css = /<style>([\s\S]*?)<\/style>/.exec(readHtml())[1];
const walk = (S, n = 50) => { for (let i = 0; i < n && L.canAdvance(S); i++) L.next(S); return S; };
const count = (s, re) => (s.match(re) || []).length;

// ---- Task 2: แถบ 6 สถานีแบบแคปซูล ----
test('renderRoute V7: สถานีปัจจุบันเป็นแคปซูล บอก "สถานี k/6 · ขั้น n" และไม่มีป้าย "ตอนนี้"', () => {
  const S = L.newState(0); L.goTo(S, 8);                 // ขั้น 9 = สถานี 3
  const h = UI.renderRoute(S);
  assert.match(h, /class="stn now"[\s\S]*?class="txt cap"><small>สถานี 3\/6 · ขั้น 9<\/small><b>เที่ยวบิน JL707<\/b>/);
  assert.doesNotMatch(h, /now-tag/);
  assert.equal(count(h, /aria-current="location"/g), 1);
  assert.match(h, /aria-label="สถานี 3 เที่ยวบิน JL707 ขั้น 9 ตอนนี้"/);
});
test('renderRoute V7: สถานีอื่นเห็นแค่ชื่อ ช่วงขั้นอยู่ใน aria-label', () => {
  const h = UI.renderRoute(L.newState(0));
  assert.doesNotMatch(h, /<span>ขั้น /);
  assert.match(h, /aria-label="สถานี 5 [^"]*ขั้น 11–14/);
});
test('renderRoute V7: ตอน hold กดไม่ได้ทั้ง 6 และแคปซูลยังอยู่', () => {
  const h = UI.renderRoute(walk(L.newState(1)));
  assert.equal(count(h, /disabled/g), 6);
  assert.match(h, /class="txt cap"/);
});
test('renderRoute V7: ภาพรวม (overview) ไม่มีแคปซูล', () => {
  const S = L.newState(0); S.overview = true;
  assert.doesNotMatch(UI.renderRoute(S), /txt cap/);
});
test('CSS แคปซูล: ไม่ล้นจอ (flex + min-width:0) และบนมือถือแถบเป็นกระจก', () => {
  assert.match(css, /\.route\{[^}]*display:flex[^}]*min-width:0/);
  assert.match(css, /\.stn \.cap\{[^}]*border-radius:999px/);
  assert.match(css, /orientation:portrait\)\{[\s\S]*?\.route-wrap\{[^}]*var\(--glass\)/);
});
