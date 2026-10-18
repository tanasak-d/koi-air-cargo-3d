# ของประกอบฉาก 4 ชิ้น สร้างด้วยโค้ดใน Blender แล้วส่งออกทีละไฟล์:
#   fishbox.glb   กล่องโฟมใส่ปลา + ฝา + สายรัด + ป้าย LIVE ANIMALS / THIS WAY UP
#   bag.glb       ถุงใส 3 ชั้น (Bag_L1..L3) + น้ำ + ยางรัดปากถุง
#   warehouse.glb คลังสินค้าสัตว์มีชีวิต (ผนังลอนเหล็ก ประตูม้วน กันสาด ป้าย)
#   xray.glb      เครื่อง X-ray สายพาน (อุโมงค์ ม่านตะกั่ว แถบไฟสแกน จอควบคุม)
# แกน: Blender -Y = ด้าน +z ในเว็บ (ด้านหน้าที่หันเข้ากล้อง) · ฐานของทุกชิ้นอยู่ที่ z = 0
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, obj_from_bmesh, prim, root, export_glb, render_preview


def text(body, size, material, loc, rot, parent, extrude=0.004, name='Text'):
    """ตัวอักษรภาษาอังกฤษ (ฟอนต์ในตัวของ Blender) แปลงเป็นเมช"""
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.active_object
    t.data.body = body; t.data.size = size; t.data.extrude = extrude
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    t.data.resolution_u = 2          # เส้นโค้งของตัวอักษรหยาบลงหน่อย ไฟล์จะเล็กลงมาก (มองไม่ออกในฉาก)
    bpy.ops.object.convert(target='MESH')
    t = bpy.context.active_object; t.name = name
    t.data.materials.clear(); t.data.materials.append(material)
    if parent is not None:
        t.parent = parent            # ตำแหน่ง loc นับจากตัวแม่ (เหมือนชิ้นอื่น ๆ)
    return t


def bevel_box(name, size, loc, material, parent, width=0.04):
    """กล่องขอบมน (bevel) — ให้ดูเป็นของจริงกว่ากล่องเหลี่ยมคม"""
    ob = prim('cube', name, material, loc=loc, scale=(size[0] / 2, size[1] / 2, size[2] / 2), parent=parent)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(scale=True)
    m = ob.modifiers.new('bevel', 'BEVEL'); m.width = width; m.segments = 2
    return ob


