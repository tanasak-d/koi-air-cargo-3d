# บรรยากาศกลุ่ม 5 (ปั้นใหม่ 1 พ.ย. 2026 ตามภาพใน โมเดล/Group 5/) ส่งออก 3 ไฟล์:
#   japan.glb  ฝั่งญี่ปุ่น: JP_Fuji ภูเขาไฟฟูจิ (ฉากหลัง) · JP_Torii เสาโทริอิ · JP_Lantern โคมหิน · JP_Sakura ซากุระ
#              JP_Pine สนญี่ปุ่นทรงบอนไซ · JP_Bamboo กอไผ่ในกระบะ
#   thai.glb   ฝั่งไทย: TH_Chedi เจดีย์ทอง (ฉากหลัง) · TH_Palm มะพร้าว · TH_SpiritHouse ศาลพระภูมิ · TH_Banana กล้วย
#              TH_Sala ศาลาทรงไทย · TH_House เรือนไทยใต้ถุนสูง (ฟาร์มบริษัทในไทย)
#   trees.glb  ต้นไม้ทั่วไป: Tree_Pine สน · Tree_Round พุ่มกลม
# ทุกชิ้นวางฐานที่ z = 0 ตรงจุดกำเนิดของตัวเอง (เว็บหยิบไปวางตามชื่อ) · ด้านหน้า = -Y ของ Blender (= +z ในเว็บ)
# ขนาดใกล้รุ่นเดิม เพราะฉากกำหนดระยะกันชนของแต่ละชิ้นไว้แล้ว · ปั้นแบบประหยัดไฟล์ (เหลี่ยมน้อย รวมชิ้นเล็กเป็นเมชเดียว)
import bpy, bmesh, math, random, sys, os
from mathutils import Matrix
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, boxes, obj_from_bmesh, lathe


def blobs(name, parent, items, material, sub=1):
    """ก้อนทรงไอโคสเฟียร์หยาบ ๆ หลายก้อนรวมเป็นเมชเดียว (พุ่มใบ ดอกซากุระ) items = [(ศูนย์กลาง, (sx, sy, sz))]"""
    bm = bmesh.new()
    for (cx, cy, cz), (sx, sy, sz) in items:
        res = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
        bmesh.ops.transform(bm, matrix=Matrix.Diagonal((sx, sy, sz, 1)), verts=res['verts'])
        bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=res['verts'])
    return obj_from_bmesh(name, bm, material, parent=parent)


