# อาคารกลุ่ม 3 (ปั้นใหม่ 1 พ.ย. 2026 ตามภาพใน โมเดล/Group 3/) ส่งออกทีละไฟล์:
#   warehouse.glb  คลังสินค้าสัตว์มีชีวิต ใช้ทั้งนาริตะและสุวรรณภูมิ (ประตูม้วน RollerDoor ด้านหน้า)
#   xray.glb       เครื่อง X-ray สายพาน (อุโมงค์ตามแกน x · ScanLight = แถบไฟสแกนในอุโมงค์)
#   farmhouse.glb  บ้านฟาร์มแบบญี่ปุ่น ผนังขาว โครงไม้เข้ม หลังคาจั่วกระเบื้องเทา ป้าย 鯉 (ปลาคาร์ฟ)
#   dof.glb        อาคารด่านตรวจสัตว์น้ำ กรมประมง (ป้ายภาษาไทย + อังกฤษ)
#   terminal.glb   อาคารผู้โดยสาร ฉากหลังสนามบิน (ใหม่) หลังคาโค้ง ผนังกระจก หอบังคับการบิน งวงช้าง 2 ตัว
# ป้ายที่สลับตามสนามบิน (มาร์ชเลือก 1 พ.ย. 2026): คลังสินค้าและอาคารผู้โดยสารมีป้าย 2 ชุดในไฟล์เดียว
#   Sign_NRT (นาริตะ) / Sign_BKK (สุวรรณภูมิ) — โค้ดในเว็บซ่อนป้ายที่ไม่ใช่สนามบินนั้น
# ตราหน่วยงานใช้วงกลมเรียบ ๆ (ไม่ใช่ตราจริง) ตามที่มาร์ชเลือก
# แกน: Blender -y = ด้านหน้าในเว็บ (+z หันเข้ากล้อง) · ฐานอยู่ที่ z = 0
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import (reset, mat, hexrgb, prim, root, export_glb, bevel_box, empty, text, boxes, emblem,
                    obj_from_bmesh, THAI_FONT)

JP_FONT = 'C:/Windows/Fonts/msgothic.ttc'      # ฟอนต์ญี่ปุ่นของ Windows (สำหรับตัวคันจิ 鯉 บนป้ายบ้านฟาร์ม)
R90 = (math.radians(90), 0, 0)                  # หมุนตัวอักษรให้ตั้งขึ้นหันไปด้าน -y


def sign_pair(parent, loc, size, nrt, bkk, board_scale, board_mat, ink):
    """ป้าย 2 ชุดที่ตำแหน่งเดียวกัน: Sign_NRT / Sign_BKK (โค้ดในเว็บโชว์ทีละชุดตามสนามบิน)"""
    for nm, body in (('Sign_NRT', nrt), ('Sign_BKK', bkk)):
        g = empty(nm, parent, loc)
        prim('cube', nm + '_Board', board_mat, loc=(0, 0, 0), scale=board_scale, parent=g)
        text(body, size, ink, (0, -board_scale[1] - 0.012, 0), R90, g, extrude=0, name=nm + '_Text')


