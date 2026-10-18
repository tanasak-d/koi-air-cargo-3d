import test from 'node:test';
import assert from 'node:assert/strict';
import { loadBlocks } from './helpers/load.mjs';

const ctx = loadBlocks(['koi-assets', 'koi-data', 'koi-logic', 'koi-scene']);
const SC = ctx.KoiScene;
const D = ctx.KoiData;
const L = ctx.KoiLogic;

test('boxTarget: ขั้นต่อเนื่องในสถานีเดียวกันอยู่คนละจุด', () => {
  for (let i = 0; i < 16; i++) {
    if (L.stationOf(i) !== L.stationOf(i + 1)) continue;
    const a = SC.boxTarget(i), b = SC.boxTarget(i + 1);
    assert.ok(a.x !== b.x || a.z !== b.z, 'ขั้น ' + i + ' กับ ' + (i + 1) + ' ซ้ำจุด');
  }
});

test('easeInOut: 0→0, 1→1, 0.5→0.5 และเพิ่มขึ้นเสมอ', () => {
  assert.equal(SC.easeInOut(0), 0);
  assert.equal(SC.easeInOut(1), 1);
  assert.ok(Math.abs(SC.easeInOut(0.5) - 0.5) < 1e-9);
  let prev = -1;
  for (let t = 0; t <= 1.0001; t += 0.05) {
    const v = SC.easeInOut(Math.min(t, 1));
    assert.ok(v >= prev);
    prev = v;
  }
});

test('easeInOut: ค่านอกช่วง 0..1 ถูกบีบให้อยู่ในช่วง', () => {
  assert.equal(SC.easeInOut(-5), 0);
  assert.equal(SC.easeInOut(5), 1);
});

test('lerpPose: ปลายทาง t=0 / t=1 ตรงจุด และกลางทางเป็นค่าเฉลี่ย', () => {
  const a = { x: -4, z: 2 }, b = { x: 6, z: -2 };
  assert.deepEqual(JSON.parse(JSON.stringify(SC.lerpPose(a, b, 0))), a);
  assert.deepEqual(JSON.parse(JSON.stringify(SC.lerpPose(a, b, 1))), b);
  const m = SC.lerpPose(a, b, 0.5);
  assert.equal(m.x, 1); assert.equal(m.z, 0);
});

test('blinkOn: กระพริบช้า ไม่เกิน 2 ครั้ง/วินาที (นับการเปลี่ยนค่า ≤ 4 ใน 1 วินาที)', () => {
  let changes = 0, last = SC.blinkOn(0, false);
  for (let t = 10; t <= 1000; t += 10) {
    const v = SC.blinkOn(t, false);
    if (v !== last) changes++;
    last = v;
  }
  assert.ok(changes <= 4, 'เปลี่ยน ' + changes + ' ครั้ง');
  assert.ok(changes >= 1, 'ต้องกระพริบจริง');
});

test('blinkOn: reduced-motion ค้างสถานะ "เปิด" (ไม่กระพริบ) ทุกเวลา', () => {
  for (let t = 0; t < 3000; t += 137) assert.equal(SC.blinkOn(t, true), true);
});

test('supported() ใน Node (ไม่มีเบราว์เซอร์) เป็น false และไม่ throw', () => {
  assert.equal(SC.supported(), false);
});

test('NO_WEBGL_MESSAGE ตรงข้อความที่ตกลงไว้', () => {
  assert.equal(SC.NO_WEBGL_MESSAGE, 'เครื่องนี้แสดงภาพ 3 มิติไม่ได้ ยังดูขั้นตอนได้ตามปกติ');
});

test('overviewTile: ตำแหน่งกระเบื้อง 6 สถานีเรียงซ้ายไปขวา ไม่ซ้อนกัน และอยู่ในกรอบ', () => {
  const xs = [0, 1, 2, 3, 4, 5].map(i => SC.overviewTile(i).x);
  for (let i = 1; i < 6; i++) assert.ok(xs[i] - xs[i - 1] >= 3.5, 'กระเบื้อง ' + i + ' ชิดเกินไป');
  assert.ok(Math.abs(xs[0]) <= 12 && Math.abs(xs[5]) <= 12);
});