def tubes(name, parent, segs, material, sides=6):
    """ท่อนกลม (ลำต้น กิ่ง ลำไผ่) หลายท่อนรวมเป็นเมชเดียว segs = [(จุดล่าง, จุดบน, รัศมีล่าง, รัศมีบน)]"""
    bm = bmesh.new()
    for a, b, r0, r1 in segs:
        ax, ay, az = a; bx, by, bz = b
        dx, dy, dz = bx - ax, by - ay, bz - az
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=sides, radius1=r0, radius2=r1, depth=L)
        # กรวยตั้งตามแกน z ที่จุดกลาง: หมุนให้ชี้ตามทิศ a→b แล้วย้ายไปจุดกลาง
        from mathutils import Vector
        rot = Vector((0, 0, 1)).rotation_difference(Vector((dx, dy, dz)).normalized()).to_matrix().to_4x4()
        bmesh.ops.transform(bm, matrix=rot, verts=res['verts'])
        bmesh.ops.translate(bm, vec=((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2), verts=res['verts'])
    return obj_from_bmesh(name, bm, material, parent=parent)


def prism_roof(name, w, d, rise, z, material, parent, overhang=0.3, flare=0.0):
    """หลังคาจั่วทรงปริซึมสามเหลี่ยม (สันตามแกน x) เป็นเมชเดียว · flare = ปลายจั่วยื่นยาวกว่าชายคา (หลังคาไทย)"""
    hw, hd = w / 2 + overhang, d / 2 + overhang
    bm = bmesh.new()
    ends = []
    for s in (-1, 1):
        x = s * (hw + flare)
        ends.append([bm.verts.new((x, -hd, z)), bm.verts.new((x, hd, z)), bm.verts.new((s * hw, 0, z + rise))])
    a, b = ends
    bm.faces.new((a[0], b[0], b[2], a[2])); bm.faces.new((a[1], a[2], b[2], b[1]))
    bm.faces.new((a[0], a[2], a[1])); bm.faces.new((b[0], b[1], b[2]))
    bm.faces.new((a[0], a[1], b[1], b[0]))
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return obj_from_bmesh(name, bm, material, parent=parent)


# ================= ญี่ปุ่น =================
def japan():
    RED = mat('ToriiRed', hexrgb(0xc8382a), 0.5); BLACK = mat('ToriiBlack', hexrgb(0x2a2a2a), 0.6)
    STONE = mat('LanternStone', hexrgb(0xa49e93), 0.95); LIGHT = mat('LanternLight', hexrgb(0xf7d36a), 0.4)
    BARK = mat('JBark', hexrgb(0x5e4130), 0.9); PINE_BARK = mat('JPineBark', hexrgb(0x6b6458), 0.9)
    PINK = mat('Sakura', hexrgb(0xf2a7c3), 0.8); PINK2 = mat('Sakura2', hexrgb(0xf8c6d8), 0.8)
    PINE = mat('JPine', hexrgb(0x2f6138), 0.85)
    ROCK = mat('FujiRock', hexrgb(0x4d5f8f), 0.95); SNOW = mat('Snow', hexrgb(0xf7f9fb), 0.7)
    BAMBOO = mat('Bamboo', hexrgb(0x5f9a3c), 0.6); PLANTER = mat('Planter', hexrgb(0x3a3f45), 0.8)
    random.seed(8)

    # ภูเขาไฟฟูจิ (ฉากหลังขนาดใหญ่ สีน้ำเงินเทา ยอดหิมะขอบหยัก)
    f = root('JP_Fuji')
    prim('cone', 'Mountain', ROCK, loc=(0, 0, 14), vertices=14, radius1=42, radius2=4, depth=28, parent=f)
    bm = bmesh.new()                                         # หมวกหิมะ: วงล่างหยักขึ้นลงสลับกัน
    n = 14
    top = bm.verts.new((0, 0, 28.3))
    low = []
    for k in range(n * 2):
        a = math.pi * k / n
        rr, zz = (14.5, 21.0) if k % 2 == 0 else (11.5, 22.8)
        low.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, zz)))
    for k in range(n * 2):
        bm.faces.new((low[k], low[(k + 1) % (n * 2)], top))
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj_from_bmesh('SnowCap', bm, SNOW, parent=f)

    # เสาโทริอิ: เสาแดง 2 ต้น ฐานดำ คานบนดำปลายงอน (คาซางิ) คานรองแดง คานล่างแดง
    t = root('JP_Torii')
    tubes('Pillars', t, [((x, 0, 0), (x * 0.94, 0, 4.25), 0.2, 0.17) for x in (-1.6, 1.6)], RED, sides=8)
    tubes('PillarBases', t, [((x, 0, 0), (x, 0, 0.35), 0.26, 0.26) for x in (-1.6, 1.6)], BLACK, sides=8)
    boxes('ToriiRed', [((0, 0, 4.1), (2.35, 0.18, 0.13)), ((0, 0, 3.35), (2.1, 0.13, 0.11)), ((0, 0, 3.75), (0.12, 0.12, 0.3))], RED, t)
    boxes('Kasagi', [((0, 0, 4.42), (2.3, 0.28, 0.15))], BLACK, t)
    for s in (1, -1):                                        # ปลายคาซางิงอนขึ้นทั้งสองข้าง
        prim('cube', 'KasagiTip', BLACK, loc=(s * 2.65, 0, 4.52), rot=(0, s * math.radians(-12), 0), scale=(0.45, 0.28, 0.14), parent=t)

    # โคมหิน: ฐานหกเหลี่ยม เสา ห้องไฟ (ช่องแสงสีเหลือง) หลังคาหกเหลี่ยม ยอดแหลม
    l = root('JP_Lantern')
    prim('cylinder', 'Foot', STONE, loc=(0, 0, 0.12), vertices=6, radius=0.42, depth=0.24, parent=l)
    prim('cylinder', 'Post', STONE, loc=(0, 0, 0.62), vertices=6, radius=0.15, depth=0.8, parent=l)
    prim('cylinder', 'Saddle', STONE, loc=(0, 0, 1.07), vertices=6, radius=0.36, depth=0.12, parent=l)
    prim('cube', 'FireBox', STONE, loc=(0, 0, 1.33), scale=(0.25, 0.25, 0.2), parent=l)
    boxes('LanternWindows', [((0, -0.255, 1.33), (0.13, 0.01, 0.12)), ((0, 0.255, 1.33), (0.13, 0.01, 0.12)),
                             ((0.255, 0, 1.33), (0.01, 0.13, 0.12)), ((-0.255, 0, 1.33), (0.01, 0.13, 0.12))], LIGHT, l)
    prim('cone', 'Hat', STONE, loc=(0, 0, 1.68), vertices=6, radius1=0.55, radius2=0.08, depth=0.36, parent=l)
    prim('uv_sphere', 'Finial', STONE, loc=(0, 0, 1.92), segments=6, ring_count=4, radius=0.09, parent=l)

    # ซากุระ: ลำต้นแตกกิ่ง 3 กิ่ง + พุ่มดอกชมพู 2 โทน
    s_ = root('JP_Sakura')
    tubes('SakuraTrunk', s_, [((0, 0, 0), (0.1, 0, 1.6), 0.22, 0.16), ((0.1, 0, 1.6), (-0.7, 0.1, 2.6), 0.14, 0.08),
                              ((0.1, 0, 1.6), (0.8, -0.1, 2.5), 0.13, 0.07), ((0.1, 0, 1.6), (0.15, 0.3, 2.9), 0.12, 0.07)], BARK)
    blobs('Blossom', s_, [((-0.7, 0.1, 2.9), (0.85, 0.8, 0.7)), ((0.8, -0.1, 2.85), (0.8, 0.75, 0.68)),
                          ((0.1, 0.2, 3.3), (0.95, 0.9, 0.8))], PINK)
    blobs('Blossom2', s_, [((-0.2, -0.5, 3.0), (0.6, 0.55, 0.5)), ((0.5, 0.5, 3.1), (0.55, 0.5, 0.48))], PINK2)

    # สนญี่ปุ่นทรงบอนไซ: ลำต้นคดเอียง + แผงใบแบน 4 ชั้น
    p = root('JP_Pine')
    tubes('PineTrunk', p, [((0, 0, 0), (0.35, 0, 1.2), 0.2, 0.16), ((0.35, 0, 1.2), (-0.2, 0, 2.3), 0.16, 0.12),
                           ((-0.2, 0, 2.3), (0.2, 0, 3.3), 0.12, 0.08), ((0.35, 0, 1.2), (1.1, 0, 1.7), 0.09, 0.05),
                           ((-0.2, 0, 2.3), (-1.0, 0, 2.6), 0.08, 0.05)], PINE_BARK)
    blobs('PinePads', p, [((1.15, 0, 1.85), (0.75, 0.6, 0.24)), ((-1.0, 0, 2.75), (0.8, 0.65, 0.25)),
                          ((0.25, 0, 3.45), (0.85, 0.7, 0.28)), ((0.0, 0, 2.6), (0.5, 0.45, 0.2))], PINE)

    # กอไผ่ในกระบะสี่เหลี่ยม (ยาวตามแกน x ราว 3.6)
    b = root('JP_Bamboo')
    prim('cube', 'Planter', PLANTER, loc=(0, 0, 0.2), scale=(1.8, 0.4, 0.2), parent=b)
    poles, nodes = [], []
    for k in range(12):
        x = -1.6 + k * 0.29 + random.uniform(-0.05, 0.05); y = random.uniform(-0.2, 0.2); h = random.uniform(2.0, 3.2)
        poles.append(((x, y, 0.35), (x, y, h), 0.05, 0.04))
        nodes += [((x, y, z), (0.06, 0.06, 0.02)) for z in (0.9, 1.6, 2.3) if z < h]
    tubes('BambooPoles', b, poles, BAMBOO)
    boxes('BambooNodes', nodes, mat('BambooNode', hexrgb(0x4a7c2e), 0.6), b)