# ---------------- คลังสินค้าสัตว์มีชีวิต ----------------
def warehouse():
    PANEL = mat('WhPanel', hexrgb(0xc9ced5), 0.6, 0.3)
    RIB = mat('WhRib', hexrgb(0xb3bac3), 0.55, 0.4)
    FRAME = mat('WhFrame', hexrgb(0x41607e), 0.5)
    DOOR = mat('RollerDoor', hexrgb(0x5d6470), 0.45, 0.5)
    SLAT = mat('Slat', hexrgb(0x454b55), 0.45, 0.5)
    INSIDE = mat('Inside', hexrgb(0x5a616c), 0.9)
    CONC = mat('Dock', hexrgb(0xa9b0b8), 0.9)
    LAMP = mat('WallLamp', hexrgb(0xfff2c0), 0.3)
    WHITE = mat('SignText', hexrgb(0xffffff), 0.5)
    W, D, H = 12.0, 8.0, 6.0                       # กว้าง (x) ลึก (y) สูง — เท่ารุ่นเดิม ฉากผูกไว้
    DW, DH = 2.2, 3.8                              # ครึ่งความกว้าง / ความสูงช่องประตู (รถลากวิ่งเข้าได้)
    r = root('Warehouse')
    # ผนังจริง (มีช่องประตูด้านหน้า) + หลังคาลาดเล็กน้อยไปด้านหลัง
    boxes('Walls', [((0, D / 2 - 0.1, H / 2), (W / 2, 0.1, H / 2))] +
          [((s * (W / 2 - 0.1), 0, H / 2), (0.1, D / 2, H / 2)) for s in (1, -1)] +
          [((s * (W / 4 + DW / 2), -D / 2 + 0.1, H / 2), ((W / 2 - DW) / 2, 0.1, H / 2)) for s in (1, -1)] +
          [((0, -D / 2 + 0.1, (H + DH) / 2), (DW, 0.1, (H - DH) / 2))], PANEL, r)
    roof = prim('cube', 'Roof', PANEL, loc=(0, 0, H + 0.1), rot=(math.radians(-3), 0, 0), scale=(W / 2 + 0.2, D / 2 + 0.2, 0.08), parent=r)
    # ข้างในมืด (มองผ่านประตูเห็นเป็นห้องลึก)
    prim('cube', 'InsideBack', INSIDE, loc=(0, D / 2 - 0.25, H / 2), scale=(W / 2 - 0.25, 0.04, H / 2 - 0.15), parent=r)
    # ลอนผนัง (ซี่แนวตั้ง) ด้านหน้าและด้านข้าง — รวมเป็นเมชเดียว
    ribs = []
    for i in range(int(W / 0.6) + 1):
        x = -W / 2 + 0.3 + i * 0.6
        if abs(x) < DW + 0.15 or abs(x) > W / 2 - 0.3:
            continue
        ribs.append(((x, -D / 2 - 0.03, H / 2), (0.05, 0.03, H / 2 - 0.1)))
    for i in range(int(D / 0.6)):
        y = -D / 2 + 0.6 + i * 0.6
        for s in (1, -1):
            ribs.append(((s * (W / 2 + 0.03), y, H / 2), (0.03, 0.05, H / 2 - 0.1)))
    boxes('Ribs', ribs, RIB, r)
    # โครงสีน้ำเงินเทา: เสามุม 4 ต้น + คานรอบอาคารระดับป้าย + ขอบหลังคา
    frame = [((sx * (W / 2 + 0.05), sy * (D / 2 + 0.05), H / 2), (0.18, 0.18, H / 2)) for sx in (1, -1) for sy in (1, -1)]
    frame += [((0, -D / 2 - 0.08, 4.1), (W / 2 + 0.1, 0.1, 0.32)), ((0, D / 2 + 0.08, 4.1), (W / 2 + 0.1, 0.1, 0.32))]
    frame += [((s * (W / 2 + 0.08), 0, 4.1), (0.1, D / 2 + 0.1, 0.32)) for s in (1, -1)]
    frame += [((0, 0, 0.12), (W / 2 + 0.1, D / 2 + 0.1, 0.12))]
    boxes('Frame', frame, FRAME, r)
    prim('cube', 'RoofTrim', FRAME, loc=(0, -D / 2 - 0.2, H + 0.25), scale=(W / 2 + 0.25, 0.08, 0.2), parent=r)
    # ประตูม้วน: ตัวแม่ชื่อ RollerDoor จุดหมุนที่ "ขอบบน" ของประตู — เว็บย่อความสูง (scale) เพื่อม้วนประตูขึ้น
    roller = empty('RollerDoor', r, loc=(0, -D / 2 - 0.04, DH))
    prim('cube', 'Door', DOOR, loc=(0, 0, -DH / 2), scale=(DW, 0.04, DH / 2), parent=roller)
    boxes('DoorSlats', [((0, -0.05, -DH + 0.25 + k * 0.3), (DW, 0.01, 0.02)) for k in range(12)], SLAT, roller)
    boxes('DoorFrame', [((s * (DW + 0.1), -D / 2 - 0.1, DH / 2), (0.1, 0.1, DH / 2)) for s in (1, -1)] +
          [((0, -D / 2 - 0.15, DH + 0.15), (DW + 0.2, 0.15, 0.15))], SLAT, r)
    # ป้ายบนคานด้านหน้า (สลับตามสนามบิน) + ตราวงกลมเรียบ ๆ ทางซ้าย
    sign_pair(r, (0.8, -D / 2 - 0.2, 4.1), 0.36, 'LIVE ANIMAL CARGO  |  NRT', 'LIVE ANIMAL CARGO  |  BKK',
              (3.9, 0.03, 0.26), FRAME, WHITE)
    emblem('Emblem', r, (-4.4, -D / 2 - 0.22, 4.1), 0.45)
    # ไฟส่องผนัง 2 ดวงมุมบน + ประตูเล็กด้านข้าง
    for x in (-5.2, 5.2):
        prim('cube', 'WallLamp', LAMP, loc=(x, -D / 2 - 0.12, 5.4), scale=(0.18, 0.1, 0.08), parent=r)
    prim('cube', 'SideDoor', DOOR, loc=(W / 2 + 0.06, 2.6, 1.05), scale=(0.02, 0.45, 1.05), parent=r)
    prim('cube', 'Apron', CONC, loc=(0, -D / 2 - 1.0, 0.02), scale=(DW + 1.0, 1.0, 0.02), parent=r)
    return r


