# ฉากประกอบชุดที่ 2 สร้างด้วยโค้ดใน Blender แล้วส่งออกทีละไฟล์:
#   pond.glb       บ่อปลาขอบหินรัศมี 1 (เว็บย่อ/ขยายตามขนาดบ่อ) น้ำเป็นวัสดุชื่อ PondWater
#   dolly.glb      แท่นลากสินค้าในสนามบิน (ด้านบนสูง 1.35 ยาว 3.2 กว้าง 2) มีราว ลูกกลิ้ง ล้อ คานพ่วง
#   farmhouse.glb  บ้านฟาร์มแบบญี่ปุ่น (ผนังขาว โครงไม้ หลังคาจั่วกระเบื้อง ระเบียง) กว้าง 9 ลึก 6
#   dof.glb        อาคารด่านกรมประมง/กักกัน (ทันสมัย ชั้นเดียว แถบเขียว ป้าย ทางเข้ากระจก) กว้าง 14 ลึก 6
#   trees.glb      ต้นไม้ 2 แบบ (Tree_Pine สน / Tree_Round พุ่มกลม) สูงราว 3.5
# แกน: Blender -Y = ด้าน +z ในเว็บ (ด้านหน้า) · ฐานของทุกชิ้นอยู่ที่ z = 0
import bpy, bmesh, math, sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from common import (reset, mat, hexrgb, obj_from_bmesh, prim, root, export_glb, render_preview,
                    text, bevel_box, empty, lathe)


# ---------------- บ่อปลา ----------------
def pond(ox=0):
    random.seed(3)
    STONE = mat('Stone', hexrgb(0x9a958c), 0.95)
    STONE2 = mat('Stone2', hexrgb(0x7d7a73), 0.95)
    WALL = mat('PondWall', hexrgb(0xb9c0c4), 0.9)
    WATER = mat('PondWater', hexrgb(0x3f8fd0), 0.05, alpha=0.85)    # เว็บเปลี่ยนสีน้ำตามบ่อ
    r = root('Pond'); r.location = (ox, 0, 0)
    lathe('Pond_Wall', [(0.86, 0.0), (0.95, 0.0), (0.95, 0.32), (0.86, 0.32)], WALL, r, seg=32)
    prim('cylinder', 'Pond_Water', WATER, loc=(0, 0, 0.27), vertices=32, radius=0.88, depth=0.04, smooth=True, parent=r)
    prim('cylinder', 'Pond_Floor', mat('PondFloor', hexrgb(0x2b5f86), 0.8), loc=(0, 0, 0.02), vertices=32, radius=0.88, depth=0.04, parent=r)
    for k in range(18):                                   # หินรอบขอบบ่อ
        a = 2 * math.pi * k / 18 + random.uniform(-0.05, 0.05)
        s = random.uniform(0.09, 0.13)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(math.cos(a) * 0.96, math.sin(a) * 0.96, 0.33))
        st = bpy.context.active_object; st.name = 'Pond_Stone'
        st.scale = (s * 1.4, s, s * 0.7); st.rotation_euler = (0, 0, a)
        st.data.materials.append(STONE if k % 3 else STONE2); st.parent = r
    return r


# ---------------- แท่นลากสินค้า ----------------
def dolly(ox=0):
    STEEL = mat('DollySteel', hexrgb(0x4b5360), 0.5, 0.5)
    ROLL = mat('Roller', hexrgb(0x9aa3ae), 0.3, 0.8)
    YEL = mat('DollyYellow', hexrgb(0xf2c230), 0.5)
    TYRE = mat('DollyTyre', hexrgb(0x1d2b3a), 0.9)
    r = root('Dolly'); r.location = (ox, 0, 0)
    prim('cube', 'Dolly_Frame', STEEL, loc=(0, 0, 0.9), scale=(1.6, 1.0, 0.15), parent=r)
    for k in range(10):                                   # ลูกกลิ้งบนแท่น
        prim('cylinder', 'Dolly_Roller', ROLL, loc=(-1.4 + k * 0.31, 0, 1.3), rot=(math.radians(90), 0, 0), vertices=10, radius=0.05, depth=1.8, parent=r)
    for s in (1, -1):                                     # ราวกันตก (เหลือง) สองข้าง
        prim('cube', 'Dolly_Rail', YEL, loc=(0, s * 0.98, 1.45), scale=(1.6, 0.03, 0.04), parent=r)
        for x in (-1.5, -0.5, 0.5, 1.5):
            prim('cube', 'Dolly_Post', YEL, loc=(x, s * 0.98, 1.25), scale=(0.03, 0.03, 0.22), parent=r)
        for x in (-1.15, 1.15):                           # ล้อ
            prim('cylinder', 'Dolly_Wheel', TYRE, loc=(x, s * 0.85, 0.38), rot=(math.radians(90), 0, 0), vertices=16, radius=0.38, depth=0.25, smooth=True, parent=r)
    prim('cube', 'Dolly_Bed', STEEL, loc=(0, 0, 1.15), scale=(1.6, 0.95, 0.1), parent=r)
    prim('cube', 'Dolly_TowBar', STEEL, loc=(2.2, 0, 0.55), scale=(0.6, 0.06, 0.06), parent=r)
    return r


