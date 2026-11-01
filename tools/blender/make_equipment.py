# อุปกรณ์และของในฉากกลุ่ม 4 (ปั้นใหม่ 1 พ.ย. 2026 ตามภาพใน โมเดล/Group 4/) ส่งออกทีละไฟล์:
#   pond.glb      บ่อปลาขอบหินกลม รัศมี 1 สูง 0.4 (เว็บขยายตามขนาดบ่อ) ผิวน้ำ Pond_Water
#   table.glb     โต๊ะสแตนเลส 2 x 1.4 ผิวโต๊ะสูง 0.9 (เว็บยืดกว้าง/ลึกตามแต่ละจุด)
#   conveyor.glb  สายพานลูกกลิ้ง 1 ท่อน ยาว 2 (ตามแกน x) กว้าง 1.4 ผิวบนสูง 0.9 (เว็บต่อหลายท่อนให้ยาวตามต้องการ)
#   uld.glb       ตู้ ULD แบบ AKE (ด้านล่างเฉียงหนึ่งข้าง) มีโลโก้หลักสูตร
#   docs.glb      เอกสาร (Doc มีแถบหัวกระดาษ Doc_Header ให้เว็บเปลี่ยนสี) + ตราประทับ (Stamp)
#   oxygen.glb    ถังออกซิเจนสีเขียว หัววาล์วทองเหลือง
#   feedbag.glb   ถุงอาหารปลา KOI FEED (ใช้ขั้นงดอาหาร)
#   fences.glb    รั้ว 2 แบบ ท่อนละ 2.5 (ตามแกน x): Fence_Wood รั้วไม้ฟาร์ม / Fence_Metal รั้วเหล็กบ่อกักกัน
#   gate.glb      ไม้กั้นด่าน: ตู้เสา + คานลายแดงขาว Gate_Bar (จุดหมุนที่เสา คานยื่นไปด้าน -y = +z ในเว็บ) + เสารับปลายคาน
# ตราบนเอกสารใช้วงกลมเรียบ ๆ (ไม่ใช่ตราจริง) ตามที่มาร์ชเลือก · ทุกชิ้นปั้นแบบประหยัดไฟล์ (รวมชิ้นเล็กเป็นเมชเดียว)
# แกน: Blender -y = ด้านหน้าในเว็บ (+z) · ฐานอยู่ที่ z = 0
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import (reset, mat, hexrgb, prim, root, export_glb, bevel_box, empty, text, boxes, obj_from_bmesh,
                    lathe, logo_decal, THAI_FONT)

R90 = (math.radians(90), 0, 0)


# ---------------- บ่อปลาขอบหิน ----------------
def pond():
    STONE_A = mat('StoneA', hexrgb(0x8f9399), 0.9)
    STONE_B = mat('StoneB', hexrgb(0x76695d), 0.9)
    WATER = mat('PondWater', hexrgb(0x5fb4e6), 0.05, alpha=0.85)
    r = root('Pond')
    random.seed(4)
    # หินก้อนเหลี่ยม 2 ชั้นเรียงรอบวง (ทรงไอโคสเฟียร์หยาบ ๆ บีบให้แบน) แยก 2 สีให้ดูเป็นหินธรรมชาติ
    for layer, (z, n, rad) in enumerate(((0.12, 18, 0.93), (0.3, 18, 0.9))):
        bms = {0: bmesh.new(), 1: bmesh.new()}
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * layer) / n
            bm = bms[(k + layer) % 2]
            res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
            sx, sy, sz = random.uniform(0.2, 0.25), random.uniform(0.14, 0.17), random.uniform(0.11, 0.14)
            m = (__import__('mathutils').Matrix.Rotation(a, 4, 'Z') @
                 __import__('mathutils').Matrix.Diagonal((sx, sy, sz, 1)))
            bmesh.ops.transform(bm, matrix=m, verts=res['verts'])
            bmesh.ops.translate(bm, vec=(math.cos(a) * rad, math.sin(a) * rad, z), verts=res['verts'])
        obj_from_bmesh('PondStoneA%d' % layer, bms[0], STONE_A, parent=r)
        obj_from_bmesh('PondStoneB%d' % layer, bms[1], STONE_B, parent=r)
    # ผิวน้ำ (แผ่นกลม 16 เหลี่ยม ชื่อ Pond_Water — เว็บเปลี่ยนสีน้ำได้)
    prim('cylinder', 'Pond_Water', WATER, loc=(0, 0, 0.27), vertices=16, radius=0.86, depth=0.02, parent=r)
    prim('cylinder', 'PondFloor', mat('PondFloor', hexrgb(0x3d6f8f), 0.9), loc=(0, 0, 0.02), vertices=16, radius=0.86, depth=0.04, parent=r)
    return r