# ================= ไทย =================
def thai():
    GOLD = mat('Gold', hexrgb(0xe2b23c), 0.35, 0.5); WHITE = mat('ThaiWhite', hexrgb(0xf2efe8), 0.8)
    STONE = mat('ThaiStone', hexrgb(0xb9bbbd), 0.9)
    ROOF = mat('RoofTeak', hexrgb(0x8a4f2a), 0.6); ROOF_D = mat('RoofDark', hexrgb(0x5a3a26), 0.65)
    TEAK = mat('Teak', hexrgb(0x7a4a2a), 0.75); BARK = mat('PalmBark', hexrgb(0x7a5a3c), 0.9)
    FROND = mat('Frond', hexrgb(0x3f8f3a), 0.8); BANANA = mat('Banana', hexrgb(0x6aa83c), 0.7)
    STEM = mat('BananaStem', hexrgb(0x8fa35a), 0.8); FRUIT = mat('BananaFruit', hexrgb(0xe6d24a), 0.6)
    FLOWER = mat('BananaFlower', hexrgb(0x7a2a5a), 0.6); NUT = mat('Coconut', hexrgb(0x6b5a2e), 0.8)
    GLASS = mat('HouseGlass', hexrgb(0x5f9ea0), 0.15, 0.3)
    random.seed(9)

    # เจดีย์ทอง (ฉากหลัง): ฐานสี่เหลี่ยมขาวซ้อน 2 ชั้น + บันไดหน้า + ทรงระฆังเหลี่ยมทอง + ปล้องไฉน + ยอดแหลม
    ch = root('TH_Chedi')
    boxes('ChediBase', [((0, 0, 0.6), (6.0, 6.0, 0.6)), ((0, 0, 1.6), (4.8, 4.8, 0.4))], WHITE, ch)
    prim('cube', 'ChediStairs', STONE, loc=(0, -5.4, 0.8), rot=(math.radians(-35), 0, 0), scale=(1.0, 1.2, 0.3), parent=ch)
    lathe('ChediBody', [(0.01, 2.0), (4.0, 2.0), (4.0, 2.6), (3.4, 2.6), (3.4, 3.1), (3.6, 4.2), (3.3, 5.6), (2.5, 6.8),
                        (1.2, 7.4), (1.2, 7.8), (0.9, 7.8), (0.9, 9.4), (0.5, 10.2), (0.3, 12.5), (0.05, 15.5), (0.01, 15.6)],
          GOLD, ch, seg=8)

    # มะพร้าว: ลำต้นโค้ง (ต่อหลายท่อน) + ใบห้อย 8 ใบ (แต่ละใบพับ 2 ช่วง) + ลูกมะพร้าว
    pa = root('TH_Palm')
    pts = [(0.0, 0, 0.0), (0.15, 0, 1.4), (0.45, 0, 2.8), (0.85, 0, 4.1), (1.2, 0, 5.3), (1.45, 0, 6.2)]
    tubes('PalmTrunk', pa, [(pts[k], pts[k + 1], 0.22 - k * 0.02, 0.2 - k * 0.02) for k in range(len(pts) - 1)], BARK)
    tx, _, tz = pts[-1]
    bm = bmesh.new()
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.2
        ca, sa = math.cos(a), math.sin(a)
        # ใบหนึ่งใบ = แผ่นแคบ 2 ช่วง: ช่วงแรกชี้ออกเฉียงขึ้น ช่วงสองห้อยลง
        p0 = (tx, 0, tz); p1 = (tx + ca * 1.3, sa * 1.3, tz + 0.35); p2 = (tx + ca * 2.4, sa * 2.4, tz - 0.6)
        wv = (-sa * 0.3, ca * 0.3, 0)
        v = [bm.verts.new((p[0] + s * wv[0] * wid, p[1] + s * wv[1] * wid, p[2])) for p, wid in ((p0, 0.3), (p1, 1.0), (p2, 0.2)) for s in (-1, 1)]
        bm.faces.new((v[0], v[1], v[3], v[2])); bm.faces.new((v[2], v[3], v[5], v[4]))
    bm.normal_update()
    fr = obj_from_bmesh('Fronds', bm, FROND, parent=pa)
    fr.data.materials[0].use_backface_culling = False
    blobs('Coconuts', pa, [((tx + 0.15, 0.12, tz - 0.25), (0.15, 0.15, 0.15)), ((tx - 0.12, 0.08, tz - 0.3), (0.15, 0.15, 0.15)),
                           ((tx + 0.02, -0.15, tz - 0.28), (0.15, 0.15, 0.15))], NUT, sub=1)

    # ศาลพระภูมิ: เสาขาวคาดทอง แท่นทอง ตัวศาลไม้ขอบทอง หลังคาจั่วไทยปลายงอน ช่อฟ้าทอง
    sp = root('TH_SpiritHouse')
    prim('cube', 'SpiritBase', WHITE, loc=(0, 0, 0.1), scale=(0.35, 0.35, 0.1), parent=sp)
    prim('cylinder', 'Pedestal', WHITE, loc=(0, 0, 0.75), vertices=8, radius=0.16, depth=1.2, parent=sp)
    boxes('PedestalBands', [((0, 0, 0.35), (0.19, 0.19, 0.03)), ((0, 0, 1.2), (0.19, 0.19, 0.03))], GOLD, sp)
    prim('cube', 'Deck', GOLD, loc=(0, 0, 1.4), scale=(0.6, 0.6, 0.05), parent=sp)
    prim('cube', 'Shrine', TEAK, loc=(0, 0, 1.75), scale=(0.38, 0.38, 0.3), parent=sp)
    boxes('ShrineTrim', [((sx * 0.4, sy * 0.4, 1.75), (0.03, 0.03, 0.32)) for sx in (1, -1) for sy in (1, -1)] +
          [((0, -0.385, 1.72), (0.14, 0.01, 0.2))], GOLD, sp)
    prism_roof('ShrineRoof', 0.76, 0.76, 0.6, 2.05, ROOF, sp, overhang=0.12, flare=0.08)
    for s in (1, -1):
        prim('cone', 'Chofa', GOLD, loc=(s * 0.55, 0, 2.7), rot=(0, s * math.radians(-30), 0), vertices=4, radius1=0.05, depth=0.3, parent=sp)

    # ต้นกล้วย: ลำต้นเป็นกาบ (ทรงกรวยต่อกัน) + ใบใหญ่ 6 ใบโค้งออก + เครือกล้วย + ปลี
    ba = root('TH_Banana')
    tubes('BananaStem', ba, [((0, 0, 0), (0, 0, 1.0), 0.2, 0.16), ((0, 0, 1.0), (0, 0, 2.0), 0.16, 0.12)], STEM, sides=7)
    bm = bmesh.new()
    for k in range(6):
        a = 2 * math.pi * k / 6
        ca, sa = math.cos(a), math.sin(a)
        p0 = (0, 0, 2.0); p1 = (ca * 0.9, sa * 0.9, 2.9); p2 = (ca * 1.8, sa * 1.8, 2.6)
        wv = (-sa, ca)
        v = [bm.verts.new((p[0] + s * wv[0] * wid, p[1] + s * wv[1] * wid, p[2])) for p, wid in ((p0, 0.05), (p1, 0.35), (p2, 0.08)) for s in (-1, 1)]
        bm.faces.new((v[0], v[1], v[3], v[2])); bm.faces.new((v[2], v[3], v[5], v[4]))
    bm.normal_update()
    lv = obj_from_bmesh('BananaLeaves', bm, BANANA, parent=ba)
    lv.data.materials[0].use_backface_culling = False
    blobs('BananaBunch', ba, [((0.25, -0.15, 1.8), (0.14, 0.12, 0.22)), ((0.3, -0.1, 1.55), (0.12, 0.11, 0.18))], FRUIT)
    blobs('BananaFlower', ba, [((0.3, -0.15, 1.3), (0.07, 0.07, 0.13))], FLOWER)

    # ศาลาทรงไทย: ฐานหิน เสาขาว 4 ต้น (โคนทอง) หลังคาจั่วซ้อน 2 ชั้นไม้สักขอบขาว ปลายจั่วงอน ช่อฟ้าทอง
    sa_ = root('TH_Sala')
    boxes('SalaBase', [((0, 0, 0.15), (2.2, 1.7, 0.15)), ((0, -1.95, 0.08), (0.8, 0.25, 0.08))], STONE, sa_)
    tubes('SalaColumns', sa_, [((x, y, 0.3), (x, y, 2.9), 0.12, 0.11) for x in (-1.7, 1.7) for y in (-1.2, 1.2)], WHITE, sides=8)
    boxes('ColumnFeet', [((x, y, 0.4), (0.15, 0.15, 0.1)) for x in (-1.7, 1.7) for y in (-1.2, 1.2)], GOLD, sa_)
    boxes('SalaBeams', [((0, s * 1.2, 2.95), (1.85, 0.08, 0.1)) for s in (1, -1)], TEAK, sa_)
    prism_roof('SalaRoof1', 3.8, 2.8, 1.0, 3.0, ROOF, sa_, overhang=0.45, flare=0.2)
    prism_roof('SalaRoof2', 2.8, 2.0, 1.5, 3.7, ROOF_D, sa_, overhang=0.25, flare=0.3)
    boxes('RoofTrim', [((0, s * 1.85, 3.02), (2.35, 0.04, 0.04)) for s in (1, -1)], WHITE, sa_)
    for s in (1, -1):
        prim('cone', 'Chofa', GOLD, loc=(s * 1.9, 0, 5.3), rot=(0, s * math.radians(-35), 0), vertices=4, radius1=0.07, depth=0.5, parent=sa_)

    # เรือนไทยใต้ถุนสูง (ฟาร์มบริษัท): เสาสูง ชานไม้ ห้องไม้สักผนังหน้ากระจก หลังคาจั่วสูงชันปลายงอน ราวระเบียง บันได
    th = root('TH_House')
    tubes('Stilts', th, [((x, y, 0), (x, y, 2.0), 0.15, 0.15) for x in (-3.6, -1.2, 1.2, 3.6) for y in (-2.4, 2.4)], TEAK, sides=6)
    prim('cube', 'Platform', TEAK, loc=(0, -0.6, 2.05), scale=(4.2, 3.4, 0.1), parent=th)
    prim('cube', 'Room', TEAK, loc=(0, 0.8, 3.4), scale=(3.8, 1.9, 1.3), parent=th)
    prim('cube', 'GlassFront', GLASS, loc=(0, -1.115, 3.35), scale=(2.4, 0.02, 1.0), parent=th)
    boxes('GlassMullions', [((x, -1.13, 3.35), (0.04, 0.02, 1.0)) for x in (-2.4, -1.2, 0, 1.2, 2.4)], ROOF_D, th)
    prism_roof('HouseRoof', 7.6, 3.8, 3.0, 4.7, ROOF_D, th, overhang=0.6, flare=0.5)
    rails = [((0, -3.95, 2.5), (4.1, 0.04, 0.04))] + [((s * 4.15, -2.2, 2.5), (0.04, 1.8, 0.04)) for s in (1, -1)]
    rails += [((x, -3.95, 2.3), (0.04, 0.04, 0.25)) for x in (-4.1, -2.05, 2.05, 4.1)]
    boxes('DeckRails', rails, TEAK, th)
    prim('cube', 'Stairs', TEAK, loc=(0, -4.6, 1.0), rot=(math.radians(-40), 0, 0), scale=(0.7, 0.12, 1.45), parent=th)


