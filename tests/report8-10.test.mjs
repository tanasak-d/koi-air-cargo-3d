// ข้อมูลหัวข้อ 8–10 ของรายงานรวมเล่ม (Handover 5 จุด 6 Interface · 8 ฝ่าย SOP/KPI · Risk Register 12 ข้อ)
// แผนภาพสรุป Handover ของมาร์ช: Shipper → FF → Origin GHA (NRT) → Airline → Destination GHA (BKK) → Customs & DOF → Consignee
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

const D = JSON.parse(JSON.stringify(loadBlocks(['koi-data']).KoiData));

test('Handover 5 จุด = 6 Interface ตามลำดับ HP1 HP2 HP3 HP4 HP5A HP5B', () => {
  assert.deepEqual(D.HANDOVERS.map(h => h.id), ['HP1', 'HP2', 'HP3', 'HP4', 'HP5A', 'HP5B']);
});
test('Handover แต่ละจุดเชื่อมฝ่ายต่อกันเป็นสาย และผูกกับขั้นในเว็บ', () => {
  const ids = D.ACTORS.map(a => a.id);
  for (const h of D.HANDOVERS) {
    for (const k of ['from', 'to']) for (const a of h[k]) assert.ok(ids.includes(a), h.id + ' ' + a);
    assert.ok(Number.isInteger(h.step) && h.step >= 0 && h.step < 17, h.id);
    for (const f of ['i', 'd', 'p', 'r']) assert.ok(h.flows[f] && h.flows[f].length > 0, h.id + ' flow ' + f);
    assert.ok(h.risk && h.risk.name && h.evidence.length >= 3, h.id);
  }
  assert.deepEqual(D.HANDOVERS.map(h => h.step), [5, 6, 7, 9, 10, 11]);
  assert.deepEqual(D.HANDOVERS.map(h => h.from.join('+') + '>' + h.to.join('+')),
    ['shipper>ff', 'ff>gha_nrt', 'gha_nrt>airline', 'airline>gha_bkk', 'gha_bkk>customs+dof', 'customs+dof>consignee']);
});
test('8 ฝ่ายตามแผนภาพ: ต้นทาง 1–4 · ปลายทาง 4–8 · ชื่อสมมติตามรายงาน', () => {
  assert.deepEqual(D.ACTORS.map(a => a.id), ['shipper', 'ff', 'gha_nrt', 'airline', 'gha_bkk', 'customs', 'dof', 'consignee']);
  assert.match(D.ACTORS[0].name, /Lucky Koi House/);
  assert.match(D.ACTORS[3].name, /No Fish No Fly/);
  assert.match(D.ACTORS[7].name, /Wasana Tongsuk/);
  for (const a of D.ACTORS) {
    assert.ok(a.sop.length >= 2, a.id + ' SOP');
    assert.ok(a.kpi.length >= 1, a.id + ' KPI');
  }
});
test('Risk Register 12 ข้อ: คะแนน = L × S และระดับตรงคะแนน', () => {
  assert.equal(D.RISKS.length, 12);
  for (const r of D.RISKS) {
    assert.equal(r.score, r.l * r.s, 'ข้อ ' + r.no);
    assert.equal(r.level, r.score >= 15 ? 'สูง' : r.score >= 8 ? 'กลาง' : 'ต่ำ', 'ข้อ ' + r.no);
  }
  assert.deepEqual(D.RISKS.filter(r => r.level === 'สูง').map(r => r.no), [3, 8]);
});
test('ทุก KPI ที่อ้าง Risk Register ชี้ไปข้อที่มีอยู่จริง', () => {
  for (const a of D.ACTORS) for (const k of a.kpi) for (const n of (k.risk || [])) assert.ok(n >= 1 && n <= 12, a.id + ' ' + n);
});

