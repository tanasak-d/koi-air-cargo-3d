// ตัวช่วยทดสอบ: ดึงโค้ดจากบล็อก <script id="..."> ในไฟล์ HTML ไปรันใน Node
// ทำไมต้องทำแบบนี้: ไฟล์งานเป็น HTML ไฟล์เดียว ไม่มีขั้นตอน build
// เราเลยอ่านไฟล์จริงแล้วรันเฉพาะส่วนตรรกะ (ไม่แตะ DOM) เพื่อทดสอบ
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
export const HTML_PATH = path.resolve(here, '../../Koi_Air_Cargo_3D.html');

/** อ่านไฟล์ HTML ทั้งไฟล์เป็นสตริง */
export function readHtml() {
  return fs.readFileSync(HTML_PATH, 'utf8');
}

/** คืนโค้ดในบล็อก <script id="id"> (สตริงว่างถ้าไม่มี) */
export function blockSource(html, id) {
  const re = new RegExp('<script id="' + id + '">([\\s\\S]*?)</script>');
  const m = re.exec(html);
  if (!m) throw new Error('ไม่พบบล็อก script id=' + id);
  return m[1];
}

/** รันบล็อกตามลำดับ id ใน context เดียว แล้วคืน context (อ่าน ctx.KoiData / ctx.KoiLogic ได้) */
export function loadBlocks(ids) {
  const html = readHtml();
  const ctx = vm.createContext({ console, atob, TextDecoder }); // atob ใช้ถอดรหัสโมเดลที่ฝังเป็น base64
  for (const id of ids) vm.runInContext(blockSource(html, id), ctx, { filename: id });
  return ctx;
}