// ---- Task 10: หน้าตาของกล่องปลาตามสถานะความเสี่ยง ----
test('riskLook: hold = held (กระพริบ), จบสูญเสีย = loss (แดงนิ่ง), อื่น ๆ = normal', () => {
  const walk = (S) => { while (L.canAdvance(S)) L.next(S); return S; };
  const S = walk(L.newState(1));
  assert.equal(SC.riskLook(S), 'held');
  L.verify(S); L.correct(S, D.SCENARIOS[1].opts.findIndex(o => !o.good));
  assert.equal(SC.riskLook(S), 'loss');
  const ok = walk(L.newState(1)); L.verify(ok); L.correct(ok, D.SCENARIOS[1].opts.findIndex(o => o.good));
  assert.equal(SC.riskLook(ok), 'normal');
  const ctl = walk(L.newState(5)); L.verify(ctl); L.correct(ctl, D.SCENARIOS[5].opts.findIndex(o => o.good));
  assert.equal(SC.riskLook(ctl), 'normal'); // คุมความเสี่ยงได้ ไม่ใช่การสูญเสีย
  assert.equal(SC.riskLook(L.newState(0)), 'normal');
});

test('blinkOn ของสถานะ loss ไม่กระพริบ (boxPulse คืนค่าคงที่)', () => {
  for (let t = 0; t < 2000; t += 111) assert.equal(SC.boxPulse('loss', t, false), true);
  const seen = new Set();
  for (let t = 0; t < 2000; t += 50) seen.add(SC.boxPulse('held', t, false));
  assert.equal(seen.size, 2); // held กระพริบจริง
  for (let t = 0; t < 2000; t += 111) assert.equal(SC.boxPulse('held', t, true), true); // reduced-motion
});

// ---- รุ่น 2 Task 2: ตัวโหลดโมเดลที่ฝังไว้ ----
test('assetUrl: แปลงที่อยู่สีของ Kenney เป็น data URI ที่ฝังไว้ ที่อยู่อื่นคงเดิม', () => {
  assert.match(SC.assetUrl('Textures/colormap.png'), /^data:image\/png;base64,/);
  assert.match(SC.assetUrl('./models/Textures/colormap.png'), /^data:image\/png;base64,/);
  assert.equal(SC.assetUrl('data:foo'), 'data:foo');
});

test('base64ToBuffer: ถอดรหัสโมเดลได้ ขึ้นต้นด้วย glTF และขนาดตรงกับไฟล์จริง', () => {
  const buf = SC.base64ToBuffer(ctx.KoiAssets.models.cone);
  assert.equal(new TextDecoder('latin1').decode(new Uint8Array(buf, 0, 4)), 'glTF');
  assert.equal(buf.byteLength, Buffer.from(ctx.KoiAssets.models.cone, 'base64').length);
});

test('placeholderSize: มีขนาดสำรองของทุกโมเดล (กว้าง/สูง/ยาว > 0)', () => {
  assert.deepEqual([...SC.MODEL_NAMES], ['delivery', 'van', 'tractor', 'cone', 'airliner', 'koi', 'person', 'fishbox', 'bag', 'warehouse', 'xray', 'pond', 'dolly', 'farmhouse', 'dof', 'trees', 'reefer', 'japan', 'thai']);
  for (const n of SC.MODEL_NAMES) { const s = SC.placeholderSize(n); assert.ok(s.w > 0 && s.h > 0 && s.d > 0, n); }
});

// ---- รุ่น 2 Task 3: ช็อตของ 17 ขั้น (เส้นทางกล่อง + มุมกล้อง) ----
const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
const plain = (o) => JSON.parse(JSON.stringify(o));

test('SHOTS: 17 ช็อต สถานีตรงกับ stationOf, act ไม่ซ้ำ, ใช้เวลา 3–10 วินาที', () => {
  assert.equal(SC.SHOTS.length, 17);
  assert.equal(new Set(SC.SHOTS.map(s => s.act)).size, 17);
  SC.SHOTS.forEach((s, i) => {
    assert.equal(s.st, L.stationOf(i), 'ขั้น ' + (i + 1));
    assert.ok(s.dur >= 3 && s.dur <= 18, 'ขั้น ' + (i + 1));
    assert.ok(s.path.length >= 2, 'ขั้น ' + (i + 1));
  });
});

test('SHOTS: ชื่อ act ตรงตามแผน', () => {
  assert.deepEqual(plain(SC.SHOTS.map(s => s.act)), ['pondSelect', 'healthCheck', 'fasting', 'bagging', 'labeling', 'truckToNRT',
    'aviReceive', 'xrayCheck', 'loadAndFly', 'bkkUnload', 'dofInspect', 'quarantineOrder', 'quarantinePond', 'releaseDocs',
    'truckToFarm', 'recovery', 'breeding']);
});

