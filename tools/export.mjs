// ส่งออกไฟล์สำหรับเปิดดู/ส่งงาน พร้อมเลขรุ่น: Koi_Air_Cargo_3D_V2.html, _V3.html, ... (เลขขึ้นเองทุกครั้งที่รัน)
// วิธีใช้:  npm run export
// - ไฟล์ทำงานหลักยังเป็น Koi_Air_Cargo_3D.html (เทสต์ทั้งหมดตรวจไฟล์นี้)
// - ไฟล์ส่งออกไปอยู่ในโฟลเดอร์ exports/ และเขียนเลขรุ่นไว้ที่หัวหน้าเว็บ (ผู้ชมเห็นว่าเปิดรุ่นไหน)
// - รุ่นแรกที่อยู่บนสาขา main ถือเป็น V1 จึงเริ่มนับที่ V2
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const BASE = 'Koi_Air_Cargo_3D';

/** เลขรุ่นถัดไป จากรายชื่อไฟล์ที่มีอยู่ (เลขมากสุด + 1, อย่างน้อย 2) */
export function nextVersion(names) {
  let max = 1;
  for (const n of names) {
    const m = new RegExp('^' + BASE + '_V(\\d+)\\.html$').exec(n);
    if (m) max = Math.max(max, Number(m[1]));
  }
  return max + 1;
}

/** ชื่อไฟล์ส่งออกของรุ่น n */
export function exportName(n) { return BASE + '_V' + n + '.html'; }

/** ใส่เลขรุ่นลงในหน้าเว็บ (แทนคำว่า dev ใน <span id="app-version">) */
export function stampVersion(html, n) {
  return html.replace(/<span id="app-version">[^<]*<\/span>/, () => '<span id="app-version">V' + n + '</span>');
}

// รันเป็นคำสั่ง (ไม่ใช่ตอนเทสต์ import)
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const outDir = path.join(root, 'exports');
  fs.mkdirSync(outDir, { recursive: true });
  const n = nextVersion(fs.readdirSync(outDir));
  const html = stampVersion(fs.readFileSync(path.join(root, BASE + '.html'), 'utf8'), n);
  const out = path.join(outDir, exportName(n));
  fs.writeFileSync(out, html);
  console.log('ส่งออกแล้ว:', out, '(' + (Buffer.byteLength(html) / 1024 / 1024).toFixed(2) + ' MB)');
}
