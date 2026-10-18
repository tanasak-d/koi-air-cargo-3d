import test from 'node:test';
import assert from 'node:assert/strict';
import { nextVersion, stampVersion, exportName } from '../tools/export.mjs';
import { readHtml } from './helpers/load.mjs';

// ไฟล์ส่งออกมีเลขรุ่นต่อท้าย V2, V3, ... (มาร์ชขอ 2026-10-18) — รุ่นแรกบน main ถือเป็น V1
test('nextVersion: ยังไม่มีไฟล์ส่งออก → V2; มี V2, V3 แล้ว → V4; ไม่สนชื่อไฟล์อื่น', () => {
  assert.equal(nextVersion([]), 2);
  assert.equal(nextVersion(['Koi_Air_Cargo_3D_V2.html', 'Koi_Air_Cargo_3D_V3.html', 'x.html']), 4);
  assert.equal(nextVersion(['Koi_Air_Cargo_3D_V10.html', 'Koi_Air_Cargo_3D_V9.html']), 11);
});

test('exportName: ชื่อไฟล์ส่งออกตามเลขรุ่น', () => {
  assert.equal(exportName(3), 'Koi_Air_Cargo_3D_V3.html');
});

test('stampVersion: เขียนเลขรุ่นลงหัวหน้าเว็บ ผู้ชมเห็นว่าเปิดรุ่นไหน', () => {
  const html = stampVersion(readHtml(), 5);
  assert.match(html, /<span id="app-version">V5<\/span>/);
  assert.doesNotMatch(html, /<span id="app-version">dev<\/span>/);
});