test('SHOTS: ทุกจุดอยู่ในฉาก |x|,|z| ≤ 30 และ y ≥ 0', () => {
  SC.SHOTS.forEach((s, i) => {
    for (const p of [...s.path, s.cam.p, s.cam.t]) {
      assert.ok(Math.abs(p.x) <= 30 && Math.abs(p.z) <= 30 && p.y >= 0, 'ขั้น ' + (i + 1) + ' ' + JSON.stringify(p));
    }
  });
});

test('SHOTS: ในสถานีเดียวกัน ช็อตถัดไปเริ่มที่จุดที่ช็อตก่อนจบ (กล่องไม่วาร์ป)', () => {
  for (let i = 1; i < 17; i++) if (SC.SHOTS[i].st === SC.SHOTS[i - 1].st) {
    assert.ok(dist(SC.SHOTS[i - 1].path.at(-1), SC.SHOTS[i].path[0]) < 0.01, 'ขั้น ' + (i + 1));
  }
});

test('SHOTS: กล้องมองจุดเกิดเหตุ — เป้าห่างเส้นทางกล่อง ≤ 8, กล้องสูง ≥ 3, ห่างเป้า 8–45', () => {
  SC.SHOTS.forEach((s, i) => {
    let near = Infinity;
    for (let u = 0; u <= 1.0001; u += 0.05) near = Math.min(near, dist(s.cam.t, SC.pathPoint(s.path, u)));
    assert.ok(near <= 8, 'ขั้น ' + (i + 1) + ' เป้าห่าง ' + near.toFixed(1));
    assert.ok(s.cam.p.y >= 3, 'ขั้น ' + (i + 1));
    const d = dist(s.cam.p, s.cam.t);
    assert.ok(d >= 8 && d <= 45, 'ขั้น ' + (i + 1) + ' ระยะ ' + d.toFixed(1));
  });
});

test('pathPoint: u=0 จุดแรก u=1 จุดสุดท้าย u กลางอยู่ครึ่งระยะทาง และบีบค่านอกช่วง', () => {
  const p = [{ x: 0, y: 0, z: 0 }, { x: 10, y: 0, z: 0 }, { x: 10, y: 0, z: 10 }];
  assert.deepEqual(plain(SC.pathPoint(p, 0)), { x: 0, y: 0, z: 0 });
  assert.deepEqual(plain(SC.pathPoint(p, 0.5)), { x: 10, y: 0, z: 0 });
  assert.deepEqual(plain(SC.pathPoint(p, 0.75)), { x: 10, y: 0, z: 5 });
  assert.deepEqual(plain(SC.pathPoint(p, 2)), { x: 10, y: 0, z: 10 });
  assert.deepEqual(plain(SC.pathPoint(p, -1)), { x: 0, y: 0, z: 0 });
});

test('shotPose: reduced-motion ได้จุดปลายทันที; ปกติ u=0 อยู่จุดเริ่ม', () => {
  for (let i = 0; i < 17; i++) {
    assert.deepEqual(plain(SC.shotPose(i, 0, true)), plain(SC.SHOTS[i].path.at(-1)));
    assert.deepEqual(plain(SC.shotPose(i, 0, false)), plain(SC.SHOTS[i].path[0]));
  }
});

test('boxTarget: คือจุดปลายของเส้นทาง (x,z)', () => {
  for (let i = 0; i < 17; i++) {
    const e = SC.SHOTS[i].path.at(-1);
    assert.deepEqual(plain(SC.boxTarget(i)), { x: e.x, z: e.z });
  }
});

test('SCENE_NOTES: 6 สถานี; สถานี 3 บอกว่าผู้ดูแลปลานั่งห้องโดยสาร; สถานี 5 ใช้ถ้อยคำกักกันที่ล็อกไว้ ไม่มีจำนวนวัน', () => {
  assert.equal(SC.SCENE_NOTES.length, 6);
  assert.match(SC.SCENE_NOTES[2].map(n => n.text).join(' '), /ห้องโดยสาร/);
  const s5 = SC.SCENE_NOTES[4].map(n => n.text).join(' ');
  assert.match(s5, /จนกว่า DOF จะตรวจและอนุญาตให้ปล่อย/);
  assert.doesNotMatch(s5, /\d+\s*วัน/);
});