# ---------------- โต๊ะสแตนเลส ----------------
def table():
    STEEL = mat('Steel', hexrgb(0xdde1e5), 0.4, 0.25)   # โลหะน้อย ๆ: ในเว็บไม่มีภาพสะท้อนรอบตัว ถ้าโลหะมากจะดำ
    r = root('Table')
    W, D, H = 2.0, 1.4, 0.9
    bevel_box('TableTop', (W, D, 0.05), (0, 0, H - 0.025), STEEL, r, 0.01)
    legs = [((sx * (W / 2 - 0.08), sy * (D / 2 - 0.08), (H - 0.1) / 2), (0.03, 0.03, (H - 0.1) / 2)) for sx in (1, -1) for sy in (1, -1)]
    legs += [((0, sy * (D / 2 - 0.08), 0.25), (W / 2 - 0.08, 0.015, 0.015)) for sy in (1, -1)]   # คานล่างยาว
    legs += [((sx * (W / 2 - 0.08), 0, 0.25), (0.015, D / 2 - 0.08, 0.015)) for sx in (1, -1)]   # คานล่างสั้น
    legs += [((0, sy * (D / 2 - 0.04), H - 0.08), (W / 2 - 0.02, 0.02, 0.03)) for sy in (1, -1)]  # ขอบใต้ผิวโต๊ะ
    boxes('TableFrame', legs, STEEL, r)
    return r


# ---------------- สายพานลูกกลิ้ง (1 ท่อน) ----------------
def conveyor():
    BLUE = mat('ConvFrame', hexrgb(0x4f6c8f), 0.5, 0.3)
    ROLL = mat('ConvRoller', hexrgb(0x3a3f46), 0.4, 0.5)
    LEG = mat('ConvLeg', hexrgb(0x22262b), 0.6)
    r = root('Conveyor')
    L, W, TOP = 2.0, 1.4, 0.9
    # รางข้างสองข้าง (น้ำเงินเทา) + ลูกกลิ้ง 10 ลูกตามขวาง (ผิวบนพอดี TOP)
    boxes('ConvRails', [((0, s * (W / 2 - 0.06), TOP - 0.12), (L / 2, 0.06, 0.14)) for s in (1, -1)], BLUE, r)
    bm = bmesh.new()
    for k in range(10):
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.07, radius2=0.07, depth=W - 0.24)
        m = __import__('mathutils').Matrix.Rotation(math.radians(90), 4, 'X')
        bmesh.ops.transform(bm, matrix=m, verts=res['verts'])
        bmesh.ops.translate(bm, vec=(-L / 2 + 0.1 + k * (L - 0.2) / 9, 0, TOP - 0.07), verts=res['verts'])
    obj_from_bmesh('ConvRollers', bm, ROLL, parent=r)
    # ขาเหล็กดำ 4 ขา + คานล่าง
    legs = [((sx * (L / 2 - 0.15), sy * (W / 2 - 0.12), (TOP - 0.26) / 2), (0.04, 0.04, (TOP - 0.26) / 2)) for sx in (1, -1) for sy in (1, -1)]
    legs += [((sx * (L / 2 - 0.15), 0, 0.3), (0.03, W / 2 - 0.12, 0.03)) for sx in (1, -1)]
    boxes('ConvLegs', legs, LEG, r)
    return r


