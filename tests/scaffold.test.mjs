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

// ---- Task 12: ตรวจไฟล์ที่ส่งออกทั้งไฟล์ ----
const noThree = (html) => html.replace(/<script id="three">[\s\S]*?<\/script>/, '');

test('ส่งออก: ไม่มี URL ภายนอกในโค้ดของเรา (ยกเว้นข้อความใน Three.js ที่ฝังไว้)', () => {
  const ours = noThree(readHtml());
  assert.doesNotMatch(ours, /https?:\/\//);
});

test('ส่งออก: ขนาดไฟล์ไม่เกิน 2 MB', () => {
  assert.ok(Buffer.byteLength(readHtml(), 'utf8') <= 2 * 1024 * 1024);
});

test('ส่งออก: มี lang="th" และ <title> 2–4 คำ', () => {
  const html = readHtml();
  assert.match(html, /<html lang="th">/);
  const t = /<title>([^<]+)<\/title>/.exec(html)[1].trim();
  const words = t.split(/\s+/).length;
  assert.ok(words >= 2 && words <= 4, 'title: ' + t);
});

test('ส่งออก: ไม่มีคำต้องห้ามของที่ล็อกไว้ในไฟล์ (ทั้งไฟล์ ไม่นับ Three.js)', () => {
  const ours = noThree(readHtml());
  assert.doesNotMatch(ours, /(21|30\s*[-–]\s*35|60)\s*วัน/);
  assert.doesNotMatch(ours, /ความไวต่ออัตรารอด/);
  assert.doesNotMatch(ours, /หัวข้อ\s*6/);
});

test('ส่งออก: ไม่มี console.log / debugger หลงเหลือในโค้ดของเรา', () => {
  const ours = noThree(readHtml());
  assert.doesNotMatch(ours, /console\.log\(/);
  assert.doesNotMatch(ours, /\bdebugger\b/);
});

test('ส่งออก: ทุกบล็อกที่ควรมีอยู่ครบ และ koi-boot อยู่หลังบล็อกอื่น', () => {
  const html = readHtml();
  const ids = ['three', 'koi-data', 'koi-logic', 'koi-ui', 'koi-scene', 'koi-boot'];
  const pos = ids.map(id => html.indexOf('<script id="' + id + '">'));
  pos.forEach((p, i) => assert.ok(p > 0, 'ไม่พบ ' + ids[i]));
  for (let i = 1; i < pos.length; i++) assert.ok(pos[i] > pos[i - 1], ids[i] + ' ต้องอยู่หลัง ' + ids[i - 1]);
});

test('ส่งออก: หน้าแรกมีข้อความบอกวิธีใช้สั้น ๆ', () => {
  assert.match(readHtml(), /วิธีใช้/);
});

test('ส่งออก: ไม่เหลือข้อความเพดาน 21 ชม. เดิม (เปลี่ยนเป็น 24 ชม. แล้ว)', () => {
  assert.doesNotMatch(noThree(readHtml()), /21\s*ชม/);
});