# ---------------- เครื่อง X-ray ----------------
def xray():
    BODY = mat('XrayBody', hexrgb(0x8e98a5), 0.45, 0.3)
    BAND = mat('XrayBand', hexrgb(0x4f6c8f), 0.45, 0.3)
    DARK = mat('XrayDark', hexrgb(0x2c323b), 0.6)
    CURTAIN = mat('Curtain', hexrgb(0x15181c), 0.8, alpha=0.85)
    PANEL = mat('XrayPanel', hexrgb(0xb7bec7), 0.5)
    ORANGE = bpy.data.materials.new('ScanStrip'); ORANGE.use_nodes = True
    p = ORANGE.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (1.0, 0.45, 0.08, 1)
    p.inputs['Emission Color'].default_value = (1.0, 0.45, 0.08, 1); p.inputs['Emission Strength'].default_value = 2.0
    SCAN = bpy.data.materials.new('ScanLight'); SCAN.use_nodes = True
    p = SCAN.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.1, 0.9, 0.3, 1)
    p.inputs['Emission Color'].default_value = (0.1, 0.9, 0.3, 1); p.inputs['Emission Strength'].default_value = 3.0
    r = root('XRay')
    L = 3.2                                         # ความยาวอุโมงค์ตามแกน x
    # ตัวเครื่อง: หน้าตัดรูปบ้านลบมุม (ผนังข้างตั้ง หลังคาลาด 2 ข้าง) เจาะอุโมงค์กลาง (กว้าง 1.5 สูง 0.8–2.1)
    bm = bmesh.new()
    outer = [(-1.15, 0.0), (1.15, 0.0), (1.15, 2.05), (0.7, 2.7), (-0.7, 2.7), (-1.15, 2.05)]
    inner = [(-0.75, 0.8), (0.75, 0.8), (0.75, 2.1), (-0.75, 2.1)]
    vo = [[bm.verts.new((x, y, z)) for (y, z) in outer] for x in (-L / 2, L / 2)]
    vi = [[bm.verts.new((x, y, z)) for (y, z) in inner] for x in (-L / 2, L / 2)]
    for k in range(len(outer)):                     # ผิวนอก
        bm.faces.new((vo[0][k], vo[0][(k + 1) % 6], vo[1][(k + 1) % 6], vo[1][k]))
    for k in range(4):                              # ผนังอุโมงค์ (หันเข้าด้านใน)
        bm.faces.new((vi[0][(k + 1) % 4], vi[0][k], vi[1][k], vi[1][(k + 1) % 4]))
    for e, sgn in ((0, -1), (1, 1)):                # ปลายทั้งสองข้าง: วงนอกต่อวงในเป็นหน้ากรอบ
        o, i_ = vo[e], vi[e]
        quads = [(o[0], o[1], i_[1], i_[0]), (o[1], o[2], i_[2], i_[1]), (o[2], o[3], i_[2]), (o[3], o[4], i_[3], i_[2]),
                 (o[4], o[5], i_[3]), (o[5], o[0], i_[0], i_[3])]
        for q in quads:
            bm.faces.new(q if sgn > 0 else tuple(reversed(q)))
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj_from_bmesh('XrayBody', bm, BODY, parent=r)
    # แถบสีน้ำเงินกลางตัวเครื่อง (คาดรอบหลังคาและผนังข้าง) + ฐานดำ
    boxes('XrayBand', [((0, s * 1.16, 1.2), (0.45, 0.01, 0.85)) for s in (1, -1)] + [((0, 0, 2.71), (0.45, 0.7, 0.01))], BAND, r)
    prim('cube', 'XrayBase', DARK, loc=(0, 0, 0.06), scale=(L / 2 + 0.05, 1.2, 0.06), parent=r)
    # แถบไฟส้มด้านข้างบน (ตกแต่ง) ทั้งสองข้าง
    boxes('ScanStrip', [((0, s * 1.165, 1.85), (1.2, 0.01, 0.1)) for s in (1, -1)], ORANGE, r)
    # ม่านกันรังสีเป็นริ้วดำทั้งปากทางเข้าและทางออก
    boxes('Curtain', [((xe, -0.66 + k * 0.19, 1.45), (0.01, 0.085, 0.62)) for xe in (-L / 2 - 0.02, L / 2 + 0.02) for k in range(8)], CURTAIN, r)
    # แถบไฟสแกนในอุโมงค์ (ชื่อ ScanLight เว็บเลื่อนไปมาและซ่อน/แสดง) — ต้องอยู่ที่ x = 0 ของตัวเครื่อง
    prim('cube', 'ScanLight', SCAN, loc=(0, 0, 2.06), scale=(0.06, 0.7, 0.02), parent=r)
    # แผงควบคุม + ตู้ไฟฟ้า + สายไฟ ด้านหน้า (-y)
    prim('cube', 'ControlPanel', DARK, loc=(-1.05, -1.17, 1.25), scale=(0.3, 0.02, 0.22), parent=r)
    for k, c in enumerate((0xd9423e, 0x45d16b, 0x2f8fdf)):
        prim('cube', 'Button', mat('Btn%d' % k, hexrgb(c), 0.4), loc=(-1.2 + k * 0.15, -1.19, 1.15), scale=(0.04, 0.01, 0.03), parent=r)
    prim('cube', 'Cabinet', PANEL, loc=(1.1, -1.17, 0.75), scale=(0.3, 0.02, 0.4), parent=r)
    prim('cube', 'JunctionBox', PANEL, loc=(0.2, -1.17, 0.7), scale=(0.25, 0.02, 0.2), parent=r)
    text('X-RAY', 0.3, mat('XText', hexrgb(0xf2f4f7), 0.5), (0, -1.175, 1.35), R90, r, extrude=0, name='XrayText')
    return r


