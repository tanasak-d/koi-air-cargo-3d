import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

// คัดลอกผ่าน JSON เพื่อให้ deepEqual เทียบกับ array ของ Node ได้ (ข้อมูลจาก vm คนละ realm)
const D = JSON.parse(JSON.stringify(loadBlocks(['koi-data']).KoiData));

// รวมทุกสตริงในข้อมูล (ยกเว้น GLOSSARY) ไว้ตรวจคำต้องห้าม/คำที่ต้องมี
function leaves(x, out = []) {
  if (typeof x === 'string') out.push(x);
  else if (Array.isArray(x)) x.forEach(v => leaves(v, out));
  else if (x && typeof x === 'object') Object.values(x).forEach(v => leaves(v, out));
  return out;
}
const { GLOSSARY, ...rest } = D;
const texts = leaves(rest);
const all = texts.join('\n');

test('มี 17 ขั้น เรียง n = 1..17', () => {
  assert.equal(D.STEPS.length, 17);
  D.STEPS.forEach((s, i) => assert.equal(s.n, i + 1));
});

test('6 สถานีครอบขั้น 0..16 ต่อเนื่องไม่ซ้ำ ตามที่ล็อกไว้', () => {
  const got = D.STATIONS.map(s => [s.first, s.last]);
  assert.deepEqual(got, [[0, 5], [6, 7], [8, 8], [9, 9], [10, 13], [14, 16]]);
});

test('ค่าเที่ยวบินตรงกับที่ล็อก (JL707, 787-8, 18:25 JST → 23:00 ICT)', () => {
  assert.equal(D.CONST.FLIGHT.no, 'JL707');
  assert.equal(D.CONST.FLIGHT.type, 'Boeing 787-8');
  assert.equal(D.CONST.FLIGHT.depJST, '18:25');
  assert.equal(D.CONST.FLIGHT.arrICT, '23:00');
  assert.equal(D.STEPS[8].dep, 1105); // 18:25 JST = 1105 นาที
  assert.equal(D.STEPS[8].t[1] - D.CONST.JST_MINUS_ICT, 1380); // ลงจอด 23:00 ICT
});

test('ทุกขั้นมี who/what/why และ t===null ต้อง approx', () => {
  for (const s of D.STEPS) {
    for (const k of ['who', 'what', 'why', 'name', 'risk']) {
      assert.ok(typeof s[k] === 'string' && s[k].length > 0, `ขั้น ${s.n} ไม่มี ${k}`);
    }
    if (s.t === null) assert.equal(s.approx, true, `ขั้น ${s.n}`);
  }
});

test('WAYPOINTS ครบตามจำนวนขั้นของแต่ละสถานี และอยู่ในกรอบ [-10,10]', () => {
  D.STATIONS.forEach((st, i) => {
    assert.equal(D.WAYPOINTS[i].length, st.last - st.first + 1);
    for (const p of D.WAYPOINTS[i]) {
      assert.ok(Math.abs(p.x) <= 10 && Math.abs(p.z) <= 10);
    }
  });
});

test('ไม่มีคำต้องห้ามตามที่ล็อกไว้', () => {
  assert.doesNotMatch(all, /(21|30\s*[-–]\s*35|60)\s*วัน/);
  assert.doesNotMatch(all, /ความไวต่ออัตรารอด/);
  assert.doesNotMatch(all, /หัวข้อ\s*6/);
});

test('มี 1:2 และ Triple Bagging', () => {
  assert.match(all, /1:2/);
  assert.match(all, /Triple Bagging/);
});

test('ทุกข้อความที่พูดถึง NOTOC ต้องระบุว่าสายการบินเป็นผู้จัดทำ', () => {
  const bad = texts.filter(t => /NOTOC/.test(t) && !/สายการบิน/.test(t));
  assert.deepEqual(bad, []);
});

test('สถานการณ์ 6 แบบ และ 1–5 มีทางเลือกที่ถูกอย่างน้อยหนึ่ง', () => {
  assert.equal(D.SCENARIOS.length, 6);
  for (const sc of D.SCENARIOS.slice(1)) {
    assert.ok(sc.opts.some(o => o.good), sc.label);
  }
});

test('ทุกศัพท์ใน GLOSSARY ปรากฏในเนื้อหาอย่างน้อยหนึ่งที่ (ไม่มีศัพท์ลอย)', () => {
  assert.ok(GLOSSARY.length >= 9);
  for (const g of GLOSSARY) {
    assert.ok(g.plain.length > 0);
    assert.ok(all.includes(g.term), 'ไม่พบศัพท์ในเนื้อหา: ' + g.term);
  }
});

test('FOURFLOW มี 4 เลน p i d r', () => {
  assert.deepEqual(D.FOURFLOW.map(f => f.lane), ['p', 'i', 'd', 'r']);
});

test('ทุกสถานีมีชื่อสั้นสำหรับแถบเส้นทาง', () => {
  assert.deepEqual(D.STATIONS.map(s => s.short), ['ผู้ส่ง', 'NRT', 'เครื่องบิน', 'BKK', 'DOF', 'ผู้รับ']);
});

test('เพดานอายุปลาในถุงคือ 24 ชม. (1440 นาที)', () => {
  assert.equal(D.CONST.BAG_LIMIT_MIN, 1440);
});

test('เอกสารทางการตรงกับรายงานของทีม: DOF 2/DOF 9/ร.6, Tor.Ror.Nor.6, ร.7 + IMD', () => {
  const docs = n => D.STEPS[n - 1].docs.join(' | ');
  assert.match(docs(11), /DOF 2/); assert.match(docs(11), /DOF 9/); assert.match(docs(11), /ร\.6/);
  assert.match(docs(13), /Tor\.Ror\.Nor\.6/);
  assert.match(docs(14), /ร\.7/); assert.match(docs(14), /IMD/);
});
