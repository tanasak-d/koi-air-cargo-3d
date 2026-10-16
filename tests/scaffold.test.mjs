import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml } from './helpers/load.mjs';

test('โหลดบล็อก koi-data ได้ และ KoiData เป็น object', () => {
  const ctx = loadBlocks(['koi-data']);
  assert.equal(typeof ctx.KoiData, 'object');
});

test('ฝัง Three.js ไว้ในไฟล์ (ใหญ่กว่า 500,000 ตัวอักษร)', () => {
  const html = readHtml();
  const m = /<script id="three">([\s\S]*?)<\/script>/.exec(html);
  assert.ok(m, 'ไม่พบ <script id="three">');
  assert.ok(m[1].length > 500000);
});

test('ไม่อ้างทรัพยากรภายนอก (ออฟไลน์ได้)', () => {
  const html = readHtml();
  assert.doesNotMatch(html, /(src|href)\s*=\s*["']https?:/);
  assert.doesNotMatch(html, /\bimport\(/);
  assert.doesNotMatch(html.replace(/<script id="three">[\s\S]*?<\/script>/, ''), /\bfetch\(/);
});
