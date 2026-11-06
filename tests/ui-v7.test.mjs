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

// ---- Task 3: เช็กลิสต์ 17 ขั้น + แถบความคืบหน้า ----
test('renderChecklist: หัวบอก "ผ่านแล้ว x จาก 17 ขั้น" + progressbar', () => {
  const S = L.newState(0); L.goTo(S, 8);
  const h = UI.renderChecklist(S);
  assert.match(h, /ผ่านแล้ว 8 จาก 17 ขั้น/);
  assert.match(h, /role="progressbar" aria-valuemin="0" aria-valuemax="17" aria-valuenow="8"/);
  assert.match(h, /47%/);
});
test('renderChecklist: 17 แถว จัด 6 กลุ่มตามสถานี ขั้นปัจจุบันมี "ตอนนี้" + aria-current', () => {
  const S = L.newState(0); L.goTo(S, 8);
  const h = UI.renderChecklist(S);
  assert.equal(count(h, /data-step="/g), 17);
  assert.equal(count(h, /class="ck-grp"/g), 6);
  assert.equal(count(h, /class="ck-row done"/g), 8);
  assert.match(h, /data-step="8" class="ck-row now" aria-current="step"[\s\S]*?ตอนนี้/);
  assert.doesNotMatch(h, /line-through/);
});
test('renderChecklist: แต่ละขั้นมีชื่อและเวลาสั้น ๆ', () => {
  const h = UI.renderChecklist(L.newState(0));
  assert.match(h, /data-step="0"[\s\S]*?ฟาร์มโคอิพรีเมียม[\s\S]*?ก่อนวันส่ง/);
  assert.match(h, /data-step="8"[\s\S]*?บิน NRT → BKK[\s\S]*?16:20 JST/);
});
test('renderChecklist: hold = ✕ ที่ขั้นค้าง และทุกแถวกดไม่ได้ · overview ไม่มี aria-current', () => {
  const S = walk(L.newState(1));
  const h = UI.renderChecklist(S);
  assert.match(h, /class="ck-row now bad"[\s\S]*?✕/);
  assert.equal(count(h, /disabled/g), 17);
  const O = L.newState(0); O.overview = true;
  assert.equal(count(UI.renderChecklist(O), /aria-current/g), 0);
});
test('progressDone: ครบ 17 เมื่อจบปกติ', () => {
  assert.equal(UI.progressDone(walk(L.newState(0))), 17);
});
test('V7: เลิกใช้ renderTimeline และ renderStationSteps', () => {
  assert.equal(UI.renderTimeline, undefined);
  assert.equal(UI.renderStationSteps, undefined);
  assert.doesNotMatch(readHtml(), /id="station-steps"/);
});

// ---- Task 4: การ์ดข้อมูล V6 ปรับใหม่ ----
test('renderFacts V7: หัวการ์ดมีไอคอนในบรรทัดป้าย · เอกสารเป็นป้ายทีละฉบับ', () => {
  const S = L.newState(0); L.goTo(S, 8);
  const h = UI.renderFacts(S);
  assert.equal(count(h, /class="fact[ "]/g), 4);
  assert.match(h, /<span class="lab"><span class="ic">/);
  assert.equal(count(h, /class="chip doc"/g), D.STEPS[8].docs.length);
  assert.match(h, /class="fact wide hazard"[\s\S]*?ความเสี่ยง/);
});
test('renderFacts V7: มาตรวัดถุงเป็นตัวเลขใหญ่ + ป้ายสถานะ + สเกล 0–24', () => {
  const S = L.newState(0); L.goTo(S, 8);                  // ขั้น 9 บินถึง BKK: L.bagAgeMin = 900 นาที = 15 ชม.
  const h = UI.renderFacts(S);
  assert.match(h, /class="bag" role="meter" aria-valuemin="0" aria-valuemax="24" aria-valuenow="15\.0"/);
  assert.match(h, /15\.0 <small>\/ 24 ชม\.<\/small>/);
  assert.match(h, /✓ ปลอดภัย · เหลือ 9\.0 ชม\./);
  assert.match(h, /<span>0<\/span><span>6<\/span><span>12<\/span><span>18<\/span><span>24 ชม\.<\/span>/);
});
test('renderFacts V7: ถุงเกิน 24 ชม. แสดง ✕ เกิน และไม่มี "เหลือ"', () => {
  const S = L.newState(0); L.goTo(S, 13); S.shift = 181; S.shiftFrom = 0;   // 1441 นาที (วิธีเดียวกับ time.test.mjs)
  assert.equal(L.bagStatus(S), 'over');
  const h = UI.renderFacts(S);
  assert.match(h, /✕ เกิน 24 ชม\./);
  assert.doesNotMatch(h, /เหลือ/);
});
test('ไม่มีอีโมจิ 🕒 ในป้ายเวลา', () => { assert.doesNotMatch(UI.renderTimeBadge(L.newState(0)), /🕒/); });

// ---- Task 5: ของลอยบนฉากเป็นกระจก + มือถือการ์ดลอย ----
test('renderSheetHead V7: การ์ดลอยมีชื่อขั้น ใครทำ เวลา และป้ายถุง', () => {
  const S = L.newState(0); L.goTo(S, 8);
  const h = UI.renderSheetHead(S, false);
  assert.match(h, /class="sh-card"/);
  assert.match(h, /ขั้น 9 จาก 17/);
  assert.match(h, /ใครทำ: /);
  assert.match(h, /class="chip"[^>]*>[\s\S]*?JST/);
  assert.match(h, /class="chip ok"[\s\S]*?ถุง/);
  assert.match(h, /class="sheet-toggle" data-act="sheet"[^>]*aria-expanded="false"[^>]*aria-label="ขยายแผ่นข้อมูล/);
});
test('renderSheetHead V7: ก่อนปิดผนึกถุงไม่มีป้ายถุง · เปิดแล้วปุ่มเป็นย่อ', () => {
  assert.doesNotMatch(UI.renderSheetHead(L.newState(0), false), /ถุง/);
  assert.match(UI.renderSheetHead(L.newState(0), true), /aria-expanded="true"[^>]*aria-label="ย่อแผ่นข้อมูล/);
});
test('CSS V7: ของลอยบนฉากใช้กระจก · แผ่นมือถือปิด = โปร่ง ให้การ์ดลอยเป็นกระจก · เปิด = พื้นทึบ', () => {
  for (const sel of ['#card', '.stage-ctrl', '.risk-menu summary']) assert.match(css, new RegExp(sel.replace(/[.#]/g, '\\$&') + '\\{[^}]*var\\(--glass\\)'), sel);
  assert.match(css, /\.panel\.sheet:not\(\.open\)\{[^}]*background:transparent/);
  assert.match(css, /\.sheet:not\(\.open\) \.sh-card\{[^}]*var\(--glass\)/);
  assert.match(css, /\.sheet\.open\{[^}]*background:var\(--surface\)/);
  assert.match(css, /orientation:portrait\)\{[\s\S]*?#card\{[^}]*display:none/);
});

// ---- Task 6: หน้าต้อนรับใหม่ + ไอคอนชุดเดียว ----
test('renderWelcome V7: การ์ดกระจก · เส้นทางมีเวลาออก/ถึงจากข้อมูล · ปุ่มเริ่มเป็นปุ่มหลัก', () => {
  const h = UI.renderWelcome();
  assert.match(h, /^<div class="w-inner glass">/);
  assert.match(h, /18:25 JST → 23:00 ICT/);
  assert.match(h, /JL707 · Boeing 787-8/);
  assert.match(h, /class="w-start" data-act="start"/);
});
test('CSS หน้าต้อนรับ V7: ไม่มีแถบดำไล่สีทึบ 90% · ตัวหนังสือใช้โทเคนธีม · ปุ่มเป็นแคปซูล', () => {
  assert.doesNotMatch(css, /rgba\(0,0,0,\.9\) 0%/);
  assert.match(css, /\.welcome\{[^}]*color:var\(--text\)/);
  assert.match(css, /\.cta button\{[^}]*border-radius:999px/);
});
test('ไม่มีอีโมจิเป็นไอคอนบนหน้า (แถบบน วิธีใช้ เมนูเหตุการณ์)', () => {
  const body = readHtml().split('<body>')[1].split('<script')[0];
  for (const e of ['✈', '🇯🇵', '🇹🇭', '❓', '⚠', '🕒']) assert.ok(!body.includes(e), e);
  assert.doesNotMatch(UI.renderScenarioMenu(L.newState(0)), /⚠/);
});
