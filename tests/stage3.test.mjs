// design-pipeline Stage 3 (ทางเลือก C): แผงขวาจอคอมเป็นแท็บ · วิธีใช้เป็นปุ่ม ? · โหมดนำเสนอแบบ V7
import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']);
const UI = ctx.KoiUI, L = ctx.KoiLogic;
const html = readHtml();
const css = /<style>([\s\S]*?)<\/style>/.exec(html)[1];
const block = q => { const i = css.indexOf(q); assert.ok(i >= 0, 'ไม่พบ ' + q); let d = 0, j = css.indexOf('{', i); for (let k = j; k < css.length; k++) { if (css[k] === '{') d++; else if (css[k] === '}' && --d === 0) return css.slice(j, k); } };

test('จอคอม/แท็บเล็ต: แท็บในแผงขวา ซ่อนส่วนที่ไม่ได้เลือก และเลื่อนในกล่องเดียว', () => {
  const b = block('@media (min-width:768px) and (min-height:501px)');
  assert.match(b, /#sheet-tabs\{display:block\}/);
  assert.match(b, /\.panel-inner\{[^}]*overflow:auto/);
  assert.match(b, /\.panel-inner #facts,\.panel-inner #timeline\{[^}]*overflow:visible/);
  assert.match(b, /\.panel\[data-tab="route"\] #facts/);
  assert.match(b, /\.panel:not\(\[data-tab="route"\]\) #timeline\{display:none\}/);
  assert.match(b, /\.panel\[data-tab="risk"\] \.sheet-risk\{display:block\}/);
});

test('แท็บมี tabpanel ผูกกัน (aria-controls) และใช้ชื่อเดิม 3 แท็บ', () => {
  const t = UI.renderSheetTabs('route');
  assert.equal((t.match(/role="tab"/g) || []).length, 3);
  assert.match(t, /aria-controls="panel-body"/);
  assert.match(t, /aria-selected="true">เส้นทาง 17 ขั้น/);
  assert.match(html, /id="panel-body"[^>]*role="tabpanel"/);
});

test('วิธีใช้: ปุ่ม ? บนแถบบนเปิดป๊อปโอเวอร์ (ไม่ใช่ details ยาวใต้แถบบนแล้ว)', () => {
  assert.doesNotMatch(html, /<details class="card howto">/);
  assert.match(html, /<button id="help-btn"[^>]*data-act="help"[^>]*aria-expanded="false"[^>]*aria-controls="howto"/);
  assert.match(html, /<div id="howto" class="card howto"[^>]*role="dialog"[^>]*hidden>/);
  assert.equal(UI.keyToAction('?'), 'help');
  assert.match(css, /\.howto\{[^}]*position:fixed/);
});

test('โหมดนำเสนอ V7: แคปซูลเวลา + ชิปถุง + ป้าย Handover ในขั้นส่งมอบ · ตัวหนาไม่เกิน 600', () => {
  const S = L.newState(0);
  L.goTo(S, 5); // ขั้น 6 = HP1
  const h = UI.renderPresentSide(S);
  assert.match(h, /class="p-chips"/);
  assert.match(h, /class="chip[^"]*">[^<]*<svg/);         // แคปซูลเวลา
  assert.match(h, /ถุง \d/);                               // ชิปถุง
  assert.match(h, /class="p-hp"[\s\S]*HP1/);               // ป้ายจุดส่งมอบ
  const S2 = L.newState(0); L.goTo(S2, 1);
  assert.doesNotMatch(UI.renderPresentSide(S2), /class="p-hp"/);
  const pcss = css.split('\n').filter(l => /present-side|\.p-|big-facts|present-foot/.test(l)).join('\n');
  assert.doesNotMatch(pcss, /font-weight:(700|800|900)/);
});
