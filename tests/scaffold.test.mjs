import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks, readHtml, blockSource } from './helpers/load.mjs';

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
// ตัดบล็อกที่ฝังจากภายนอก (Three.js, addons, โมเดล) ออก เหลือเฉพาะโค้ดของเรา
const noThree = (html) => html.replace(/<script id="(three|three-addons|koi-assets)">[\s\S]*?<\/script>/g, '');

test('ส่งออก: ไม่มี URL ภายนอกในโค้ดของเรา (ยกเว้นข้อความใน Three.js ที่ฝังไว้)', () => {
  const ours = noThree(readHtml());
  assert.doesNotMatch(ours, /https?:\/\//);
});

// มาร์ชขยายเพดานจาก 3 MB เป็น 5 MB (2026-10-18) เพื่อให้ใส่โมเดลจาก Blender ได้มากขึ้น
test('ส่งออก: ขนาดไฟล์ไม่เกิน 5 MB', () => {
  assert.ok(Buffer.byteLength(readHtml(), 'utf8') <= 5 * 1024 * 1024);
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
  assert.doesNotMatch(ours, /(?<!อย่างน้อย )21\s*วัน|30\s*[-–]\s*35\s*วัน|60\s*วัน/);
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
  const ids = ['three', 'three-addons', 'koi-assets', 'koi-data', 'koi-logic', 'koi-ui', 'koi-scene', 'koi-boot'];
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

// ---- รุ่น 2 Task 1: ฝัง addons และโมเดลลงไฟล์เดียว ----
test('ฝัง addons: GLTFLoader และ OrbitControls อยู่ในบล็อก three-addons', () => {
  const src = blockSource(readHtml(), 'three-addons');
  assert.match(src, /class GLTFLoader extends THREE\.Loader/);
  assert.match(src, /OrbitControls/);
});

test('ฝังโมเดล: KoiAssets มีโมเดล 4 ตัวที่ถอดรหัสแล้วขึ้นต้นด้วย glTF และมี colormap', () => {
  const ctx = loadBlocks(['koi-assets']);
  for (const n of ['delivery', 'van', 'tractor', 'cone', 'airliner', 'koi', 'person', 'fishbox', 'bag', 'warehouse', 'xray', 'pond', 'dolly', 'farmhouse', 'dof', 'trees', 'reefer', 'japan', 'thai']) {
    const head = Buffer.from(ctx.KoiAssets.models[n], 'base64').subarray(0, 4).toString('latin1');
    assert.equal(head, 'glTF', n);
  }
  assert.match(ctx.KoiAssets.textures.colormap, /^data:image\/png;base64,/);
});

// ---- รุ่น 2 Task 5: เลย์เอาต์ B ----
test('เลย์เอาต์ B: มีเวที (การ์ดลอย ปุ่มบนโมเดล เมนูเหตุการณ์) และเส้นเวลา; ไม่เหลือแถบสถานี/แผงขั้นตอนเดิม', () => {
  const html = readHtml();
  for (const id of ['stage', 'card', 'stage-ctrl', 'risk', 'timeline', 'facts']) assert.match(html, new RegExp('id="' + id + '"'), id);
  for (const id of ['strip', 'steps', 'controls']) assert.doesNotMatch(html, new RegExp('id="' + id + '"'), id);
});

test('เลย์เอาต์ B: วิธีใช้บอกคีย์ลัดครบ (← → Space P T O)', () => {
  const how = /<div id="howto"[^>]*>([\s\S]*?)<\/div>/.exec(readHtml())[1];
  assert.match(how, /คีย์ลัด/);
  for (const k of ['←', '→', 'Space', 'P', 'T', 'O']) assert.ok(how.includes(k), k);
});

test('ไม่มี WebGL: การ์ดชื่อขั้นยังแสดงแบบคงที่ (มีสไตล์ #card.static)', () => {
  assert.match(readHtml(), /#card\.static\{[^}]*position:/);
});

test('เปลี่ยนสถานีแบบนุ่ม: ภาพจาง-ขึ้น (มี transition ของ opacity ที่ canvas)', () => {
  assert.match(readHtml(), /#stage canvas\{[^}]*transition:opacity/);
});

test('ฝังแผนที่: KoiAssets.map มีประเทศญี่ปุ่นและไทย (ข้อมูล Natural Earth)', () => {
  const ctx = loadBlocks(['koi-assets']);
  const a3 = ctx.KoiAssets.map.countries.map(c => c.a3);
  assert.ok(a3.includes('JPN') && a3.includes('THA'));
});

test('V4: มีแถบบน (สถานะการขนส่ง) แผงติดตามด้านข้าง และป้ายสถานีบนภาพ', () => {
  const html = readHtml();
  for (const id of ['topbar', 'status', 'panel', 'route']) assert.match(html, new RegExp('id="' + id + '"'), id);
});

// ---- รายงานรวมเล่ม 10 หัวข้อ: ไม่เหลือเที่ยวบินเดิมที่ไหนในหน้าเว็บ (แถบบน ฉาก 3 มิติ ป้าย) ----
test('ไม่เหลือข้อความเที่ยวบินเดิม JL707 / Boeing 787-8 / 18:25 ในไฟล์งาน', () => {
  const page = readHtml()
    .replace(/<script id="(three|three-addons|koi-assets)">[\s\S]*?<\/script>/g, '');
  assert.doesNotMatch(page, /JL707|787-8|18:25/);
});