// ---- รุ่น 2 Task 4: กล้องเลื่อนเอง คุณภาพอัตโนมัติ การ์ดลอย ----
test('camGlide: k=1 ถึงเป้าทันที done=true; k=0.5 อยู่ครึ่งทาง; เริ่มจากตำแหน่งปัจจุบันเสมอ', () => {
  const cur = { p: { x: 0, y: 10, z: 0 }, t: { x: 0, y: 0, z: 0 } };
  const goal = { p: { x: 10, y: 10, z: 0 }, t: { x: 4, y: 0, z: 0 } };
  const a = SC.camGlide(cur, goal, 1);
  assert.deepEqual(plain(a), { p: goal.p, t: goal.t, done: true });
  const b = SC.camGlide(cur, goal, 0.5);
  assert.deepEqual(plain(b.p), { x: 5, y: 10, z: 0 });
  assert.deepEqual(plain(b.t), { x: 2, y: 0, z: 0 });
  assert.equal(b.done, false);
  const c = SC.camGlide(b, goal, 0.5);          // ก้าวต่อจากจุดที่อยู่จริง ไม่เริ่มใหม่จากต้นทาง
  assert.deepEqual(plain(c.p), { x: 7.5, y: 10, z: 0 });
  assert.equal(SC.camGlide({ p: goal.p, t: goal.t }, goal, 0.1).done, true);
});

test('glideK: reduced = 1 (กระโดด), ปกติ 0<k<1 และ dt มากขึ้น k มากขึ้น', () => {
  assert.equal(SC.glideK(0.016, true), 1);
  const a = SC.glideK(0.016, false), b = SC.glideK(0.05, false);
  assert.ok(a > 0 && a < 1 && b > a);
});

test('idleReturnDue: กลับมุมช็อตเมื่อไม่แตะครบ 8 วินาทีและไม่ได้กำลังเลื่อนอยู่', () => {
  assert.equal(SC.IDLE_RETURN_MS, 8000);
  assert.equal(SC.idleReturnDue(0, 7999, false), false);
  assert.equal(SC.idleReturnDue(0, 8000, false), true);
  assert.equal(SC.idleReturnDue(0, 9000, true), false);
  assert.equal(SC.idleReturnDue(null, 9000, false), false); // ผู้ชมยังไม่เคยแตะ ไม่ต้องกลับ
});

test('nextQuality: เฟรมตกปิดเงาก่อน แล้วลดความละเอียด เฟรมดีคงเดิม', () => {
  assert.deepEqual(plain(SC.nextQuality({ ratio: 2, shadows: true }, 20)), { ratio: 2, shadows: false });
  assert.deepEqual(plain(SC.nextQuality({ ratio: 2, shadows: false }, 20)), { ratio: 1, shadows: false });
  assert.deepEqual(plain(SC.nextQuality({ ratio: 1, shadows: false }, 20)), { ratio: 1, shadows: false });
  assert.deepEqual(plain(SC.nextQuality({ ratio: 2, shadows: true }, 60)), { ratio: 2, shadows: true });
});

test('cardPos: อยู่ในกรอบเวทีเสมอ และพลิกไปใต้จุดเมื่อชนขอบบน', () => {
  const a = SC.cardPos(5, 5, 200, 60, 400, 300);
  assert.ok(a.left >= 8 && a.top > 5, JSON.stringify(a));
  const b = SC.cardPos(395, 200, 200, 60, 400, 300);
  assert.ok(b.left + 200 <= 392 && b.top + 60 <= 200, JSON.stringify(b));
  const c = SC.cardPos(200, 295, 200, 60, 400, 300);
  assert.ok(c.top + 60 <= 300, JSON.stringify(c));
});

// ---- รุ่น 2 Task 6–9: ทุกช็อตมีอนิเมชันของตัวเอง ----
const actionsFor = (from, to) => { for (let i = from; i <= to; i++) assert.equal(typeof SC.ACTIONS[SC.SHOTS[i].act], 'function', SC.SHOTS[i].act); };
test('ACTIONS: ทุกช็อตของสถานี 1 (ขั้น 1–6) มีฟังก์ชันอนิเมชัน', () => actionsFor(0, 5));
test('ACTIONS: ทุกช็อตของสถานี 2 (ขั้น 7–8) มีฟังก์ชันอนิเมชัน', () => actionsFor(6, 7));
test('ACTIONS: ช็อตของสถานี 3–4 (ขั้น 9–10) มีฟังก์ชันอนิเมชัน', () => actionsFor(8, 9));
test('ACTIONS: ช็อตของสถานี 5–6 (ขั้น 11–17) มีฟังก์ชันอนิเมชัน', () => actionsFor(10, 16));
test('ACTIONS: ครบทั้ง 17 ช็อต', () => SC.SHOTS.forEach(s => assert.equal(typeof SC.ACTIONS[s.act], 'function', s.act)));