# ---------------- ตู้ ULD แบบ AKE ----------------
def uld():
    ALU = mat('UldAlu', hexrgb(0xc4c9cf), 0.4, 0.6)
    EDGE = mat('UldEdge', hexrgb(0x8e959d), 0.45, 0.6)
    NET = mat('UldNet', hexrgb(0xb8b29a), 0.8, alpha=0.9)
    INK = mat('UldInk', hexrgb(0x1d1d1d), 0.6)
    r = root('ULD')
    W, D, H = 2.4, 2.0, 1.9                         # ยาว (x) ลึก (y) สูง · ฐานแคบกว่าด้านบน (ด้าน +y เฉียง ตามรูปท้องเครื่อง)
    BASE_D = 1.55
    # หน้าตัดตามแกน y: ฐาน -D/2..-D/2+BASE_D แล้วเฉียงขึ้นไปเต็มลึกที่ความสูง 0.6
    prof = [(-D / 2, 0.08), (-D / 2 + BASE_D, 0.08), (D / 2, 0.6), (D / 2, H), (-D / 2, H)]
    bm = bmesh.new()
    a = [bm.verts.new((-W / 2, y, z)) for y, z in prof]
    b = [bm.verts.new((W / 2, y, z)) for y, z in prof]
    n = len(prof)
    for k in range(n):
        bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.faces.new(list(reversed(a))); bm.faces.new(b)
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj_from_bmesh('UldBody', bm, ALU, parent=r)
    prim('cube', 'UldBase', EDGE, loc=(0, -D / 2 + BASE_D / 2, 0.04), scale=(W / 2 + 0.03, BASE_D / 2 + 0.03, 0.04), parent=r)
    # ขอบมุมและคาดหลังคา
    boxes('UldEdges', [((sx * (W / 2 + 0.01), -D / 2 - 0.01, H / 2), (0.03, 0.03, H / 2)) for sx in (1, -1)] +
          [((0, -D / 2 - 0.01, H), (W / 2 + 0.02, 0.03, 0.03)), ((0, D / 2 + 0.01, H), (W / 2 + 0.02, 0.03, 0.03))] +
          [((x, 0, H + 0.01), (0.03, D / 2, 0.01)) for x in (-0.4, 0.4)], EDGE, r)
    # ด้านหน้า (-y) เป็นม่านตาข่ายเปิดปิด (ส่วนขวา) + ช่องเอกสาร (ส่วนซ้าย)
    prim('cube', 'UldNet', NET, loc=(0.25, -D / 2 - 0.015, 1.0), scale=(0.85, 0.01, 0.8), parent=r)
    boxes('UldStraps', [((0.25 + dx, -D / 2 - 0.03, 1.0), (0.025, 0.01, 0.8)) for dx in (-0.45, 0, 0.45)], EDGE, r)
    prim('cube', 'UldDocPocket', EDGE, loc=(-0.9, -D / 2 - 0.02, 1.3), scale=(0.12, 0.01, 0.16), parent=r)
    # รหัสตู้ + โลโก้ที่ด้านข้าง (+x) ทั้งสองข้าง
    for s, face in ((1, '+x'), (-1, '-x')):
        text('AKE 12345 SPU', 0.2, INK, (s * (W / 2 + 0.012), -0.05, 1.62), (math.radians(90), 0, s * math.radians(90)), r,
             extrude=0, name='UldCode')
        logo_decal('UldLogo', r, (s * (W / 2 + 0.012), -0.05, 1.0), 1.5, face)
    return r