# ---------------- บ้านฟาร์มแบบญี่ปุ่น ----------------
def gable_roof(name, w, d, rise, overhang, z, material, parent):
    """หลังคาจั่ว (สันตามแกน x) ทำจากแผ่นหนา 2 แผ่น"""
    half = d / 2 + overhang
    slope = math.atan2(rise, d / 2)
    length = math.hypot(half, rise * half / (d / 2))
    for s in (1, -1):
        # แผ่นหลังคาลาดลงจากสันกลาง (y = 0) ไปชายคา: ด้าน +y หมุนติดลบ ด้าน -y หมุนเป็นบวก
        prim('cube', name, material, loc=(0, s * half / 2, z + rise - rise * half / d), rot=(-s * slope, 0, 0),
             scale=(w / 2 + overhang, length / 2, 0.1), parent=parent)


def farmhouse():
    PLASTER = mat('Plaster', hexrgb(0xf3eedf), 0.85)
    TIMBER = mat('Timber', hexrgb(0x4a2f1d), 0.7)
    WOOD = mat('DoorWood', hexrgb(0x8a5a35), 0.6)
    ROOF = mat('RoofTile', hexrgb(0x3b4148), 0.6)
    PAPER = mat('Shoji', hexrgb(0xf7f3e8), 0.9)
    STONE = mat('Stone', hexrgb(0xa7a49b), 0.9)
    INK = mat('SignInk', hexrgb(0x1d1d1d), 0.6)
    r = root('Farmhouse')
    W, D, H = 9.0, 6.0, 3.4
    prim('cube', 'Plinth', STONE, loc=(0, 0, 0.1), scale=(W / 2 + 0.15, D / 2 + 0.15, 0.1), parent=r)
    prim('cube', 'Walls', PLASTER, loc=(0, 0, 0.2 + H / 2), scale=(W / 2, D / 2, H / 2), parent=r)
    # หน้าจั่ว (สามเหลี่ยมผนังขาว) ทั้งสองด้าน (±x)
    rise = 2.0
    for s in (1, -1):
        bm = bmesh.new()
        v = [bm.verts.new((s * W / 2, y, z)) for y, z in ((-D / 2, 0.2 + H), (D / 2, 0.2 + H), (0, 0.2 + H + rise))]
        bm.faces.new(v if s > 0 else list(reversed(v)))
        obj_from_bmesh('Gable', bm, PLASTER, parent=r)
    # โครงไม้เข้ม: เสา คานบน คานกลาง คานล่าง (ด้านหน้า หลัง ข้าง) + โครงหน้าจั่ว — รวมเป็นเมชเดียว
    tb = []
    for y in (-D / 2 - 0.03, D / 2 + 0.03):
        for k in range(7):
            tb.append(((-W / 2 + k * W / 6, y, 0.2 + H / 2), (0.07, 0.04, H / 2)))
        for z in (0.3, 0.2 + H * 0.55, 0.2 + H - 0.05):
            tb.append(((0, y, z), (W / 2 + 0.05, 0.04, 0.06)))
    for x in (-W / 2 - 0.03, W / 2 + 0.03):
        for k in range(5):
            tb.append(((x, -D / 2 + k * D / 4, 0.2 + H / 2), (0.04, 0.07, H / 2)))
        for z in (0.3, 0.2 + H * 0.55, 0.2 + H - 0.05):
            tb.append(((x, 0, z), (0.04, D / 2 + 0.05, 0.06)))
        tb.append(((x, 0, 0.2 + H + rise * 0.45), (0.04, D / 4, 0.05)))
        tb.append(((x, 0, 0.2 + H + rise / 2), (0.04, 0.06, rise / 2)))
    boxes('Timber', tb, TIMBER, r)
    gable_roof('Roof', W, D, rise, 0.6, 0.2 + H, ROOF, r)
    prim('cube', 'Ridge', ROOF, loc=(0, 0, 0.2 + H + rise + 0.05), scale=(W / 2 + 0.6, 0.15, 0.12), parent=r)
    # ทางเข้าด้านหน้า (-y): ประตูไม้บานเลื่อน + บานโชจิ + กันสาดกระเบื้องเล็ก
    FY = -D / 2 - 0.05
    prim('cube', 'EntryDoor', WOOD, loc=(-0.55, FY, 1.3), scale=(0.5, 0.03, 1.05), parent=r)
    boxes('DoorBars', [((-0.55 + dx, FY - 0.03, 1.3), (0.02, 0.01, 1.0)) for dx in (-0.3, -0.15, 0, 0.15, 0.3)], TIMBER, r)
    prim('cube', 'ShojiDoor', PAPER, loc=(0.5, FY, 1.3), scale=(0.5, 0.03, 1.05), parent=r)
    boxes('ShojiGrid', [((0.5 + dx, FY - 0.03, 1.3), (0.015, 0.01, 1.05)) for dx in (-0.25, 0, 0.25)] +
          [((0.5, FY - 0.03, 0.4 + k * 0.3), (0.5, 0.01, 0.015)) for k in range(7)], TIMBER, r)
    prim('cube', 'Awning', ROOF, loc=(0, FY - 0.55, 2.65), rot=(math.radians(-14), 0, 0), scale=(1.5, 0.65, 0.06), parent=r)
    prim('cube', 'Step', STONE, loc=(0, FY - 0.45, 0.08), scale=(1.3, 0.45, 0.08), parent=r)
    # หน้าต่างลูกกรงไม้ 2 บาน
    for x in (-3.0, 3.0):
        prim('cube', 'Window', PAPER, loc=(x, FY, 2.0), scale=(0.55, 0.02, 0.4), parent=r)
        boxes('WindowBars', [((x + dx, FY - 0.03, 2.0), (0.02, 0.01, 0.4)) for dx in (-0.4, -0.2, 0, 0.2, 0.4)], TIMBER, r)
    # ป้ายไม้ตั้งพื้น เขียนตัวคันจิ 鯉 (ปลาคาร์ฟ)
    prim('cube', 'SignPost', TIMBER, loc=(1.75, FY - 0.6, 0.7), scale=(0.04, 0.04, 0.7), parent=r)
    prim('cube', 'SignBoard', WOOD, loc=(1.75, FY - 0.6, 1.45), scale=(0.3, 0.03, 0.4), parent=r)
    text('鯉', 0.42, INK, (1.75, FY - 0.64, 1.45), R90, r, extrude=0, name='SignKanji', font=JP_FONT)
    return r