// ---- รุ่น 2 Task 10: ภาพเหตุการณ์เสี่ยงที่ด่าน ----
test('riskCue: แต่ละเหตุการณ์ที่ค้างได้ cue ของตัวเอง ไม่ค้าง = null', () => {
  const want = [null, 'bag-leak', 'cutoff-clock', 'hold-notoc', 'doc-mismatch', 'disease'];
  for (let sc = 1; sc <= 5; sc++) { const S = L.newState(sc); while (L.canAdvance(S)) L.next(S); assert.equal(SC.riskCue(S), want[sc], 'เหตุการณ์ ' + sc); }
  assert.equal(SC.riskCue(L.newState(0)), null);
  const ok = L.newState(1); while (L.canAdvance(ok)) L.next(ok); L.verify(ok); L.correct(ok, D.SCENARIOS[1].opts.findIndex(o => o.good));
  assert.equal(SC.riskCue(ok), null);   // แก้แล้ว ไม่ค้าง
});

test('riskCue: ด่านของเหตุการณ์อยู่ในช็อตที่กล้องจับได้ (ขั้นของเหตุการณ์มีช็อต)', () => {
  for (let sc = 1; sc <= 5; sc++) assert.ok(SC.SHOTS[D.SCENARIOS[sc].step], 'เหตุการณ์ ' + sc);
});

test('holdU: ค้างที่ด่านแล้วอนิเมชันหยุดที่จังหวะของด่าน (0 < u ≤ 1) ไม่ค้าง = null', () => {
  for (let sc = 1; sc <= 5; sc++) {
    const S = L.newState(sc); while (L.canAdvance(S)) L.next(S);
    const u = SC.holdU(S); assert.ok(u > 0 && u <= 1, 'เหตุการณ์ ' + sc);
  }
  assert.equal(SC.holdU(L.newState(0)), null);
});

// ---- Final review fixes ----
const heldAt = (sc) => { const S = L.newState(sc); while (L.canAdvance(S)) L.next(S); return S; };
test('animU: ค้างที่ด่าน → หยุดที่จังหวะของด่าน; reduced-motion ไปที่จังหวะนั้นทันที', () => {
  const S = heldAt(3), dur = SC.SHOTS[S.idx].dur;
  assert.equal(SC.animU(S, S.idx, 1, dur, false), 1 / dur);
  assert.equal(SC.animU(S, S.idx, 100, dur, false), 0.245);
  assert.equal(SC.animU(S, S.idx, 0, dur, true), 0.245);
});
test('animU: ตอบผิด (สูญเสีย) อนิเมชันยังหยุดที่ด่าน ไม่เล่นต่อเหมือนส่งสำเร็จ', () => {
  const S = heldAt(3); L.verify(S); L.correct(S, D.SCENARIOS[3].opts.findIndex(o => !o.good));
  assert.equal(S.end, 'loss');
  assert.equal(SC.animU(S, S.idx, 100, SC.SHOTS[S.idx].dur, false), 0.245);
});
test('animU: แก้ถูกแล้วเล่นต่อจนจบ; reduced-motion = 1; ขั้นอื่นไม่ถูกจำกัด', () => {
  const S = heldAt(3); L.verify(S); L.correct(S, D.SCENARIOS[3].opts.findIndex(o => o.good));
  const dur = SC.SHOTS[S.idx].dur;
  assert.equal(SC.animU(S, S.idx, 100, dur, false), 1);
  assert.equal(SC.animU(S, S.idx, 0, dur, true), 1);
  assert.equal(SC.animU(heldAt(3), 2, 100, 5, false), 1);
});
test('resumeT0: ปล่อยจากด่านแล้วเล่นต่อจากจังหวะเดิม (ไม่กระโดดไปท้ายขั้น)', () => {
  assert.equal(SC.resumeT0(20000, 0.65, 10), 13500);
});
test('idleReturnDue: ระหว่างผู้ชมกำลังลากกล้องค้างไว้ ไม่ดึงกล้องกลับ', () => {
  assert.equal(SC.idleReturnDue(0, 20000, false, true), false);
  assert.equal(SC.idleReturnDue(0, 20000, false, false), true);
});