# ---------------- เอกสาร + ตราประทับ ----------------
def docs():
    PAPER = mat('Paper', hexrgb(0xf4f0e2), 0.8)
    HEADER = mat('DocHeader', hexrgb(0x1d3f8a), 0.6)
    LINE = mat('DocLine', hexrgb(0x55595e), 0.7)
    RED = mat('SealRed', hexrgb(0xc8312b), 0.6)
    BLUE = mat('SealBlue', hexrgb(0x2f5fb5), 0.6)
    WOOD = mat('StampWood', hexrgb(0x7a4a2a), 0.6)
    PAD = mat('StampPad', hexrgb(0x2a2d31), 0.7)
    # เอกสารวางราบบนโต๊ะ: กว้าง 0.7 (x) ยาว 0.95 (y) หนา 0.03 · หัวกระดาษอยู่ด้าน +y (ไกลกล้อง) = -z ในเว็บ ตรงกับรุ่นเดิม
    d = root('Doc')
    prim('cube', 'DocPaper', PAPER, loc=(0, 0, 0.015), scale=(0.35, 0.475, 0.015), parent=d)
    prim('cube', 'Doc_Header', HEADER, loc=(0, 0.38, 0.032), scale=(0.35, 0.09, 0.004), parent=d)
    lines = [((0.12, 0.2 - k * 0.07, 0.032), (0.12 if k % 2 else 0.16, 0.012, 0.002)) for k in range(4)]
    lines += [((0.05, -0.12 - k * 0.07, 0.032), (0.2 if k % 2 else 0.24, 0.012, 0.002)) for k in range(3)]
    lines += [((0.18, -0.38, 0.032), (0.1, 0.012, 0.002))]
    boxes('DocLines', lines, LINE, d)
    # ตราวงกลมเรียบ ๆ 2 ดวง (แดง = ตราหน่วยงานรับรอง, น้ำเงิน = ตรากรม) ไม่ใช่ตราจริง
    prim('cylinder', 'DocSealRed', RED, loc=(-0.2, 0.15, 0.033), vertices=12, radius=0.08, depth=0.004, parent=d)
    prim('cylinder', 'DocSealBlue', BLUE, loc=(-0.2, -0.12, 0.033), vertices=12, radius=0.08, depth=0.004, parent=d)
    # ตราประทับ: ฐานสี่เหลี่ยม (หมึกดำ + กรอบไม้) + ด้ามจับทรงกลึง — ฐานอยู่ที่ z = 0
    s = root('Stamp'); s.location = (1.0, 0, 0)
    prim('cube', 'StampPad', PAD, loc=(0, 0, 0.03), scale=(0.18, 0.18, 0.03), parent=s)
    prim('cube', 'StampBase', WOOD, loc=(0, 0, 0.09), scale=(0.17, 0.17, 0.03), parent=s)
    lathe('StampHandle', [(0.01, 0.12), (0.06, 0.12), (0.05, 0.2), (0.05, 0.3), (0.09, 0.38), (0.08, 0.45), (0.01, 0.47)], WOOD, s, seg=8)
    return d


# ---------------- ถังออกซิเจน ----------------
def oxygen():
    GREEN = mat('O2Green', hexrgb(0x4f8a34), 0.45, 0.2)
    BRASS = mat('Brass', hexrgb(0xc9a23c), 0.3, 0.8)
    WHITE = mat('O2Text', hexrgb(0xf2f2f2), 0.5)
    r = root('Oxygen')
    R, H = 0.25, 1.6
    lathe('O2Body', [(0.01, 0.0), (R * 0.95, 0.0), (R, 0.04), (R, H - 0.35), (R * 0.85, H - 0.2), (R * 0.5, H - 0.1),
                     (0.07, H - 0.07), (0.01, H - 0.07)], GREEN, r, seg=12)
    prim('cylinder', 'ValveNeck', BRASS, loc=(0, 0, H - 0.02), vertices=8, radius=0.04, depth=0.1, parent=r)
    prim('cylinder', 'ValveWheel', BRASS, loc=(0, 0, H + 0.05), vertices=8, radius=0.07, depth=0.03, parent=r)
    prim('cube', 'ValveOutlet', BRASS, loc=(0.06, 0, H - 0.01), scale=(0.04, 0.02, 0.02), parent=r)
    text('OXYGEN', 0.09, WHITE, (0, -R - 0.006, 0.95), R90, r, extrude=0, name='O2Label')
    text('O2', 0.14, WHITE, (0, -R - 0.006, 0.78), R90, r, extrude=0, name='O2Symbol')
    return r


