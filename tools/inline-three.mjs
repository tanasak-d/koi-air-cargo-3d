// ฝัง Three.js ลงในไฟล์ HTML (รันซ้ำได้ ไม่ฝังซ้ำ)
// ทำไมใช้ฟังก์ชันเป็นตัวแทนที่: โค้ด minified มีเครื่องหมาย $ ซึ่งถ้าใช้สตริงตรง ๆ
// String.replace จะตีความ $& $1 ผิดและทำให้โค้ดพัง
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.resolve(here, '../Koi_Air_Cargo_3D.html');
const threePath = 'C:/Users/tanas/projects/don-mueang-apron/node_modules/three/build/three.min.js';

let html = fs.readFileSync(htmlPath, 'utf8');
const three = fs.readFileSync(threePath, 'utf8');
const block = '<script id="three">' + three + '</script>';

if (html.includes('<script id="three">')) {
  // มีอยู่แล้ว: แทนที่บล็อกเดิม
  html = html.replace(/<script id="three">[\s\S]*?<\/script>/, () => block);
} else {
  html = html.replace('<!--THREE-->', () => block);
}
fs.writeFileSync(htmlPath, html);
console.log('ฝัง Three.js แล้ว', three.length, 'ตัวอักษร');