// ---- โมเดลจาก Blender: ปลาคาร์ฟ 3 สายพันธุ์ ----
test('koiBreed: เลือกสายพันธุ์ตามสี (ขาว = ซันเก้, ส้ม/แดง = โคฮากุ, ทอง = โอกอน)', () => {
  assert.equal(SC.koiBreed(0xffffff), 'Koi_Sanke');
  assert.equal(SC.koiBreed(0xff7a33), 'Koi_Kohaku');
  assert.equal(SC.koiBreed(0xd13b32), 'Koi_Kohaku');
  assert.equal(SC.koiBreed(0xf5c242), 'Koi_Ogon');
});

// ---- ความเสถียร: ของในฉากต้องอยู่ในท่าที่ถูกต้องเสมอ ไม่ว่าจะข้ามขั้นมาอย่างไร ----
test('poseOrder: ทุกขั้นในสถานีถูกจัดท่า — ขั้นที่ผ่านแล้ว u=1, ขั้นที่ยังไม่ถึง u=0, ขั้นปัจจุบันทำทีหลังสุด', () => {
  const list = plain(SC.poseOrder(3, 0.4));          // ขั้น 4 ของสถานี 1 (ขั้น 1–6)
  assert.deepEqual(list, [{ k: 0, u: 1 }, { k: 1, u: 1 }, { k: 2, u: 1 }, { k: 4, u: 0 }, { k: 5, u: 0 }, { k: 3, u: 0.4 }]);
  assert.deepEqual(plain(SC.poseOrder(8, 0.7)), [{ k: 8, u: 0.7 }]);   // สถานีที่มีขั้นเดียว
});

test('nextQuality: ลดคุณภาพเมื่อเฟรมตกติดกัน 2 ช่วงเท่านั้น (สะดุดครั้งเดียวตอนสร้างฉากใหม่ไม่นับ)', () => {
  const q = { ratio: 2, shadows: true };
  assert.deepEqual(plain(SC.nextQuality(q, 20, 1)), q);
  assert.deepEqual(plain(SC.nextQuality(q, 20, 2)), { ratio: 2, shadows: false });
});

// ---- ขั้น 9: ต้องขนของขึ้นเครื่องให้เสร็จก่อนเครื่องบินออก (มาร์ชพบว่าเครื่องออกก่อนของขึ้น) ----
test('loadPhases: เครื่องบินเริ่มเคลื่อนก็ต่อเมื่อกล่องถึงประตูแล้ว เข้าห้องสินค้าแล้ว และประตูปิดแล้ว', () => {
  for (let u = 0; u <= 1.0001; u += 0.01) {
    const p = SC.loadPhases(u);
    if (p.fly > 0) {
      assert.equal(p.e, 1, 'u=' + u.toFixed(2));
      assert.equal(p.inHold, true, 'u=' + u.toFixed(2));
      assert.equal(p.doorOpen, false, 'u=' + u.toFixed(2));
    }
    if (p.inHold) assert.equal(p.e, 1, 'กล่องหายเข้าเครื่องก่อนถึงประตู u=' + u.toFixed(2));
  }
  assert.equal(SC.loadPhases(0).fly, 0);
  assert.equal(SC.loadPhases(1).fly, 1);
});

test('loadPhases: เหตุการณ์ NOTOC ค้างที่ด่านก่อนกล่องเข้าห้องสินค้า (กล่องยังมองเห็นอยู่ที่ประตู)', () => {
  const S = L.newState(3); while (L.canAdvance(S)) L.next(S);
  const p = SC.flightPhases(SC.holdU(S)).ground;          // ขั้น 9 ช่วงแรก = ขนของที่สนามบิน
  assert.equal(p.inHold, false);
  assert.ok(p.e > 0.9);
});

