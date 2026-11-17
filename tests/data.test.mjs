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

// รายงานรวมเล่ม 10 หัวข้อ (หัวข้อ 1.2, 1.4, 10.0.1, 10.0.3)
test('ค่าเที่ยวบินตรงกับรายงาน (NN393, A350-900, 07:00 JST → 12:00 ICT, บินตรง 7 ชม.)', () => {
  assert.equal(D.CONST.FLIGHT.no, 'NN393');
  assert.equal(D.CONST.FLIGHT.type, 'Airbus A350-900');
  assert.equal(D.CONST.FLIGHT.airline, 'No Fish No Fly Airline');
  assert.equal(D.CONST.FLIGHT.depJST, '07:00');
  assert.equal(D.CONST.FLIGHT.arrICT, '12:00');
  assert.equal(D.STEPS[8].dep, 420); // 07:00 JST = 420 นาที
  assert.equal(D.STEPS[8].t[1] - D.STEPS[8].dep, 420); // บิน 7 ชม.
  assert.equal(D.STEPS[8].t[1] - D.CONST.JST_MINUS_ICT, 720); // ลงจอด 12:00 ICT
});
test('Master Timeline: ปิดถุง 01:00 JST (T0) · เปิดถุงที่สถานกักกันภายใน 15:00 ICT · อยู่ในถุง 16 ชม.', () => {
  assert.equal(D.CONST.SEAL0, 60);
  assert.equal(D.CONST.OPEN0, 1020);            // 15:00 ICT = 17:00 JST
  assert.equal(D.CONST.OPEN0 - D.CONST.SEAL0, 960);
  assert.equal(D.STEPS[12].t[1], D.CONST.OPEN0); // ขั้น 13 จบตอนเปิดถุง
  assert.deepEqual(D.STEPS[5].t, [60, 180]);    // รถ 01:00–03:00 JST
  assert.deepEqual(D.STEPS[9].t, [840, 890]);   // Unload + คลัง AVI 12:00–12:50 ICT
});
test('อุณหภูมิ 15–20°C ปรากฏในขั้นรถ คลัง และเที่ยวบิน', () => {
  for (const i of [5, 6, 8]) assert.match(JSON.stringify(D.STEPS[i]), /15–20°C/, 'ขั้น ' + (i + 1));
});
test('ผู้เกี่ยวข้องใช้ชื่อสมมติตามรายงาน', () => {
  const who = i => D.STEPS[i].who;
  assert.match(who(0), /Lucky Koi House/);
  assert.match(who(5), /Koi Express Logistics/);
  assert.match(who(6), /Sakura Scale Ground Services/);
  assert.match(who(8), /No Fish No Fly Airline/);
  assert.match(who(9), /Golden Scale Cargo Handling/);
  assert.match(who(10), /Lat Krabang Clearance/);
  assert.match(who(14), /Wasana Tongsuk Koi Farm/);
});

test('ทุกขั้นมี who/what/why และ t===null ต้อง approx', () => {
  for (const s of D.STEPS) {
    for (const k of ['who', 'what', 'why', 'name', 'risk']) {
      assert.ok(typeof s[k] === 'string' && s[k].length > 0, `ขั้น ${s.n} ไม่มี ${k}`);
    }
    if (s.t === null) assert.equal(s.approx, true, `ขั้น ${s.n}`);
  }
});

test('ไม่มีคำต้องห้ามตามที่ล็อกไว้', () => {
  assert.doesNotMatch(all, /(?<!อย่างน้อย )21\s*วัน|30\s*[-–]\s*35\s*วัน|60\s*วัน/);
  assert.doesNotMatch(all, /ความไวต่ออัตรารอด/);
  assert.doesNotMatch(all, /หัวข้อ\s*6/);
});

test('บรรจุ: Triple Bagging + 1 ตัว : 1 ถุง : 1 กล่อง และไม่ใช้สูตรน้ำ:ออกซิเจนตายตัว (หัวข้อ 2.1.4)', () => {
  assert.match(all, /Triple Bagging/);
  assert.match(all, /1 ตัว : 1 ถุง : 1 กล่อง/);
  assert.doesNotMatch(all, /1:2|1 : 2/);
  assert.doesNotMatch(all, /งดอาหาร 3/);
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

test('เส้นตายอายุปลาในถุงตาม SOP คือ 18 ชม. (1080 นาที) · รายงาน 10.0.1', () => {
  assert.equal(D.CONST.BAG_LIMIT_MIN, 1080);
});
test('ไม่เหลือค่าเที่ยวบินเดิม', () => {
  assert.doesNotMatch(all, /JL707|787-8|18:25/);
});

test('เอกสารทางการตรงกับรายงานของทีม: DOF 2/DOF 9/ร.6, ทรน.6, ร.7 + IMD', () => {
  const docs = n => D.STEPS[n - 1].docs.join(' | ');
  assert.match(docs(11), /DOF 2/); assert.match(docs(11), /DOF 9/); assert.match(docs(11), /ร\.6/);
  assert.match(docs(13), /ทรน\.6/);
  assert.match(docs(14), /ร\.7/); assert.match(docs(14), /IMD/);
});