# ---------------- บ้านฟาร์มแบบญี่ปุ่น ----------------
def gable_roof(name, w, d, h, overhang, z, material, parent):
    """หลังคาจั่ว (สันหลังคาตามแกน x) แบบปริซึมสามเหลี่ยม มีชายคายื่น"""
    bm = bmesh.new(); W, D = w / 2 + overhang, d / 2 + overhang
    v = [bm.verts.new(p) for p in [(-W, -D, z), (W, -D, z), (W, D, z), (-W, D, z), (-W, 0, z + h), (W, 0, z + h)]]
    th = 0.12
    v2 = [bm.verts.new((p.co.x, p.co.y, p.co.z + th)) for p in v]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (6, 7, 11, 10), (8, 9, 10, 11), (0, 4, 10, 6), (1, 7, 11, 5), (3, 9, 10, 4), (2, 5, 11, 8), (0, 6, 7, 1), (2, 8, 9, 3)]:
        try:
            bm.faces.new([(v + v2)[i] for i in f])
        except ValueError:
            pass
    bm.normal_update()
    return obj_from_bmesh(name, bm, material, parent=parent)


def farmhouse(ox=0):
    WALL = mat('Plaster', hexrgb(0xf3efe6), 0.9)
    WOOD = mat('Wood', hexrgb(0x5a3b26), 0.8)
    TILE = mat('RoofTile', hexrgb(0x3d4552), 0.6, 0.2)
    PAPER = mat('Shoji', hexrgb(0xfaf6ea), 0.9)
    STONE = mat('Foundation', hexrgb(0x8c8a85), 0.95)
    r = root('Farmhouse'); r.location = (ox, 0, 0)
    W, D, H = 9.0, 6.0, 3.4
    prim('cube', 'House_Base', STONE, loc=(0, 0, 0.2), scale=(W / 2 + 0.1, D / 2 + 0.1, 0.2), parent=r)
    prim('cube', 'House_Wall', WALL, loc=(0, 0, 0.4 + H / 2), scale=(W / 2, D / 2, H / 2), parent=r)
    for x in [-W / 2 + i * (W / 6) for i in range(7)]:   # เสาไม้ตามผนังหน้า/หลัง
        for s in (1, -1):
            prim('cube', 'House_Post', WOOD, loc=(x, s * (D / 2 + 0.03), 0.4 + H / 2), scale=(0.09, 0.05, H / 2), parent=r)
    for s in (1, -1):
        prim('cube', 'House_Beam', WOOD, loc=(0, s * (D / 2 + 0.04), 0.4 + H - 0.1), scale=(W / 2, 0.06, 0.1), parent=r)
    # ประตูบานเลื่อนแบบโชจิ (กระดาษขาว ลูกฟักไม้) ด้านหน้า
    for x in (-0.75, 0.75):
        prim('cube', 'Shoji', PAPER, loc=(x, -D / 2 - 0.05, 1.5), scale=(0.72, 0.02, 1.05), parent=r)
        for k in range(4):
            prim('cube', 'ShojiBar', WOOD, loc=(x, -D / 2 - 0.07, 0.7 + k * 0.53), scale=(0.72, 0.015, 0.02), parent=r)
        prim('cube', 'ShojiBarV', WOOD, loc=(x, -D / 2 - 0.07, 1.5), scale=(0.02, 0.015, 1.05), parent=r)
    # ระเบียงไม้ (เองาวะ) ด้านหน้า
    prim('cube', 'Veranda', WOOD, loc=(0, -D / 2 - 0.7, 0.45), scale=(W / 2 - 0.5, 0.6, 0.06), parent=r)
    gable_roof('House_Roof', W, D, 2.0, 0.8, 0.4 + H, TILE, r)
    prim('cube', 'Ridge', TILE, loc=(0, 0, 0.4 + H + 2.1), scale=(W / 2 + 0.8, 0.18, 0.12), parent=r)
    return r


