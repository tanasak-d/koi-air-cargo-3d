import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

const html = readHtml();
const css = /<style>([\s\S]*?)<\/style>/.exec(html)[1];

// ---- ช่วยอ่านสีและคำนวณอัตราส่วนความต่างตามสูตร WCAG ----
function tokens(block) {
  const out = {};
  for (const m of block.matchAll(/--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\s*;/g)) out[m[1]] = m[2];
  return out;
}
function lum(hex) {
  const c = [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map(v => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function ratio(a, b) {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
}

// หาบล็อก CSS ตามหัวข้อ selector (ไม่ซ้อน)
function rule(sel) {
  const i = css.indexOf(sel + '{');
  if (i < 0) throw new Error('ไม่พบกฎ CSS: ' + sel);
  return css.slice(i + sel.length + 1, css.indexOf('}', i));
}
const light = tokens(rule(':root'));
const darkAuto = tokens(rule(':root:not([data-theme="light"])'));
const darkManual = tokens(rule(':root[data-theme="dark"]'));

test('มีธีมมืดทั้งแบบตามระบบ (prefers-color-scheme) และแบบสลับเอง และค่าตรงกัน', () => {
  assert.match(css, /@media\s*\(prefers-color-scheme:\s*dark\)/);
  assert.deepEqual(darkAuto, darkManual);
});

const PAIRS = [
  ['text', 'bg'], ['text', 'surface'], ['muted', 'bg'], ['muted', 'surface'],
  ['blue', 'surface'], ['blue', 'bg'], ['on-blue', 'blue'], ['on-pink', 'pink'],
  ['ok', 'surface'], ['warn', 'surface'], ['bad', 'surface']
];
for (const [name, set] of [['สว่าง', light], ['มืด', darkAuto]]) {
  test('ธีม' + name + ': ทุกคู่สีตัวอักษรผ่าน WCAG AA (>= 4.5:1)', () => {
    for (const [fg, bg] of PAIRS) {
      assert.ok(set[fg] && set[bg], `ขาดโทเคน ${fg}/${bg}`);
      const r = ratio(set[fg], set[bg]);
      assert.ok(r >= 4.5, `${fg} บน ${bg} = ${r.toFixed(2)} ต่ำกว่า 4.5`);
    }
  });
}

test('คลาสสถานะ (.st-ok/.st-warn/.st-bad) ไม่ใช้สีชมพู', () => {
  for (const c of ['.st-ok', '.st-warn', '.st-bad']) {
    assert.doesNotMatch(rule(c), /--pink|on-pink/, c);
  }
});

test('ไม่มีการเลื่อนแนวนอน: ใช้ overflow-wrap กับข้อความไทยและ min-width:0 ในกริด', () => {
  assert.match(css, /overflow-wrap:\s*anywhere/);
  assert.match(css, /min-width:\s*0/);
});

// ---- initTheme / toggleTheme ใช้ stub เพื่อทดสอบโดยไม่ต้องมีเบราว์เซอร์ ----
const UI = loadBlocks(['koi-data', 'koi-logic', 'koi-ui']).KoiUI;
function fakeEnv({ saved = null, systemDark = false, throwing = false } = {}) {
  const attrs = {};
  const store = {};
  return {
    attrs, store,
    doc: { documentElement: {
      setAttribute: (k, v) => { attrs[k] = v; },
      removeAttribute: k => { delete attrs[k]; },
      getAttribute: k => (k in attrs ? attrs[k] : null)
    } },
    storage: {
      getItem: () => { if (throwing) throw new Error('blocked'); return saved; },
      setItem: (k, v) => { if (throwing) throw new Error('blocked'); store[k] = v; }
    },
    matchMedia: () => ({ matches: systemDark })
  };
}

test('initTheme: ใช้ค่าที่บันทึกไว้ ถ้าไม่มีให้ตามระบบ (ไม่ตั้ง data-theme)', () => {
  const a = fakeEnv({ saved: 'dark' }); UI.initTheme(a);
  assert.equal(a.attrs['data-theme'], 'dark');
  const b = fakeEnv({ saved: null }); UI.initTheme(b);
  assert.equal('data-theme' in b.attrs, false);
});

test('toggleTheme: สลับสว่าง/มืด จากสถานะที่เห็นอยู่ และบันทึกค่า', () => {
  const e = fakeEnv({ systemDark: true });        // ระบบมืด ยังไม่เคยเลือก
  assert.equal(UI.toggleTheme(e), 'light');        // สลับเป็นสว่าง
  assert.equal(e.attrs['data-theme'], 'light');
  assert.equal(e.store['koi-theme'], 'light');
  assert.equal(UI.toggleTheme(e), 'dark');
});

test('localStorage ถูกบล็อก: ธีมยังทำงาน ไม่ throw', () => {
  const e = fakeEnv({ throwing: true });
  assert.doesNotThrow(() => UI.initTheme(e));
  assert.doesNotThrow(() => UI.toggleTheme(e));
  assert.ok(e.attrs['data-theme']);
});
