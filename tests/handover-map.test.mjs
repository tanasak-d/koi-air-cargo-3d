// แผนผัง Handover ในเว็บ (design-pipeline ทางเลือก C · design/03-decision.md)
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, D = ctx.KoiData;
const html = readHtml();
const css = /<style>([\s\S]*?)<\/style>/.exec(html)[1];
const count = (s, re) => (s.match(re) || []).length;
const hmCss = css.split('\n').filter(l => /\.hm-/.test(l)).join('\n');

test('แผนภาพ: 8 ฝ่าย 6 จุดส่งมอบ ตามลำดับภาพวาด และกลุ่มช่วงทางแนวนอน 3 กลุ่ม', () => {
  const h = UI.renderHmChain({ kind: 'hp', id: 'HP2' });
  assert.equal(count(h, /data-actor="/g), 8);
  assert.equal(count(h, /data-hp="/g), 6);
  const order = [...h.matchAll(/data-(actor|hp)="([^"]+)"/g)].map(m => m[2]).join(' ');
  assert.equal(order, 'shipper HP1 ff HP2 gha_nrt HP3 airline HP4 gha_bkk HP5A customs dof HP5B consignee');
  assert.equal(count(h, /class="hm-grp"/g), 3);
  assert.match(h, /ต้นทาง[\s\S]*?กลางทาง[\s\S]*?ปลายทาง/);
  assert.match(h, /ออก MAWB[\s\S]*?จัดทำ NOTOC/);
  assert.match(h, /data-hp="HP2"[^>]*aria-pressed="true"/);
  assert.equal(count(h, /aria-pressed="true"/g), 1);
});
test('รายละเอียดจุดส่งมอบ: ใครส่งให้ใคร · 4 Flows · ความเสี่ยงสำคัญ · หลักฐาน', () => {
  const h = UI.renderHmDetail({ kind: 'hp', id: 'HP5A' }, 'hp');
  assert.match(h, /Handover 5A/);
  for (const w of ['Information', 'Document', 'Physical', 'Responsibility']) assert.match(h, new RegExp(w));
  assert.match(h, /ความเสี่ยงสำคัญ/);
  assert.match(h, /หลักฐานที่ต้องมี/);
});
test('รายละเอียดฝ่าย: หน้าที่ · SOP ครบทุกข้อ · KPI พร้อมเป้าหมาย', () => {
  const a = D.ACTORS.find(x => x.id === 'airline');
  const h = UI.renderHmDetail({ kind: 'actor', id: 'airline' }, 'actor');
  assert.match(h, /No Fish No Fly Airline/);
  assert.equal(count(h, /<li>/g), a.sop.length);
  assert.equal(count(h, /<tr>/g), a.kpi.length);
  assert.match(h, /ต้นทาง กลางทาง และปลายทาง/);
});
test('Risk Register: 13 แถว ตัวเลข L × S = คะแนน + คำระดับ ไม่มีแถบคะแนนเล็ก', () => {
  const h = UI.renderHmDetail({ kind: 'hp', id: 'HP1' }, 'risk');
  assert.equal(count(h, /<tr data-risk=/g), 13);
  assert.match(h, /3 × 5 = 15/);
  assert.match(h, /สูง/);
  assert.doesNotMatch(h, /class="bar"/);
});
test('แท็บ 3 แท็บ เลือกอยู่มี aria-selected', () => {
  const h = UI.renderHmTabs('risk');
  assert.equal(count(h, /role="tab"/g), 3);
  assert.match(h, /data-ht="risk"[^>]*aria-selected="true"/);
});
test('สไตล์ตามที่มาร์ชเลือก: ป้าย HP เป็นตราประทับมุม 6 · ไม่มีตัวหนังสือแนวตั้ง · น้ำหนักไม่เกิน 600', () => {
  assert.match(css, /\.hm-hp\{[^}]*border-radius:6px[^}]*border:2px solid/);
  assert.doesNotMatch(hmCss, /writing-mode/);
  assert.doesNotMatch(hmCss, /font-weight:(700|800|900)/);
  assert.doesNotMatch(hmCss, /margin-left:-/);
});
test('หน้าต่างแผนผังอยู่ในหน้าเว็บ เปิดด้วยปุ่มบนแถบบน การ์ด HP และคีย์ H', () => {
  assert.match(html, /<div id="hmap" class="hmap" role="dialog" aria-modal="true" aria-labelledby="hm-title" hidden>/);
  assert.match(html, /id="hmap-btn"[^>]*data-act="hmap"/);
  assert.equal(UI.keyToAction('h'), 'hmap');
  assert.equal(UI.keyToAction('H'), 'hmap');
});