# ---------------- ถุงอาหารปลา ----------------
def feedbag():
    KRAFT = mat('Kraft', hexrgb(0xb79a6e), 0.85)
    INK = mat('FeedInk', hexrgb(0x2b2b2b), 0.6)
    ORANGE = mat('FeedOrange', hexrgb(0xe8662a), 0.5)
    WHITE = mat('FeedWhite', hexrgb(0xf4f4f4), 0.5)
    r = root('FeedBag')
    W, D, H = 0.7, 0.5, 0.9
    # ตัวถุง: หน้าตัดหกเหลี่ยม (ป่องกลาง) ยกขึ้นตามความสูง แล้วปลายบนบีบแบนเป็นปากถุงพับ
    def ring(z, w, d):
        return [(w / 2, 0), (w / 2 * 0.8, d / 2), (-w / 2 * 0.8, d / 2), (-w / 2, 0), (-w / 2 * 0.8, -d / 2), (w / 2 * 0.8, -d / 2)]
    levels = [(0.0, W * 0.9, D * 0.7), (0.08, W, D), (0.6, W, D), (0.75, W * 0.98, D * 0.35), (0.8, W * 0.98, 0.04)]
    bm = bmesh.new(); prev = None
    for z, w, dd in levels:
        cur = [bm.verts.new((x, y, z)) for x, y in ring(z, w, dd)]
        if prev:
            for k in range(6):
                bm.faces.new((prev[k], prev[(k + 1) % 6], cur[(k + 1) % 6], cur[k]))
        else:
            bm.faces.new(list(reversed(cur)))
        prev = cur
    bm.faces.new(prev)
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj_from_bmesh('FeedBody', bm, KRAFT, parent=r)
    prim('cube', 'FeedTop', KRAFT, loc=(0, 0, 0.85), scale=(W / 2 * 0.98, 0.025, 0.05), parent=r)
    # ฉลากด้านหน้า (-y): ตัวหนังสือ KOI FEED + ปลาคาร์ฟลายง่าย ๆ (ลำตัวขาว จุดส้ม หาง)
    FY = -D / 2 - 0.008
    text('KOI FEED', 0.11, INK, (0, FY, 0.52), R90, r, extrude=0, name='FeedText')
    prim('uv_sphere', 'FeedKoiBody', WHITE, loc=(0.02, FY, 0.3), segments=8, ring_count=4, radius=1, scale=(0.11, 0.005, 0.045), parent=r)
    prim('uv_sphere', 'FeedKoiSpot', ORANGE, loc=(0.05, FY - 0.004, 0.31), segments=8, ring_count=4, radius=1, scale=(0.04, 0.003, 0.03), parent=r)
    prim('cone', 'FeedKoiTail', WHITE, loc=(-0.12, FY, 0.3), rot=(math.radians(90), 0, math.radians(90)), vertices=3, radius1=0.05, depth=0.006, parent=r)
    return r


# ---------------- รั้ว 2 แบบ (ท่อนละ 2.5 ตามแกน x จุดกำเนิดกลางท่อน) ----------------
def fences():
    WOOD_D = mat('FenceWoodDark', hexrgb(0x7a4b2a), 0.8)
    WOOD_L = mat('FenceWoodLight', hexrgb(0xb07a48), 0.8)
    METAL = mat('FenceMetal', hexrgb(0x5d6a78), 0.5, 0.5)
    L, H = 2.5, 0.95
    w = root('Fence_Wood'); w.location = (0, -1, 0)
    boxes('FenceWoodPosts', [((s * (L / 2 - 0.07), 0, H / 2), (0.07, 0.07, H / 2)) for s in (1, -1)], WOOD_D, w)
    boxes('FenceWoodRails', [((0, -0.08, z), (L / 2 - 0.1, 0.03, 0.06)) for z in (0.25, 0.5, 0.75)], WOOD_L, w)
    m = root('Fence_Metal'); m.location = (0, 1, 0)
    bars = [((s * (L / 2 - 0.06), 0, H / 2), (0.06, 0.06, H / 2)) for s in (1, -1)]
    bars += [((0, 0, z), (L / 2 - 0.1, 0.02, 0.02)) for z in (0.15, 0.6, 0.8)]
    bars += [((-L / 2 + 0.25 + k * 0.2, 0, 0.46), (0.012, 0.012, 0.42)) for k in range(11)]
    boxes('FenceMetalBars', bars, METAL, m)
    bm = bmesh.new()                                            # หัวหอกปลายซี่
    for k in range(11):
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.025, radius2=0.0, depth=0.07)
        bmesh.ops.translate(bm, vec=(-L / 2 + 0.25 + k * 0.2, 0, 0.91), verts=res['verts'])
    obj_from_bmesh('FenceMetalSpikes', bm, METAL, parent=m)
    return w