// ---- แสดง Handover ในขั้นที่เกิดการส่งมอบ ----
const U = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = U.KoiUI, L = U.KoiLogic;
test('renderHandover: ขั้นที่ไม่มีการส่งมอบคืนค่าว่าง', () => {
  const S = L.newState(0); L.goTo(S, 2);
  assert.equal(UI.renderHandover(S), '');
});
test('renderHandover: ขั้น 7 (index 6) = Handover 2 Koi Express → Sakura Scale พร้อม 4 Flows ความเสี่ยงหลัก และหลักฐาน', () => {
  const S = L.newState(0); L.goTo(S, 6);
  const h = UI.renderHandover(S);
  assert.match(h, /^<details class="handover"/);
  assert.match(h, /Handover 2/);
  assert.match(h, /Koi Express Logistics[\s\S]*?→[\s\S]*?Sakura Scale Ground Services/);
  for (const w of ['Information', 'Document', 'Physical', 'Responsibility']) assert.match(h, new RegExp(w));
  assert.match(h, /ความเสี่ยงสำคัญ/);
  assert.match(h, /หลักฐานที่ต้องมี/);
  assert.match(h, /Risk Register ข้อ 5/);
});
test('renderHandover: ขั้น 11 (index 10) = 5A ส่งให้ศุลกากรและกรมประมงพร้อมกัน', () => {
  const S = L.newState(0); L.goTo(S, 10);
  assert.match(UI.renderHandover(S), /Handover 5A[\s\S]*?Golden Scale[\s\S]*?ศุลกากร[\s\S]*?กรมประมง/);
});
test('renderFacts รวมการ์ด Handover · เช็กลิสต์มีป้าย HP ที่ขั้นส่งมอบ 6 แถว', () => {
  const S = L.newState(0); L.goTo(S, 5);
  assert.match(UI.renderFacts(S), /class="handover"/);
  const c = UI.renderChecklist(S);
  assert.equal((c.match(/class="hp-tag"/g) || []).length, 6);
  assert.match(c, /data-step="9"[\s\S]*?class="hp-tag">HP4</);
});

// ---- ฉาก 3 มิติ: กล่อง 10 ใบตามรายงาน (1 ตัว : 1 ถุง : 1 กล่อง) ----
import { readHtml, blockSource } from './helpers/load.mjs';
test('ข้อมูลกลาง: กล่อง 10 ใบ และฉาก 3 มิติสร้างกล่องตามจำนวนนี้ (ไม่วางซ้อน)', () => {
  assert.equal(D.CONST.BOXES, 10);
  const scene = blockSource(readHtml(), 'koi-scene');
  assert.match(scene, /function makeBoxSet\(/);
  assert.match(scene, /D\.CONST\.BOXES/);
  assert.match(scene, /kit\.fishBox\(\)[\s\S]{0,80}makeBoxSet|makeBoxSet\(\)/);
});

// ---- รายงานรวมเล่ม v1_2 (8 พ.ย.) ----
const docsOf = n => D.STEPS[n - 1].docs.join(' | ');
const actor = id => D.ACTORS.find(a => a.id === id);
test('v1_2: สายการบินเป็นผู้ออก MAWB · Forwarder จองและส่งข้อมูล แล้วตรวจ MAWB', () => {
  assert.match(docsOf(8), /MAWB \(สายการบินออก/);
  assert.doesNotMatch(JSON.stringify(D), /ออกโดย Koi Express Logistics/);
  assert.match(actor('airline').duty, /^ออก MAWB/);
  assert.match(actor('ff').duty, /ส่งข้อมูลให้สายการบินออก MAWB/);
  assert.match(actor('ff').sop.join(' '), /ตรวจ MAWB ที่สายการบินออก/);
  const g = D.GLOSSARY.find(x => x.term === 'MAWB');
  assert.match(g.plain, /สายการบินเป็นผู้ออก/);
});
test('v1_2: Ground Handler ทั้งสองสนามบินเป็นผู้รับจ้างของสายการบิน', () => {
  for (const id of ['gha_nrt', 'gha_bkk']) assert.match(actor(id).role, /ผู้รับจ้างของสายการบิน/);
  assert.match(D.STEPS[6].who, /ผู้รับจ้างของสายการบิน/);
  assert.match(D.STEPS[9].who, /ผู้รับจ้างของสายการบิน/);
});
test('v1_2: สายการบินอยู่ทั้งต้นทาง กลางทาง และปลายทาง', () => {
  assert.equal(actor('airline').side, 'all');
});
test('v1_2: ที่ BKK ศุลกากรประเมินและเก็บภาษีก่อน (12:50–13:30) แล้วส่งต่อกรมประมงตรวจ (13:30–14:30) ผ่านแล้วปล่อย', () => {
  const s11 = D.STEPS[10].what;
  assert.ok(s11.indexOf('ประเมิน') < s11.indexOf('ส่งต่อ'), s11);
  assert.match(s11, /12:50–13:30 ICT/);
  assert.match(s11, /13:30–14:30 ICT/);
  assert.match(actor('customs').sop.join(' '), /12:50–13:30 ICT/);
  assert.match(actor('dof').sop.join(' '), /13:30–14:30 ICT/);
  assert.match(D.HANDOVERS[4].flows.r, /ศุลกากรประเมินภาษีก่อน แล้วส่งต่อกรมประมงตรวจ/);
});