// ---- ขั้น 11–12: โต๊ะ เอกสาร และกล่องต้องวางพอดี ไม่เหลื่อมกัน (มาร์ชพบเอกสารซ้อนโต๊ะ/กล่อง) ----
const rect = (x, z, w, d) => ({ x0: x - w / 2, x1: x + w / 2, z0: z - d / 2, z1: z + d / 2 });
const inside = (a, b) => a.x0 >= b.x0 && a.x1 <= b.x1 && a.z0 >= b.z0 && a.z1 <= b.z1;
const overlap = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.z0 < b.z1 && a.z1 > b.z0;
test('DOF_LAYOUT: เอกสารทุกใบอยู่บนโต๊ะทั้งใบ และไม่ซ้อนกับกล่องปลาที่วางบนโต๊ะ', () => {
  const Lay = SC.DOF_LAYOUT;
  for (const [deskName, step, docs] of [['counter', 10, ['docA', 'docB']], ['order', 11, ['order']]]) {
    const d = Lay.desks[deskName], desk = rect(d.x, d.z, d.w, d.d);
    const e = SC.SHOTS[step].path.at(-1), box = rect(e.x, e.z, 1.65, 1.15);
    assert.ok(inside(box, desk), 'กล่องไม่อยู่บนโต๊ะ ' + deskName);
    for (const n of docs) {
      const p = Lay.docs[n], doc = rect(p.x, p.z, 0.7, 0.95);
      assert.ok(inside(doc, desk), n + ' ล้นโต๊ะ');
      assert.ok(!overlap(doc, box), n + ' ซ้อนกล่อง');
    }
  }
});

// ---- ขั้น 11: รถตู้ถอยหลังเข้ามาจอดหน้าเคาน์เตอร์ แล้วจึงยกกล่องออก (มาร์ชพบว่ากล่องไม่ได้อยู่ในรถ) ----
test('vanPhases: กล่องอยู่ในรถ (มองไม่เห็น) ตลอดที่รถยังเคลื่อน รถหันท้ายเข้าเคาน์เตอร์และจอดก่อนชนโต๊ะ', () => {
  const desk = SC.DOF_LAYOUT.desks.counter, deskLeft = desk.x - desk.w / 2;
  let prevX = -Infinity;
  for (let u = 0; u <= 1.0001; u += 0.01) {
    const v = SC.vanPhases(u);
    assert.ok(v.x >= prevX - 1e-9, 'รถต้องถอยเข้าทางเดียว (x เพิ่มขึ้น)'); prevX = v.x;
    const moving = SC.vanPhases(Math.min(1, u + 0.01)).x > v.x + 1e-6;
    if (moving) assert.equal(v.cargoInVan, true, 'กล่องออกจากรถตอนรถยังวิ่ง u=' + u.toFixed(2));
    assert.ok(v.x + 2.3 <= deskLeft - 0.3, 'ท้ายรถชนโต๊ะ u=' + u.toFixed(2));
  }
  assert.equal(SC.vanPhases(0).cargoInVan, true);
  assert.equal(SC.vanPhases(1).cargoInVan, false);
  assert.equal(SC.vanPhases(0).facing, Math.PI);              // หันหัวออก (ท้ายรถเข้าหาเคาน์เตอร์)
});

// ---- ขั้น 10: ประตูคลัง BKK เปิดก่อน แล้วรถลากพากล่องเข้าไปข้างใน (มาร์ชขอ) ----
test('bkkPhases: ประตูเปิดสุดก่อนรถลากถึงแนวผนังหน้า และเส้นทางจบข้างในคลัง', () => {
  const path = SC.SHOTS[9].path, FRONT_Z = -6;          // คลังอยู่ที่ z = -10 ลึก 8 → ผนังหน้าอยู่ที่ z = -6
  assert.ok(path.at(-1).z < FRONT_Z - 1.5, 'เส้นทางต้องเข้าไปในคลัง');
  for (let u = 0; u <= 1.0001; u += 0.01) {
    const ph = SC.bkkPhases(u), p = SC.pathPoint(path, ph.e);
    if (p.z < FRONT_Z + 2.5) assert.equal(ph.door, 1, 'รถถึงประตูแต่ประตูยังไม่เปิดสุด u=' + u.toFixed(2));
  }
  assert.equal(SC.bkkPhases(0).door, 0);
});

// ---- เส้นทางบินบนแผนที่ (ขั้น 9 → 10) ----
test('mapXZ: แปลงลองจิจูด/ละติจูดเป็นตำแหน่งบนแผนที่ อยู่ในกรอบ ±30 · ญี่ปุ่นอยู่ขวาบน ไทยอยู่ซ้ายล่าง', () => {
  const n = SC.mapXZ(SC.AIRPORTS.NRT.lon, SC.AIRPORTS.NRT.lat), b = SC.mapXZ(SC.AIRPORTS.BKK.lon, SC.AIRPORTS.BKK.lat);
  for (const p of [n, b, SC.mapXZ(86, -2), SC.mapXZ(150, 48)]) assert.ok(Math.abs(p.x) <= 30 && Math.abs(p.z) <= 30);
  assert.ok(n.x > b.x, 'ญี่ปุ่นอยู่ทางตะวันออก (x มากกว่า)');
  assert.ok(n.z < b.z, 'ญี่ปุ่นอยู่เหนือ (z น้อยกว่า = ไกลกล้อง)');
});

