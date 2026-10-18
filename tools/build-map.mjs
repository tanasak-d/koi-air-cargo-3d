// สร้างแผนที่เอเชีย (ญี่ปุ่น → ไทย) สำหรับฉากเส้นทางบินในขั้น 9 จากข้อมูล Natural Earth (สาธารณสมบัติ)
// อ่าน spike/assets-raw/naturalearth/ne_50m_admin_0_countries.geojson (ไม่เก็บลง git)
// → ตัดเฉพาะกรอบเอเชียตะวันออก/ตะวันออกเฉียงใต้ + ลดจำนวนจุดของเส้น → assets/map/asia.json (เล็ก ฝังลงไฟล์เว็บได้)
// วิธีใช้:  node tools/build-map.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
export const BBOX = { lon0: 86, lon1: 150, lat0: -2, lat1: 48 };   // กรอบแผนที่ (องศา)

// ตัดรูปหลายเหลี่ยมให้อยู่ในกรอบสี่เหลี่ยม (วิธี Sutherland–Hodgman ตัดทีละด้าน)
export function clipRing(ring, b) {
  const edges = [
    [p => p[0] >= b.lon0, (p, q) => cut(p, q, 0, b.lon0)],
    [p => p[0] <= b.lon1, (p, q) => cut(p, q, 0, b.lon1)],
    [p => p[1] >= b.lat0, (p, q) => cut(p, q, 1, b.lat0)],
    [p => p[1] <= b.lat1, (p, q) => cut(p, q, 1, b.lat1)]
  ];
  let out = ring;
  for (const [inside, inter] of edges) {
    const src = out; out = [];
    for (let i = 0; i < src.length; i++) {
      const p = src[i], q = src[(i + 1) % src.length];
      if (inside(p)) { out.push(p); if (!inside(q)) out.push(inter(p, q)); }
      else if (inside(q)) out.push(inter(p, q));
    }
    if (!out.length) return [];
  }
  return out;
}
function cut(p, q, axis, v) {
  const t = (v - p[axis]) / (q[axis] - p[axis]);
  return [p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t];
}

// ลดจำนวนจุดของเส้น (Douglas–Peucker): ตัดจุดที่เบี่ยงจากเส้นตรงน้อยกว่า tol องศา
export function simplify(pts, tol) {
  if (pts.length < 4) return pts;
  const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1;
  const stack = [[0, pts.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop(); let best = -1, idx = -1;
    for (let i = a + 1; i < b; i++) {
      const d = segDist(pts[i], pts[a], pts[b]);
      if (d > best) { best = d; idx = i; }
    }
    if (best > tol) { keep[idx] = 1; stack.push([a, idx], [idx, b]); }
  }
  return pts.filter((_, i) => keep[i]);
}
function segDist(p, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = dx * dx + dy * dy;
  const t = L ? Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L)) : 0;
  return Math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const src = path.join(root, 'spike/assets-raw/naturalearth/ne_50m_admin_0_countries.geojson');
  const geo = JSON.parse(fs.readFileSync(src, 'utf8'));
  const countries = [];
  for (const f of geo.features) {
    const g = f.geometry; if (!g) continue;
    const polys = g.type === 'Polygon' ? [g.coordinates] : g.type === 'MultiPolygon' ? g.coordinates : [];
    const rings = [];
    for (const poly of polys) {
      const outer = poly[0];                                      // ใช้เฉพาะขอบนอก (ไม่ต้องมีรูทะเลสาบ)
      const c = clipRing(outer.slice(0, -1), BBOX);
      if (c.length < 3) continue;
      const s = simplify(c, 0.12);
      if (s.length < 3) continue;
      rings.push(s.map(([x, y]) => [Math.round(x * 100) / 100, Math.round(y * 100) / 100]));
    }
    if (rings.length) countries.push({ a3: f.properties.ADM0_A3, name: f.properties.NAME, rings });
  }
  const out = path.join(root, 'assets/map/asia.json');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({ bbox: BBOX, source: 'Natural Earth 1:50m Admin 0 Countries (public domain)', countries }));
  console.log('แผนที่:', countries.length, 'ประเทศ ·', fs.statSync(out).size, 'ไบต์ →', out);
}
