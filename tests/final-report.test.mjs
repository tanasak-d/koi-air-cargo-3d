// ตรวจข้อมูลให้ตรงรายงานฉบับสมบูรณ์ของทีม (PDF APM33267 · 7 บท)
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, D = ctx.KoiData;
const docs = n => D.STEPS[n - 1].docs.join(' | ');

test('ใบรับรองสถานกักกันชื่อ ทรน.6 (ไม่ใช้ Tor.Ror.Nor.6 แล้ว)', () => {
  assert.match(docs(13), /ทรน\.6/);
  assert.doesNotMatch(readHtml(), /Tor\.Ror\.Nor/);
});

test('ชื่อโรคใช้ SVC ตามรายงาน (ไม่ใช้ SVCV)', () => {
  assert.doesNotMatch(readHtml(), /SVCV/);
  assert.match(docs(13), /SVC/);
});

test('กักกันอย่างน้อย 21 วัน และถอนกักเมื่อ DOF อนุญาต', () => {
  const s14 = D.STEPS[13];
  assert.match(s14.what, /อย่างน้อย 21 วัน/);
  assert.match(s14.tl, /21 วัน/);
});

test('Health Certificate ออกภายใน 10 วัน · ทะเบียนผู้ประกอบการ ทบ.2', () => {
  assert.match(docs(11), /Health Certificate[^|]*10 วัน/);
  assert.match(readHtml(), /ทบ\.2/);
});

test('Risk Register 13 ข้อ: ข้อ 13 น้ำรั่วลงพื้นระวาง L2 × S5 = 10 คงเหลือ 1×5=5', () => {
  assert.equal(D.RISKS.length, 13);
  const r = D.RISKS[12];
  assert.equal(r.no, 13);
  assert.match(r.name, /พื้นระวาง/);
  assert.equal(r.l * r.s, 10); assert.equal(r.score, 10); assert.equal(r.level, 'กลาง');
  assert.equal(r.res, '1×5=5');
  assert.match(r.ctrl, /NOTOC/);
});

test('ลำดับความสำคัญ 3 ระดับ: P1 = ข้อ 3, 8 · P3 = ข้อ 1, 2, 5, 9 · ที่เหลือ P2', () => {
  const by = p => Array.from(D.RISKS.filter(r => r.pri === p), r => r.no);
  assert.deepEqual(by(1), [3, 8]);
  assert.deepEqual(by(3), [1, 2, 5, 9]);
  assert.deepEqual(by(2), [4, 6, 7, 10, 11, 12, 13]);
});

test('ตารางความเสี่ยงในแผนผังแสดง 13 แถว และบอก Priority', () => {
  const h = UI.renderHmDetail({ kind: 'hp', id: 'HP1' }, 'risk');
  assert.equal((h.match(/<tr data-risk=/g) || []).length, 13);
  assert.match(h, /P1/);
  assert.match(UI.renderHmTabs('risk'), /Risk Register 13 ข้อ/);
});

test('ทุกข้อมีความเสี่ยงคงเหลือ (ข้อ 11 = 1×5=5 ตามตาราง 6.8)', () => {
  for (const r of D.RISKS) assert.match(r.res || '', /^\d×\d=\d+$/, 'ข้อ ' + r.no);
  assert.equal(D.RISKS[10].res, '1×5=5');
});