test('greatCircle: เส้นทางบินจริงโค้งตามผิวโลก — ปลายตรงสนามบิน และกลางทางโค้งขึ้นเหนือกว่าเส้นตรง', () => {
  const A = SC.AIRPORTS.NRT, B = SC.AIRPORTS.BKK, pts = SC.greatCircle(A, B, 40);
  assert.equal(pts.length, 41);
  assert.ok(Math.abs(pts[0].lon - A.lon) < 1e-6 && Math.abs(pts[0].lat - A.lat) < 1e-6);
  assert.ok(Math.abs(pts[40].lon - B.lon) < 1e-6 && Math.abs(pts[40].lat - B.lat) < 1e-6);
  assert.ok(pts[20].lat > (A.lat + B.lat) / 2, 'กลางทางต้องอยู่เหนือกว่าค่าเฉลี่ยละติจูด');
});

test('flightPhases: ขนของ+วิ่งขึ้นที่สนามบินก่อน แล้วจึงเปลี่ยนเป็นแผนที่ และเครื่องบินเริ่มบินบนแผนที่หลังจากนั้น', () => {
  for (let u = 0; u <= 1.0001; u += 0.01) {
    const f = SC.flightPhases(u);
    if (f.mapView) assert.equal(f.ground.fly, 1, 'เปลี่ยนเป็นแผนที่ก่อนเครื่องวิ่งขึ้นเสร็จ u=' + u.toFixed(2));
    if (f.route > 0) assert.equal(f.mapView, true, 'เครื่องบินบนแผนที่เริ่มก่อนเปลี่ยนภาพ u=' + u.toFixed(2));
  }
  assert.equal(SC.flightPhases(0).route, 0);
  assert.equal(SC.flightPhases(1).route, 1);
});

test('SHOTS ขั้น 9: มีมุมกล้องที่สอง (มองแผนที่) และจังหวะสลับกล้องตรงกับตอนเปลี่ยนเป็นแผนที่', () => {
  const s = SC.SHOTS[8];
  assert.ok(s.cam2 && s.cam2.p.y > SC.MAP_Y, 'กล้องต้องอยู่เหนือแผนที่');
  assert.ok(Math.abs(s.cam2.t.y - SC.MAP_Y) < 2, 'กล้องต้องมองที่แผนที่');
  assert.equal(SC.flightPhases(s.camAt).mapView, true);
  assert.equal(SC.flightPhases(s.camAt - 0.02).mapView, false);
});

// ---- บรรยากาศประเทศ: ญี่ปุ่น (สถานี 1–3) · ไทย (สถานี 4–6) ----
const segDist2 = (p, a, b) => { const dx = b.x - a.x, dz = b.z - a.z, L = dx * dx + dz * dz;
  const t = L ? Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.z - a.z) * dz) / L)) : 0; return Math.hypot(p.x - a.x - t * dx, p.z - a.z - t * dz); };
test('DECOR: ของตกแต่งฝั่งญี่ปุ่นอยู่สถานี 1–3 และฝั่งไทยอยู่สถานี 4–6 ทุกสถานีมีของตกแต่ง', () => {
  assert.equal(SC.DECOR.length, 6);
  SC.DECOR.forEach((list, st) => {
    assert.ok(list.length > 0, 'สถานี ' + (st + 1));
    for (const d of list) assert.equal(d.model, st <= 2 ? 'japan' : 'thai', d.node + ' สถานี ' + (st + 1));
  });
});
test('DECOR: ของตกแต่งไม่ขวางเส้นทางของกล่อง/รถ (ห่างเส้นทาง ≥ รัศมีของ + 1.2) — กันภาพเหลื่อมทับ', () => {
  SC.DECOR.forEach((list, st) => {
    const paths = SC.SHOTS.filter(s => s.st === st).map(s => s.path);
    for (const d of list) {
      if (d.bg) continue;                                                // ฉากหลังไกล ๆ (ภูเขา/เจดีย์)
      for (const path of paths) for (let k = 1; k < path.length; k++) {
        const dist = segDist2({ x: d.x, z: d.z }, path[k - 1], path[k]);
        assert.ok(dist >= d.r + 1.2, d.node + ' ชิดเส้นทางสถานี ' + (st + 1) + ' (' + dist.toFixed(1) + ')');
      }
    }
  });
});