def empty(name, parent, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.parent = parent; e.location = loc
    return e


# ---------------- กล่องโฟม ----------------
def fishbox(ox=0):
    FOAM = mat('BoxBody', hexrgb(0xf1f3f2), 0.9)        # ชื่อนี้เว็บใช้เปลี่ยนเป็นสีแดงตอนเกิดความเสี่ยง
    LID = mat('BoxLid', hexrgb(0xe6e9e8), 0.9)
    STRAP = mat('Strap', hexrgb(0x2f5fb5), 0.5)
    RED = mat('LabelRed', hexrgb(0xd9423e), 0.5)
    WHITE = mat('LabelWhite', hexrgb(0xffffff), 0.5)
    GREEN = mat('LabelGreen', hexrgb(0x2e9e57), 0.5)
    INK = mat('Ink', hexrgb(0x1d2b3a), 0.6)
    r = root('FishBox'); r.location = (ox, 0, 0)
    bevel_box('Box_Body', (1.6, 1.1, 0.86), (0, 0, 0.43), FOAM, r, 0.05)
    bevel_box('Box_Lid', (1.66, 1.16, 0.2), (0, 0, 0.96), LID, r, 0.04)
    for x in (-0.45, 0.45):                                   # สายรัด 2 เส้นพาดฝาลงมาด้านข้าง
        prim('cube', 'Strap', STRAP, loc=(x, 0, 0.535), scale=(0.035, 0.595, 0.535), parent=r)
    # ป้าย LIVE ANIMALS (แดง ตัวอักษรขาว) ด้านหน้า
    live = empty('LiveLabel', r)
    prim('cube', 'LiveBoard', RED, loc=(-0.05, -0.556, 0.47), scale=(0.3, 0.004, 0.17), parent=live)
    text('LIVE', 0.14, WHITE, (-0.05, -0.562, 0.52), (math.radians(90), 0, 0), live, name='LiveText1')
    text('ANIMALS', 0.1, WHITE, (-0.05, -0.562, 0.4), (math.radians(90), 0, 0), live, name='LiveText2')
    # ป้าย THIS WAY UP (ลูกศรเขียว 2 อัน)
    arrow = empty('ArrowLabel', r)
    prim('cube', 'ArrowBoard', mat('LabelYellow', hexrgb(0xfff1b8), 0.5), loc=(0.55, -0.556, 0.47), scale=(0.17, 0.004, 0.17), parent=arrow)
    for dx in (-0.06, 0.06):
        prim('cube', 'ArrowStem', GREEN, loc=(0.55 + dx, -0.562, 0.43), scale=(0.018, 0.004, 0.07), parent=arrow)
        prim('cone', 'ArrowHead', GREEN, loc=(0.55 + dx, -0.562, 0.53), rot=(0, 0, 0), vertices=3, radius1=0.05, radius2=0, depth=0.06, parent=arrow)
    text('THIS WAY UP', 0.045, INK, (0.55, -0.562, 0.34), (math.radians(90), 0, 0), arrow, name='ArrowText')
    # ข้อความบนฝา: เที่ยวบิน
    text('KOI  JL707  NRT-BKK', 0.09, INK, (0, 0, 1.065), (0, 0, 0), r, name='LidText')
    return r


# ---------------- ถุง 3 ชั้น ----------------
def lathe(name, profile, material, parent, seg=20, loc=(0, 0, 0)):
    """หมุนเส้นโปรไฟล์ (รัศมี, ความสูง) รอบแกนตั้ง ได้รูปทรงกลมแบบถุง/ขวด"""
    bm = bmesh.new(); rings = []
    for r_, z in profile:
        rings.append([bm.verts.new((loc[0] + math.cos(2 * math.pi * j / seg) * r_, loc[1] + math.sin(2 * math.pi * j / seg) * r_, loc[2] + z)) for j in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for j in range(seg):
            bm.faces.new((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j]))
    bm.normal_update()
    return obj_from_bmesh(name, bm, material, smooth=True, parent=parent)


def bag(ox=0):
    FILM = mat('BagFilm', hexrgb(0xe6f2ff), 0.15, alpha=0.22)
    WATER = mat('Water', hexrgb(0x3f8fd0), 0.05, alpha=0.5)
    BAND = mat('Band', hexrgb(0xf28c28), 0.5)
    r = root('Bag'); r.location = (ox, 0, 0)
    for k, (rad, h) in enumerate([(0.42, 0.95), (0.39, 0.9), (0.36, 0.85)]):     # ชั้นนอก → ชั้นใน
        prof = [(0.01, 0.0), (rad * 0.7, 0.02), (rad * 0.97, 0.1), (rad, 0.3 * h), (rad * 0.95, 0.55 * h),
                (rad * 0.7, 0.78 * h), (rad * 0.3, 0.92 * h), (0.06, h)]
        lathe('Bag_L' + str(k + 1), prof, FILM, r)
    lathe('Bag_Water', [(0.01, 0.01), (0.24, 0.02), (0.33, 0.1), (0.34, 0.3), (0.01, 0.3)], WATER, r)
    prim('torus', 'Bag_Knot', BAND, loc=(0, 0, 0.93), major_radius=0.06, minor_radius=0.02, major_segments=12, minor_segments=6, parent=r)
    prim('cone', 'Bag_Tail', mat('BagNeck', hexrgb(0xe6f2ff), 0.15, alpha=0.4), loc=(0, 0, 1.0), vertices=10, radius1=0.05, radius2=0.1, depth=0.14, parent=r)
    return r


# ---------------- คลังสินค้า ----------------
def warehouse(ox=0):
    WALL = mat('Wall', hexrgb(0xdfe3e8), 0.6, 0.3)
    RIB = mat('Rib', hexrgb(0xc5ccd5), 0.5, 0.4)
    TRIM = mat('Trim', hexrgb(0x2f5fb5), 0.5)
    DOOR = mat('RollerDoor', hexrgb(0x8d96a3), 0.4, 0.6)
    SLAT = mat('Slat', hexrgb(0x6c7584), 0.4, 0.6)
    GLASS = mat('Glass', hexrgb(0x5b7da6), 0.1, 0.2)
    YEL = mat('Bollard', hexrgb(0xf2c230), 0.5)
    WHITE = mat('SignText', hexrgb(0xffffff), 0.5)
    CONC = mat('Dock', hexrgb(0xa9b0b8), 0.9)
    W, D, H = 12.0, 8.0, 6.0
    r = root('Warehouse'); r.location = (ox, 0, 0)
    prim('cube', 'Shell', WALL, loc=(0, 0, H / 2), scale=(W / 2, D / 2, H / 2), parent=r)
    # ผนังลอนเหล็ก: ซี่แนวตั้งด้านหน้าและด้านข้าง
    for i in range(int(W / 0.5) + 1):
        x = -W / 2 + i * 0.5
        if abs(x) < 2.3: continue                                   # เว้นช่องประตู
        prim('cube', 'Rib', RIB, loc=(x, -D / 2 - 0.03, H / 2), scale=(0.06, 0.03, H / 2), parent=r)
    for i in range(int(D / 0.5) + 1):
        y = -D / 2 + i * 0.5
        for s in (1, -1):
            prim('cube', 'Rib', RIB, loc=(s * (W / 2 + 0.03), y, H / 2), scale=(0.03, 0.06, H / 2), parent=r)
    prim('cube', 'RoofTrim', TRIM, loc=(0, 0, H + 0.2), scale=(W / 2 + 0.3, D / 2 + 0.3, 0.2), parent=r)
    prim('cube', 'Base', CONC, loc=(0, 0, 0.15), scale=(W / 2 + 0.05, D / 2 + 0.05, 0.15), parent=r)
    # ประตูม้วน (ชื่อ Door) + ร่องบานเกล็ด + กันสาด
    door = prim('cube', 'Door', DOOR, loc=(0, -D / 2 - 0.04, 1.9), scale=(2.1, 0.04, 1.9), parent=r)
    for k in range(12):
        prim('cube', 'DoorSlat', SLAT, loc=(0, -D / 2 - 0.09, 0.3 + k * 0.3), scale=(2.1, 0.01, 0.02), parent=r)
    prim('cube', 'Canopy', TRIM, loc=(0, -D / 2 - 0.8, 4.2), rot=(math.radians(-8), 0, 0), scale=(2.8, 0.85, 0.06), parent=r)
    # หน้าต่างแถบด้านบน + ป้ายชื่อ
    for x in (-4.4, -3.2, 3.2, 4.4):
        prim('cube', 'Window', GLASS, loc=(x, -D / 2 - 0.05, 4.6), scale=(0.45, 0.02, 0.35), parent=r)
    prim('cube', 'SignBoard', TRIM, loc=(0, -D / 2 - 0.08, 5.2), scale=(3.2, 0.04, 0.45), parent=r)
    text('CARGO TERMINAL - AVI', 0.42, WHITE, (0, -D / 2 - 0.13, 5.2), (math.radians(90), 0, 0), r, name='SignText')
    # เสากันชนสีเหลืองหน้าประตู + ช่องระบายอากาศบนหลังคา
    for x in (-2.5, 2.5):
        prim('cylinder', 'Bollard', YEL, loc=(x, -D / 2 - 0.35, 0.5), vertices=10, radius=0.12, depth=1.0, parent=r)
    for x in (-3.5, 0, 3.5):
        prim('cylinder', 'Vent', RIB, loc=(x, 1.5, H + 0.6), vertices=10, radius=0.35, depth=0.5, parent=r)
    return r


# ---------------- เครื่อง X-ray ----------------
def xray(ox=0):
    BODY = mat('XrayBody', hexrgb(0xdde4ee), 0.4, 0.2)
    DARK = mat('XrayDark', hexrgb(0x39455c), 0.5)
    CURTAIN = mat('Curtain', hexrgb(0x2b3445), 0.7, alpha=0.75)
    STRIPE = mat('Stripe', hexrgb(0xf2c230), 0.5)
    BLACK = mat('StripeBlack', hexrgb(0x1d1d1d), 0.5)
    SCREEN = mat('ScanScreen', hexrgb(0x4aa3df), 0.2)
    SCAN = bpy.data.materials.new('ScanLight'); SCAN.use_nodes = True
    p = SCAN.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.1, 0.9, 0.3, 1)
    p.inputs['Emission Color'].default_value = (0.1, 0.9, 0.3, 1); p.inputs['Emission Strength'].default_value = 3.0
    r = root('XRay'); r.location = (ox, 0, 0)
    L, Wd = 3.2, 2.2
    # ตัวเครื่อง: ผนังซ้ายขวา + หลังคา (อุโมงค์โล่งตามแกน x สูง 0.8–2.1)
    for s in (1, -1):
        prim('cube', 'Side', BODY, loc=(0, s * 0.9, 1.15), scale=(L / 2, 0.2, 1.15), parent=r)
        for k in range(6):                                         # แถบเตือนเหลือง-ดำ
            prim('cube', 'Stripe', STRIPE if k % 2 == 0 else BLACK, loc=(-L / 2 + 0.2 + k * 0.25, s * 1.105, 0.25), scale=(0.125, 0.01, 0.1), parent=r)
    prim('cube', 'Top', BODY, loc=(0, 0, 2.3), scale=(L / 2, Wd / 2, 0.2), parent=r)
    prim('cube', 'Base', DARK, loc=(0, 0, 0.4), scale=(L / 2, 0.75, 0.4), parent=r)
    # ม่านตะกั่ว (แผ่นห้อยเป็นริ้ว) ทั้งปากทางเข้าและทางออก
    for xe in (-L / 2 - 0.02, L / 2 + 0.02):
        for k in range(7):
            prim('cube', 'Curtain', CURTAIN, loc=(xe, -0.6 + k * 0.2, 1.55), scale=(0.01, 0.09, 0.5), parent=r)
    # แถบไฟสแกน (ชื่อ ScanLight เว็บใช้ขยับ/เปลี่ยนสี) + ไฟเตือนบนหลังคา
    prim('cube', 'ScanLight', SCAN, loc=(0, 0, 2.08), scale=(0.06, 0.65, 0.02), parent=r)
    prim('cylinder', 'Beacon', mat('Beacon', hexrgb(0xd9423e), 0.3), loc=(0.9, 0, 2.62), vertices=12, radius=0.12, depth=0.25, parent=r)
    # จอควบคุมบนเสาข้างเครื่อง (ด้านหน้า -Y)
    prim('cylinder', 'Pole', DARK, loc=(L / 2 + 0.4, -1.3, 0.75), vertices=8, radius=0.05, depth=1.5, parent=r)
    prim('cube', 'Monitor', DARK, loc=(L / 2 + 0.4, -1.3, 1.6), rot=(math.radians(15), 0, 0), scale=(0.35, 0.04, 0.25), parent=r)
    prim('cube', 'Screen', SCREEN, loc=(L / 2 + 0.4, -1.345, 1.6), rot=(math.radians(15), 0, 0), scale=(0.31, 0.01, 0.21), parent=r)
    text('X-RAY', 0.28, mat('XText', hexrgb(0x1d2b3a), 0.5), (0, -1.105, 1.6), (math.radians(90), 0, 0), r, name='XrayText')
    return r


ITEMS = [('fishbox.glb', fishbox), ('bag.glb', bag), ('warehouse.glb', warehouse), ('xray.glb', xray)]
for fname, build in ITEMS:
    reset(); build(); export_glb(fname)

# ภาพตัวอย่างรวม 4 ชิ้น (ย่อคลังสินค้าลงให้อยู่ในภาพเดียวกัน)
reset()
fishbox(-3.2); bag(-1.4); xray(1.6)
w = warehouse(0); w.location = (0, 9, 0)
render_preview('props.png', cam_loc=(3, -11, 6.5), target=(0, 2, 1.6), lens=32, size=(1280, 720))