# ---------------- อาคารด่านตรวจสัตว์น้ำ กรมประมง ----------------
def dof():
    CREAM = mat('DofWall', hexrgb(0xefeadb), 0.8)
    NAVY = mat('DofNavy', hexrgb(0x1f3a7a), 0.5)
    YELLOW = mat('DofStripe', hexrgb(0xe0b43a), 0.5)
    ROOF = mat('DofRoof', hexrgb(0xb9c0c8), 0.6, 0.3)
    GLASS = mat('DofGlass', hexrgb(0x6f93b8), 0.15, 0.3)
    FRAMEM = mat('DofFrame', hexrgb(0xdfe3e8), 0.4, 0.5)
    DOOR = mat('DofShutter', hexrgb(0xb3bac3), 0.45, 0.5)
    WHITE = mat('DofText', hexrgb(0xffffff), 0.5)
    r = root('DofBuilding')
    W, D, H = 14.0, 6.0, 3.6
    prim('cube', 'Slab', mat('DofSlab', hexrgb(0xa9b0b8), 0.9), loc=(0, 0, 0.08), scale=(W / 2 + 0.3, D / 2 + 0.3, 0.08), parent=r)
    prim('cube', 'Walls', CREAM, loc=(0, 0, 0.16 + H / 2), scale=(W / 2, D / 2, H / 2), parent=r)
    # ผนังช่วงล่างสีน้ำเงิน + เส้นเหลืองคาดรอบอาคาร
    boxes('NavyBase', [((0, s * (D / 2 + 0.02), 0.6), (W / 2 + 0.02, 0.02, 0.44)) for s in (1, -1)] +
          [((s * (W / 2 + 0.02), 0, 0.6), (0.02, D / 2 + 0.02, 0.44)) for s in (1, -1)], NAVY, r)
    boxes('Stripe', [((0, s * (D / 2 + 0.03), 1.08), (W / 2 + 0.03, 0.02, 0.04)) for s in (1, -1)] +
          [((s * (W / 2 + 0.03), 0, 1.08), (0.02, D / 2 + 0.03, 0.04)) for s in (1, -1)], YELLOW, r)
    # หลังคาแบนยื่น + ขอบหลังคาลาด (เทา) + แอร์ 2 ตัวบนหลังคา
    prim('cube', 'Roof', ROOF, loc=(0, 0, 0.16 + H + 0.12), scale=(W / 2 + 0.5, D / 2 + 0.5, 0.12), parent=r)
    prim('cube', 'Fascia', CREAM, loc=(0, -D / 2 - 0.5, 0.16 + H + 0.12), scale=(W / 2 + 0.5, 0.05, 0.2), parent=r)
    for x in (-5.0, -3.8):
        prim('cube', 'AirCon', FRAMEM, loc=(x, 1.5, 0.16 + H + 0.5), scale=(0.45, 0.3, 0.26), parent=r)
    FY = -D / 2 - 0.04
    # ด้านหน้า (-y) จากซ้ายไปขวา: ประตูม้วนเปิดรับรถ · ทางเข้ากระจก + กันสาดน้ำเงิน · หน้าต่างแถว · ประตูข้าง
    prim('cube', 'ShutterOpen', mat('DofInside', hexrgb(0xf7f7f5), 0.9), loc=(-5.0, FY, 1.45), scale=(1.4, 0.02, 1.25), parent=r)
    prim('cube', 'ShutterBox', DOOR, loc=(-5.0, FY - 0.1, 2.9), scale=(1.5, 0.12, 0.18), parent=r)
    prim('cube', 'GlassDoor', GLASS, loc=(-1.6, FY, 1.35), scale=(0.8, 0.02, 1.15), parent=r)
    boxes('GlassDoorFrame', [((-1.6 + dx, FY - 0.02, 1.35), (0.04, 0.02, 1.15)) for dx in (-0.8, 0, 0.8)] +
          [((-1.6, FY - 0.02, 2.5), (0.84, 0.02, 0.04))], FRAMEM, r)
    prim('cube', 'Canopy', NAVY, loc=(-0.9, FY - 0.6, 2.75), rot=(math.radians(-8), 0, 0), scale=(2.0, 0.6, 0.05), parent=r)
    for x in (0.9, 2.6, 4.3):
        prim('cube', 'Window', GLASS, loc=(x, FY, 1.95), scale=(0.7, 0.02, 0.55), parent=r)
        boxes('WindowFrame', [((x + dx, FY - 0.02, 1.95), (0.03, 0.02, 0.55)) for dx in (-0.7, -0.23, 0.23, 0.7)] +
              [((x, FY - 0.02, z), (0.72, 0.02, 0.03)) for z in (1.4, 2.5)], FRAMEM, r)
    prim('cube', 'SideDoor', DOOR, loc=(6.0, FY, 1.2), scale=(0.45, 0.02, 1.05), parent=r)
    # ป้ายชื่อบนขอบหลังคา: ไทย + อังกฤษ (น้ำเงิน ขอบทอง) + ตราวงกลมเรียบ ๆ เหนือป้าย
    prim('cube', 'SignFrame', YELLOW, loc=(0, FY - 0.55, 4.45), scale=(4.3, 0.04, 0.62), parent=r)
    prim('cube', 'SignBoard', NAVY, loc=(0, FY - 0.6, 4.45), scale=(4.2, 0.04, 0.57), parent=r)
    text('ด่านตรวจสัตว์น้ำ  กรมประมง', 0.55, WHITE, (0, FY - 0.65, 4.6), R90, r, extrude=0, name='SignThai', font=THAI_FONT)
    text('DEPARTMENT OF FISHERIES QUARANTINE', 0.22, WHITE, (0, FY - 0.65, 4.07), R90, r, extrude=0, name='SignEng')
    emblem('Emblem', r, (0, FY - 0.55, 5.45), 0.42)
    return r