# ---------------- อาคารด่านกรมประมง ----------------
def dof(ox=0):
    WALL = mat('DofWall', hexrgb(0xeef0ea), 0.7)
    GREEN = mat('DofGreen', hexrgb(0x11743a), 0.5)
    GLASS = mat('DofGlass', hexrgb(0x5b7da6), 0.1, 0.3)
    FRAME = mat('DofFrame', hexrgb(0x39455c), 0.5, 0.4)
    WHITE = mat('DofText', hexrgb(0xffffff), 0.5)
    AC = mat('DofAC', hexrgb(0xc5ccd5), 0.5, 0.3)
    r = root('DofBuilding'); r.location = (ox, 0, 0)
    W, D, H = 14.0, 6.0, 4.6
    prim('cube', 'Dof_Wall', WALL, loc=(0, 0, H / 2), scale=(W / 2, D / 2, H / 2), parent=r)
    prim('cube', 'Dof_Band', GREEN, loc=(0, 0, H + 0.25), scale=(W / 2 + 0.25, D / 2 + 0.25, 0.3), parent=r)
    prim('cube', 'Dof_Canopy', GREEN, loc=(0, -D / 2 - 1.1, 3.3), scale=(2.6, 1.1, 0.08), parent=r)
    for x in (-2.2, 2.2):
        prim('cylinder', 'Dof_Column', FRAME, loc=(x, -D / 2 - 2.0, 1.65), vertices=10, radius=0.1, depth=3.3, parent=r)
    prim('cube', 'Dof_Entrance', GLASS, loc=(0, -D / 2 - 0.04, 1.4), scale=(1.6, 0.03, 1.4), parent=r)
    prim('cube', 'Dof_DoorFrame', FRAME, loc=(0, -D / 2 - 0.06, 1.4), scale=(0.04, 0.02, 1.4), parent=r)
    for x in (-5.4, -4.0, 4.0, 5.4):
        prim('cube', 'Dof_Window', GLASS, loc=(x, -D / 2 - 0.04, 2.4), scale=(0.55, 0.03, 0.8), parent=r)
    prim('cube', 'Dof_Sign', GREEN, loc=(0, -D / 2 - 0.08, 3.9), scale=(4.2, 0.04, 0.4), parent=r)
    text('FISHERIES INSPECTION & QUARANTINE', 0.32, WHITE, (0, -D / 2 - 0.13, 3.9), (math.radians(90), 0, 0), r, name='Dof_SignText')
    for x in (-4.5, -2.5):                               # เครื่องปรับอากาศบนหลังคา
        prim('cube', 'Dof_AC', AC, loc=(x, 1.2, H + 0.85), scale=(0.6, 0.45, 0.3), parent=r)
    return r


# ---------------- ต้นไม้ ----------------
def trees(ox=0):
    BARK = mat('Bark', hexrgb(0x6e4c32), 0.9)
    PINE = mat('PineLeaf', hexrgb(0x3f7a45), 0.8)
    LEAF = mat('Leaf', hexrgb(0x5f9a4c), 0.8)
    a = root('Tree_Pine'); a.location = (ox - 1.5, 0, 0)
    prim('cylinder', 'Pine_Trunk', BARK, loc=(0, 0, 0.6), vertices=8, radius=0.14, depth=1.2, parent=a)
    for k, (rad, z) in enumerate([(1.1, 1.5), (0.85, 2.3), (0.55, 3.0)]):
        prim('cone', 'Pine_Leaves', PINE, loc=(0, 0, z), vertices=9, radius1=rad, radius2=0.05, depth=1.3, parent=a)
    b = root('Tree_Round'); b.location = (ox + 1.5, 0, 0)
    prim('cylinder', 'Round_Trunk', BARK, loc=(0, 0, 0.8), vertices=8, radius=0.16, depth=1.6, parent=b)
    random.seed(5)
    for k in range(5):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.6, 0.85),
                                              location=(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(2.1, 2.9)))
        lf = bpy.context.active_object; lf.name = 'Round_Leaves'; lf.data.materials.append(LEAF); lf.parent = b
        lf.location = (lf.location.x, lf.location.y, lf.location.z)
    return a, b


ITEMS = [('pond.glb', pond), ('dolly.glb', dolly), ('farmhouse.glb', farmhouse), ('dof.glb', dof), ('trees.glb', trees)]
for fname, build in ITEMS:
    reset(); build(); export_glb(fname)

# ภาพตัวอย่างรวม
reset()
p = pond(-9); p.scale = (2.2, 2.2, 1)
dolly(-4.5); trees(-1.5)
f = farmhouse(0); f.location = (-6, 11, 0)
d = dof(0); d.location = (9, 11, 0)
render_preview('scenery.png', cam_loc=(2, -16, 9), target=(0, 5, 1.5), lens=28, size=(1280, 720))
