// ฝัง "ส่วนเสริมของ Three.js" และ "โมเดล 3 มิติ" ลงในไฟล์ HTML (รันซ้ำได้ ไม่ฝังซ้ำ)
// ทำไมต้องฝัง: มาร์ชเลือกให้ไฟล์ส่งมอบเป็นไฟล์เดียว ดับเบิลคลิกเปิดได้ (file://)
// ถ้าโมเดลเป็นไฟล์แยก เบราว์เซอร์จะไม่ยอมให้หน้าเว็บอ่านไฟล์จากดิสก์ โมเดลจะไม่ขึ้น
// วิธี: แปลงไฟล์ .glb / .png เป็นข้อความ base64 แล้วเก็บไว้ในตัวแปร KoiAssets
// ใช้ฟังก์ชันเป็นตัวแทนที่ใน replace เพราะโค้ด minified มีเครื่องหมาย $ (เหตุผลเดียวกับ inline-three.mjs)
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const htmlPath = path.join(root, 'Koi_Air_Cargo_3D.html');
const threeDir = 'C:/Users/tanas/projects/don-mueang-apron/node_modules/three/examples/js';
// รถ 3 แบบ + กรวย: Kenney Car Kit (CC0) · เครื่องบิน ปลาคาร์ฟ คน กล่องปลา ถุง คลังสินค้า X-ray: สร้างใน Blender ด้วยสคริปต์ใน tools/blender/
const MODELS = ['delivery', 'van', 'tractor', 'cone', 'airliner', 'koi', 'person', 'fishbox', 'bag', 'warehouse', 'xray'];

// ใส่บล็อกใหม่: ถ้ามีบล็อกเดิมอยู่แล้วให้แทนที่ ถ้ายังไม่มีให้แทนที่ตัวจองที่ (marker)
function put(html, id, marker, body) {
  const block = '<script id="' + id + '">' + body + '</script>';
  const re = new RegExp('<script id="' + id + '">[\\s\\S]*?</script>');
  if (re.test(html)) return html.replace(re, () => block);
  if (!html.includes(marker)) throw new Error('ไม่พบตัวจองที่ ' + marker);
  return html.replace(marker, () => block);
}

const addons = ['loaders/GLTFLoader.js', 'controls/OrbitControls.js']
  .map(f => fs.readFileSync(path.join(threeDir, f), 'utf8')).join('\n');

const models = {};
for (const n of MODELS) models[n] = fs.readFileSync(path.join(root, 'assets/models', n + '.glb')).toString('base64');
const colormap = 'data:image/png;base64,' +
  fs.readFileSync(path.join(root, 'assets/models/Textures/colormap.png')).toString('base64');
const assets = '\n// โมเดล Kenney Car Kit (CC0) แบบ base64 — สร้างโดย tools/inline-assets.mjs ห้ามแก้ด้วยมือ\n' +
  'var KoiAssets = ' + JSON.stringify({ models, textures: { colormap } }) + ';\n';

let html = fs.readFileSync(htmlPath, 'utf8');
html = put(html, 'three-addons', '<!--ADDONS-->', addons);
html = put(html, 'koi-assets', '<!--ASSETS-->', assets);
fs.writeFileSync(htmlPath, html);
console.log('ฝัง addons', addons.length, 'ตัวอักษร · โมเดล', MODELS.length, 'ไฟล์ · ไฟล์รวม', Buffer.byteLength(html), 'ไบต์');