# ---------------- อาคารผู้โดยสาร (ฉากหลังสนามบิน) ----------------
def terminal():
    GLASS = mat('TermGlass', hexrgb(0x3f7fae), 0.15, 0.3)
    MULL = mat('Mullion', hexrgb(0x2a4a68), 0.4, 0.4)
    ROOF = mat('TermRoof', hexrgb(0xdfe3e8), 0.5, 0.3)
    BASE = mat('TermBase', hexrgb(0xb9c0c8), 0.6)
    BRIDGE = mat('JetBridge', hexrgb(0xc5ccd5), 0.5, 0.3)
    DARK = mat('TermDark', hexrgb(0x2d3239), 0.6)
    GOLD = mat('SignGold', hexrgb(0xe0b43a), 0.4, 0.4)
    r = root('Terminal')
    L, D, H = 40.0, 6.0, 4.4                       # ยาว (x) ลึก (y) สูงผนังกระจก — เว็บยืดตามแกน x ให้ยาวตามฉากได้
    prim('cube', 'Base', BASE, loc=(0, 0, 0.3), scale=(L / 2, D / 2, 0.3), parent=r)
    prim('cube', 'GlassWall', GLASS, loc=(0, 0, 0.6 + (H - 0.6) / 2), scale=(L / 2 - 0.1, D / 2 - 0.1, (H - 0.6) / 2), parent=r)
    # เส้นแบ่งกระจก (แนวตั้งทุก 1.6 ม. + แนวนอน 2 เส้น) ด้านหน้าและด้านข้าง
    mu = [((-L / 2 + 0.8 + k * 1.6, -D / 2 + 0.07, 0.6 + (H - 0.6) / 2), (0.04, 0.04, (H - 0.6) / 2)) for k in range(25)]
    mu += [((0, -D / 2 + 0.07, z), (L / 2, 0.04, 0.05)) for z in (1.9, 3.2)]
    mu += [((s * (L / 2 - 0.07), 0, z), (0.04, D / 2, 0.05)) for s in (1, -1) for z in (1.9, 3.2)]
    boxes('Mullions', mu, MULL, r)
    # หลังคาโค้ง (โค้งตามแนวยาว สูงกลาง ต่ำปลาย) ยื่นออกจากผนังเล็กน้อย
    bm = bmesh.new(); n = 20; prev = None
    for i in range(n + 1):
        x = -L / 2 - 0.6 + i * (L + 1.2) / n
        z = H + 0.15 + 0.9 * (1 - (2 * i / n - 1) ** 2)
        ring = [bm.verts.new((x, y, zz)) for y, zz in ((-D / 2 - 0.8, z - 0.25), (D / 2 + 0.4, z - 0.25), (D / 2 + 0.4, z), (-D / 2 - 0.8, z))]
        if prev:
            for k in range(4):
                bm.faces.new((prev[k], prev[(k + 1) % 4], ring[(k + 1) % 4], ring[k]))
        else:
            bm.faces.new(list(reversed(ring)))
        prev = ring
    bm.faces.new(prev)
    bm.normal_update(); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj_from_bmesh('Roof', bm, ROOF, parent=r)
    # หอบังคับการบินที่ปลาย +x: เสา + ห้องควบคุมกระจก 8 เหลี่ยม + หลังคา
    TX = L / 2 - 2.5
    prim('cylinder', 'TowerShaft', BASE, loc=(TX, 1.0, 4.5), vertices=8, radius=0.9, depth=9.0, parent=r)
    prim('cylinder', 'TowerCab', GLASS, loc=(TX, 1.0, 9.6), vertices=8, radius=1.5, depth=1.2, parent=r)
    prim('cone', 'TowerRoof', ROOF, loc=(TX, 1.0, 10.45), vertices=8, radius1=1.7, radius2=1.2, depth=0.5, parent=r)
    # งวงช้าง 2 ตัวยื่นไปทางลานจอด (-y)
    for x in (-9.0, 7.0):
        prim('cube', 'BridgeTunnel', BRIDGE, loc=(x, -D / 2 - 3.2, 3.6), scale=(0.9, 3.0, 0.75), parent=r)
        prim('cube', 'BridgeCab', BRIDGE, loc=(x, -D / 2 - 6.5, 3.6), scale=(1.1, 0.5, 0.85), parent=r)
        prim('cylinder', 'BridgeLeg', DARK, loc=(x, -D / 2 - 5.6, 1.45), vertices=8, radius=0.15, depth=2.9, parent=r)
        prim('cube', 'BridgeWheels', DARK, loc=(x, -D / 2 - 5.6, 0.2), scale=(0.6, 0.3, 0.2), parent=r)
    # ป้ายชื่อสนามบิน (สลับตามสนามบิน) บนผนังกระจกด้านหน้า: พื้นดำ ตัวอักษรทอง
    sign_pair(r, (-1.0, -D / 2 - 0.05, 3.3), 0.55, 'NARITA INTERNATIONAL AIRPORT', 'SUVARNABHUMI AIRPORT',
              (5.6, 0.04, 0.45), DARK, GOLD)
    return r


ITEMS = [('warehouse.glb', warehouse), ('xray.glb', xray), ('farmhouse.glb', farmhouse), ('dof.glb', dof),
         ('terminal.glb', terminal)]
ONLY = os.environ.get('KOI_ONLY')            # ตั้งค่าเพื่อสร้างชิ้นเดียว เช่น KOI_ONLY=dof
for fname, build in ITEMS:
    if ONLY and not fname.startswith(ONLY):
        continue
    reset(); build(); export_glb(fname)