# ---------------- ไม้กั้นด่าน ----------------
def gate():
    BOX = mat('GateBox', hexrgb(0x3a3f46), 0.5, 0.3)
    YEL = mat('GateYellow', hexrgb(0xe9b024), 0.5)
    RED = mat('GateRed', hexrgb(0xd9423e), 0.5)
    WHITE = mat('GateWhite', hexrgb(0xf4f4f4), 0.5)
    POST = mat('GatePost', hexrgb(0x4a5058), 0.5, 0.3)
    r = root('Gate')
    L = 3.0                                                     # ความยาวคาน (ยื่นไปด้าน -y ของ Blender = +z ในเว็บ)
    # ตู้เสาขับเคลื่อน (เทาเข้ม แถบเหลืองด้านหน้า) + ถ่วงน้ำหนักด้านหลัง
    bevel_box('GateHousing', (0.4, 0.4, 2.2), (0, 0.15, 1.1), BOX, r, 0.04)
    prim('cube', 'GateStripe', YEL, loc=(0, -0.055, 1.0), scale=(0.15, 0.01, 0.95), parent=r)
    bevel_box('GateWeight', (0.3, 0.3, 0.45), (0, 0.75, 2.1), BOX, r, 0.04)
    # คาน: ตัวแม่ว่าง Gate_Bar จุดหมุนที่เสาสูง 2.1 — เว็บหมุนรอบแกน x เพื่อยกคานขึ้น
    bar = empty('Gate_Bar', r, (0, 0, 2.1))
    n = 8
    for k in range(n):                                          # ลายแดงขาวสลับ
        prim('cube', 'BarSeg', RED if k % 2 == 0 else WHITE, loc=(0, -(k + 0.5) * L / n, 0), scale=(0.05, L / n / 2, 0.06), parent=bar)
    # ป้าย STOP / หยุดตรวจ กลางคาน
    prim('cylinder', 'StopSign', RED, loc=(0.07, -L * 0.5, 0), rot=(0, math.radians(90), 0), vertices=16, radius=0.32, depth=0.02, parent=bar)
    prim('cylinder', 'StopFace', WHITE, loc=(0.085, -L * 0.5, 0), rot=(0, math.radians(90), 0), vertices=16, radius=0.27, depth=0.01, parent=bar)
    text('STOP', 0.13, RED, (0.095, -L * 0.5, 0.07), (math.radians(90), 0, math.radians(90)), bar, extrude=0, name='StopText')
    text('หยุดตรวจ', 0.11, RED, (0.095, -L * 0.5, -0.08), (math.radians(90), 0, math.radians(90)), bar, extrude=0,
         name='StopThai', font=THAI_FONT)
    # เสารับปลายคาน (รูปตัว Y)
    prim('cube', 'RestPost', POST, loc=(0, -L + 0.05, 0.95), scale=(0.05, 0.05, 0.95), parent=r)
    boxes('RestFork', [((s * 0.08, -L + 0.05, 2.0), (0.02, 0.04, 0.12)) for s in (1, -1)], POST, r)
    prim('cube', 'RestFoot', POST, loc=(0, -L + 0.05, 0.03), scale=(0.15, 0.15, 0.03), parent=r)
    return r


ITEMS = [('pond.glb', pond), ('table.glb', table), ('conveyor.glb', conveyor), ('uld.glb', uld), ('docs.glb', docs),
         ('oxygen.glb', oxygen), ('feedbag.glb', feedbag), ('fences.glb', fences), ('gate.glb', gate)]
ONLY = os.environ.get('KOI_ONLY')            # ตั้งค่าเพื่อสร้างชิ้นเดียว เช่น KOI_ONLY=gate
for fname, build in ITEMS:
    if ONLY and not fname.startswith(ONLY):
        continue
    reset(); build(); export_glb(fname)