# ================= ต้นไม้ทั่วไป =================
def trees():
    BARK = mat('Bark', hexrgb(0x6e4c32), 0.9)
    PINE = mat('PineLeaf', hexrgb(0x2f6b3a), 0.8)
    LEAF = mat('Leaf', hexrgb(0x4f8a3c), 0.8)
    a = root('Tree_Pine'); a.location = (-1.5, 0, 0)
    tubes('Pine_Trunk', a, [((0, 0, 0), (0, 0, 1.0), 0.15, 0.12)], BARK, sides=6)
    bm = bmesh.new()                                         # ใบสน 5 ชั้นซ้อน (กรวย 8 เหลี่ยม เล็กลงทีละชั้น)
    for k, (rad, z) in enumerate([(1.2, 0.9), (1.0, 1.45), (0.82, 1.95), (0.62, 2.45), (0.4, 2.95)]):
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=rad, radius2=0.02 if k == 4 else rad * 0.35, depth=0.75)
        bmesh.ops.translate(bm, vec=(0, 0, z + 0.375), verts=res['verts'])
    obj_from_bmesh('Pine_Leaves', bm, PINE, parent=a)
    b = root('Tree_Round'); b.location = (1.5, 0, 0)
    tubes('Round_Trunk', b, [((0, 0, 0), (0, 0, 1.7), 0.14, 0.11)], BARK, sides=6)
    blobs('Round_Leaves', b, [((0, 0, 2.5), (1.05, 1.05, 1.0))], LEAF, sub=2)


reset(); japan(); export_glb('japan.glb')
reset(); thai(); export_glb('thai.glb')
reset(); trees(); export_glb('trees.glb')
