import test from 'node:test';
import assert from 'node:assert/strict';
import { clipRing, simplify, BBOX } from '../tools/build-map.mjs';

// เครื่องมือสร้างแผนที่ (tools/build-map.mjs)
test('clipRing: ตัดรูปหลายเหลี่ยมที่ล้นกรอบให้อยู่ในกรอบ', () => {
  const sq = [[80, 10], [100, 10], [100, 20], [80, 20]];          // ยื่นออกทางซ้ายของกรอบ (lon0 = 86)
  const c = clipRing(sq, BBOX);
  assert.ok(c.length >= 4);
  for (const [x, y] of c) assert.ok(x >= BBOX.lon0 - 1e-9 && x <= BBOX.lon1 && y >= BBOX.lat0 && y <= BBOX.lat1);
  assert.deepEqual(clipRing([[0, 0], [1, 0], [1, 1]], BBOX), []); // อยู่นอกกรอบทั้งรูป
});

test('simplify: ตัดจุดที่อยู่บนเส้นตรงทิ้ง แต่เก็บมุมไว้', () => {
  const line = [[0, 0], [1, 0.001], [2, 0], [3, 0], [3, 3]];
  const s = simplify(line, 0.05);
  assert.deepEqual(s, [[0, 0], [3, 0], [3, 3]]);
});
