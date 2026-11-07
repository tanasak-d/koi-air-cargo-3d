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
  assert.match(h, /class="stn now"[\s\S]*?class="txt cap"><small>สถานี 3\/6 · ขั้น 9<\/small><b>เที่ยวบิน NN393<\/b>/);
  assert.doesNotMatch(h, /now-tag/);
  assert.equal(count(h, /aria-current="location"/g), 1);
  assert.match(h, /aria-label="สถานี 3 เที่ยวบิน NN393 ขั้น 9 ตอนนี้"/);
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
  assert.match(h, /data-step="0"[\s\S]*?ฟาร์มโคอิพรีเมียม[\s\S]*?ก่อนวัน D/);
  assert.match(h, /data-step="8"[\s\S]*?บิน NRT → BKK[\s\S]*?07:00 JST/);
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
test('renderFacts: มาตรวัดถุงเทียบเส้นตาย SOP 18 ชม. + ป้ายสถานะ + สเกล 0–18', () => {
  const S = L.newState(0); L.goTo(S, 8);                  // ขั้น 9 บินถึง BKK 12:00 ICT: 840 − 60 = 780 นาที = 13 ชม.
  const h = UI.renderFacts(S);
  assert.match(h, /class="bag" role="meter" aria-valuemin="0" aria-valuemax="18" aria-valuenow="13\.0"/);
  assert.match(h, /13\.0 <small>\/ 18 ชม\.<\/small>/);
  assert.match(h, /✓ ปลอดภัย · เหลือ 5\.0 ชม\./);
  assert.match(h, /<span>0<\/span><span>6<\/span><span>12<\/span><span>18 ชม\.<\/span>/);
});
test('renderFacts: ถุงเกินเส้นตาย 18 ชม. แสดง ✕ เกิน และไม่มี "เหลือ"', () => {
  const S = L.newState(0); L.goTo(S, 13); S.shift = 181; S.shiftFrom = 0;   // 1441 นาที (วิธีเดียวกับ time.test.mjs)
  assert.equal(L.bagStatus(S), 'over');
  const h = UI.renderFacts(S);
  assert.match(h, /✕ เกินเส้นตาย 18 ชม\./);
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
  assert.match(h, /07:00 JST → 12:00 ICT/);
  assert.match(h, /NN393 · Airbus A350-900/);
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

// ---- Task 7: พบตอนตรวจจอ 360×740 แผ่นปิดสูงเกินเพดาน 45% (แถบเล่น 2 แถว) ----
test('CSS V7: แผ่นมือถือตอนปิด แถบเล่นแถวเดียว (ซ่อนตัวนับ ปุ่มภาพรวมเหลือไอคอน)', () => {
  assert.match(css, /\.sheet:not\(\.open\) \.stage-ctrl\{[^}]*flex-wrap:nowrap/);
  assert.match(css, /\.sheet:not\(\.open\) \.stage-ctrl \.count\{display:none\}/);
  assert.match(css, /\.sheet:not\(\.open\) \.ov-btn\{[^}]*font-size:0/);
});

// ---- รีวิวทั้งสาขา: แก้ข้อสำคัญ ----
test('รีวิว: การ์ดลอยตอนแผ่นปิดตัดบรรทัด (ใครทำ 1 บรรทัด · ชื่อขั้น 2 บรรทัด) ไม่ให้ดันแถบเล่นตกจอเตี้ย', () => {
  assert.match(css, /\.sheet:not\(\.open\) \.sh-card \.eyebrow\{[^}]*-webkit-line-clamp:1/);
  assert.match(css, /\.sheet:not\(\.open\) \.sh-card \.step-title\{[^}]*-webkit-line-clamp:2/);
});
test('รีวิว: ทุกกฎที่ใช้ var(--glass) มีทางสำรองพื้นทึบ', () => {
  // รวมรายการ selector จากทุกบล็อกทางสำรอง (ทั้ง @supports not และ prefers-reduced-transparency ต้องมีชุดเดียวกัน)
  const pick = re => [...css.matchAll(re)].flatMap(m => m[1].split(',').map(x => x.trim()));
  const sup = pick(/@supports not \(\(backdrop-filter:blur\(1px\)\) or \(-webkit-backdrop-filter:blur\(1px\)\)\)\{([^{]+)\{background:var\(--surface\)\}\}/g);
  const red = pick(/@media \(prefers-reduced-transparency:reduce\)\{([^{]+)\{background:var\(--surface\)/g);
  assert.ok(sup.length && red.length, 'ไม่พบรายการทางสำรอง');
  const list = sup.filter(x => red.includes(x));
  const bare = css.replace(/\/\*[\s\S]*?\*\//g, '');   // ตัดคอมเมนต์ออกก่อนหา selector
  const users = [...bare.matchAll(/([^{}]+)\{[^}]*background:var\(--glass\)/g)].map(m => m[1].trim()).filter(s => s !== '.glass');
  for (const sel of users) for (const one of sel.split(',')) assert.ok(list.includes(one.trim()), 'ไม่มีทางสำรอง: ' + one.trim());
});
test('รีวิว: มือถือแนวนอน สถานีปัจจุบันไม่เป็นแคปซูลว่าง และยังมีเส้นเชื่อม', () => {
  const land = css.slice(css.indexOf('@media (max-height:500px) and (orientation:landscape){'));
  assert.match(land, /\.stn\.now button\{background:transparent;padding:2px 6px\}/);
  assert.match(land, /\.stn\.now::after\{display:block\}/);
  assert.match(land, /\.stn\.now\{flex:1 1 0\}/);
});
test('รีวิว: ที่จับลากไม่ใช่จุดโฟกัสซ้ำ โฟกัสกลับมาที่ปุ่มลูกศรหลังวาดใหม่', () => {
  const h = UI.renderSheetHead(L.newState(0), false);
  assert.match(h, /class="grab" data-act="sheet-grab"[^>]*tabindex="-1"[^>]*aria-hidden="true"/);
  assert.equal(count(h, /data-act="sheet"/g), 1);
});
test('รีวิว: หัวเมนูเหตุการณ์บนกระจกใช้สีตัวหนังสือหลัก (สีแดงอยู่ที่ขอบ/ไอคอน)', () => {
  assert.match(css, /\.risk-menu summary\{[^}]*color:var\(--text\)/);
});
