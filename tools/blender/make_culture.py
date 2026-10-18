# บรรยากาศประเทศ 2 ชุด สร้างด้วยโค้ดใน Blender:
#   japan.glb  ฝั่งญี่ปุ่น: JP_Torii เสาโทริอิ · JP_Lantern โคมหิน · JP_Sakura ซากุระ · JP_Pine สนญี่ปุ่น · JP_Fuji ภูเขาไฟฟูจิ (ฉากหลัง) · JP_Bamboo รั้วไผ่
#   thai.glb   ฝั่งไทย: TH_SpiritHouse ศาลพระภูมิ · TH_Sala ศาลาทรงไทย · TH_Palm มะพร้าว · TH_Banana กล้วย · TH_Chedi เจดีย์ (ฉากหลัง) · TH_House เรือนไทยใต้ถุนสูง
# ทุกชิ้นวางฐานที่ z = 0 ตรงจุดกำเนิดของตัวเอง (เว็บหยิบไปวางตามชื่อ) · ด้านหน้า = -Y ของ Blender (= +z ในเว็บ)
import bpy, bmesh, math, sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, obj_from_bmesh, prim, root, export_glb, render_preview, lathe


def gable(name, w, d, h, z, material, parent, overhang=0.3, flare=0.0):
    """หลังคาจั่วทรงปริซึม (สันตามแกน x) — flare = ปลายสันงอนขึ้น (แบบไทย)"""
    bm = bmesh.new(); W, D = w / 2 + overhang, d / 2 + overhang
    a = [bm.verts.new(p) for p in [(-W, -D, z), (W, -D, z), (W + flare, 0, z + h + flare * 0.6), (-W - flare, 0, z + h + flare * 0.6), (W, D, z), (-W, D, z)]]
    bm.faces.new([a[0], a[1], a[2], a[3]]); bm.faces.new([a[5], a[3], a[2], a[4]])
    bm.faces.new([a[1], a[4], a[2]]); bm.faces.new([a[0], a[3], a[5]])
    bm.normal_update()
    ob = obj_from_bmesh(name, bm, material, parent=parent)
    m = ob.modifiers.new('solid', 'SOLIDIFY'); m.thickness = 0.12
    return ob


def leaves_cluster(name, parent, center, radius, n, material, seed):
    random.seed(seed)
    for k in range(n):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius * random.uniform(0.55, 0.85),
            location=(center[0] + random.uniform(-radius, radius) * 0.8, center[1] + random.uniform(-radius, radius) * 0.8, center[2] + random.uniform(-radius, radius) * 0.4))
        o = bpy.context.active_object; o.name = name; o.data.materials.append(material); o.parent = parent


# ================= ญี่ปุ่น =================
def japan():
    RED = mat('ToriiRed', hexrgb(0xd23a2a), 0.5); BLACK = mat('ToriiBlack', hexrgb(0x222222), 0.6)
    STONE = mat('LanternStone', hexrgb(0xa7a49c), 0.95); BARK = mat('JBark', hexrgb(0x5e4636), 0.9)
    PINK = mat('Sakura', hexrgb(0xf6b8cf), 0.8); PINK2 = mat('Sakura2', hexrgb(0xfbd3e1), 0.8)
    PINE = mat('JPine', hexrgb(0x2f6b45), 0.85); SNOW = mat('Snow', hexrgb(0xf7f9fb), 0.7)
    ROCK = mat('FujiRock', hexrgb(0x6d7a8f), 0.95); BAMBOO = mat('Bamboo', hexrgb(0xb9a46a), 0.7); ROPE = mat('Rope', hexrgb(0x5a4a33), 0.9)
    # เสาโทริอิ
    t = root('JP_Torii')
    for x in (-1.6, 1.6):
        prim('cylinder', 'Pillar', RED, loc=(x, 0, 2.1), vertices=12, radius=0.2, depth=4.2, smooth=True, parent=t)
        prim('cylinder', 'Base', BLACK, loc=(x, 0, 0.2), vertices=12, radius=0.26, depth=0.4, parent=t)
    prim('cube', 'Kasagi', BLACK, loc=(0, 0, 4.45), scale=(2.6, 0.32, 0.18), parent=t)
    prim('cube', 'Shimaki', RED, loc=(0, 0, 4.15), scale=(2.4, 0.26, 0.14), parent=t)
    prim('cube', 'Nuki', RED, loc=(0, 0, 3.4), scale=(2.2, 0.16, 0.12), parent=t)
    # โคมหิน
    l = root('JP_Lantern')
    prim('cylinder', 'Foot', STONE, loc=(0, 0, 0.12), vertices=6, radius=0.42, depth=0.24, parent=l)
    prim('cylinder', 'Post', STONE, loc=(0, 0, 0.7), vertices=8, radius=0.14, depth=0.95, parent=l)
    prim('cube', 'Light', STONE, loc=(0, 0, 1.35), scale=(0.3, 0.3, 0.22), parent=l)
    prim('cone', 'Hat', STONE, loc=(0, 0, 1.75), vertices=6, radius1=0.55, radius2=0.05, depth=0.45, parent=l)
    # ซากุระ
    s = root('JP_Sakura')
    prim('cylinder', 'Trunk', BARK, loc=(0, 0, 1.0), vertices=8, radius=0.2, depth=2.0, parent=s)
    prim('cylinder', 'Branch', BARK, loc=(0.5, 0, 2.0), rot=(0, math.radians(40), 0), vertices=6, radius=0.09, depth=1.4, parent=s)
    leaves_cluster('Blossom', s, (0, 0, 3.0), 1.4, 7, PINK, 11); leaves_cluster('Blossom', s, (0.3, 0.2, 3.3), 1.0, 4, PINK2, 12)
    # สนญี่ปุ่น (กิ่งเป็นชั้น ๆ)
    p = root('JP_Pine')
    prim('cylinder', 'Trunk', BARK, loc=(0, 0, 1.4), rot=(0, math.radians(8), 0), vertices=8, radius=0.18, depth=2.8, parent=p)
    for (x, z, r) in [(-0.6, 2.2, 0.9), (0.7, 2.8, 0.8), (0, 3.4, 0.7)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(x, 0, z), segments=10, ring_count=5)
        o = bpy.context.active_object; o.name = 'PinePad'; o.scale = (r * 1.4, r * 1.1, r * 0.45); o.data.materials.append(PINE); o.parent = p
    # ภูเขาไฟฟูจิ (ฉากหลังขนาดใหญ่ ยอดหิมะ)
    f = root('JP_Fuji')
    prim('cone', 'Mountain', ROCK, loc=(0, 0, 14), vertices=24, radius1=42, radius2=4, depth=28, parent=f)
    prim('cone', 'SnowCap', SNOW, loc=(0, 0, 24.15), vertices=24, radius1=15.2, radius2=4.3, depth=8.1, parent=f)
    # รั้วไผ่ (ยาว 4)
    b = root('JP_Bamboo')
    for k in range(17):
        prim('cylinder', 'Pole', BAMBOO, loc=(-2 + k * 0.25, 0, 0.75), vertices=8, radius=0.07, depth=1.5, parent=b)
    for z in (0.5, 1.15):
        prim('cylinder', 'Rail', BAMBOO, loc=(0, -0.09, z), rot=(0, math.radians(90), 0), vertices=8, radius=0.05, depth=4.2, parent=b)
        prim('torus', 'Tie', ROPE, loc=(-1.5, -0.1, z), rot=(0, math.radians(90), 0), major_radius=0.08, minor_radius=0.025, parent=b)


# ================= ไทย =================
def thai():
    GOLD = mat('Gold', hexrgb(0xe0b24a), 0.35, 0.6); WHITE = mat('ThaiWhite', hexrgb(0xf4f1ea), 0.8)
    ROOF_R = mat('RoofRed', hexrgb(0xb63a2a), 0.6); ROOF_G = mat('RoofGreen', hexrgb(0x2e7d4f), 0.6)
    TEAK = mat('Teak', hexrgb(0x7a4a2a), 0.75); BARK = mat('PalmBark', hexrgb(0x8a6b4a), 0.9)
    FROND = mat('Frond', hexrgb(0x3f8f3a), 0.8); BANANA = mat('Banana', hexrgb(0x6fae3e), 0.7)
    PINK = mat('Garland', hexrgb(0xe0598b), 0.6)
    # ศาลพระภูมิ (บ้านเล็กทองบนเสา) + พวงมาลัย
    sp = root('TH_SpiritHouse')
    prim('cylinder', 'Pedestal', WHITE, loc=(0, 0, 0.7), vertices=8, radius=0.18, depth=1.4, parent=sp)
    prim('cube', 'Deck', GOLD, loc=(0, 0, 1.45), scale=(0.65, 0.65, 0.05), parent=sp)
    prim('cube', 'Shrine', GOLD, loc=(0, 0, 1.8), scale=(0.4, 0.4, 0.35), parent=sp)
    gable('ShrineRoof', 0.9, 0.9, 0.55, 2.15, ROOF_R, sp, 0.12, 0.12)
    prim('cone', 'Spire', GOLD, loc=(0, 0, 3.0), vertices=8, radius1=0.12, radius2=0.0, depth=0.6, parent=sp)
    prim('torus', 'Garland', PINK, loc=(0, -0.41, 1.75), rot=(math.radians(90), 0, 0), major_radius=0.18, minor_radius=0.04, parent=sp)
    # ศาลาทรงไทย (เสา 4 ต้น หลังคาซ้อน 2 ชั้น สีแดง-เขียว ปลายจั่วงอน)
    sa = root('TH_Sala')
    prim('cube', 'Floor', TEAK, loc=(0, 0, 0.3), scale=(2.0, 1.5, 0.3), parent=sa)
    for x in (-1.7, 1.7):
        for y in (-1.2, 1.2):
            prim('cylinder', 'Column', WHITE, loc=(x, y, 1.75), vertices=8, radius=0.12, depth=2.6, parent=sa)
    gable('SalaRoof1', 3.8, 2.8, 1.3, 3.0, ROOF_R, sa, 0.45, 0.35)
    gable('SalaRoof2', 2.6, 1.9, 1.2, 3.8, ROOF_G, sa, 0.25, 0.4)
    for x in (-2.35, 2.35):
        prim('cone', 'Chofa', GOLD, loc=(x * 0.85, 0, 5.15), rot=(0, x / abs(x) * math.radians(-35), 0), vertices=6, radius1=0.09, radius2=0.0, depth=0.6, parent=sa)
    # ต้นมะพร้าว (ลำต้นโค้ง ใบห้อย 8 ใบ)
    pa = root('TH_Palm')
    for k in range(6):
        prim('cylinder', 'PalmTrunk', BARK, loc=(k * 0.08, 0, 0.55 + k * 1.0), rot=(0, math.radians(5), 0), vertices=8, radius=0.2 - k * 0.012, depth=1.05, parent=pa)
    for k in range(8):
        a = 2 * math.pi * k / 8
        prim('cube', 'Frond', FROND, loc=(0.45 + math.cos(a) * 1.1, math.sin(a) * 1.1, 6.0), rot=(0, math.radians(18), a), scale=(1.25, 0.28, 0.03), parent=pa)
    leaves_cluster('Coconut', pa, (0.45, 0, 5.75), 0.25, 3, mat('Coconut', hexrgb(0x6b5a2e), 0.8), 21)
    # ต้นกล้วย (ใบกว้างตั้งขึ้น)
    ba = root('TH_Banana')
    prim('cylinder', 'Stem', BANANA, loc=(0, 0, 1.0), vertices=8, radius=0.18, depth=2.0, parent=ba)
    for k in range(6):
        a = 2 * math.pi * k / 6
        prim('cube', 'Leaf', BANANA, loc=(math.cos(a) * 0.7, math.sin(a) * 0.7, 2.3), rot=(math.radians(25) * math.sin(a), math.radians(-25) * math.cos(a), a), scale=(0.8, 0.28, 0.02), parent=ba)
    # เจดีย์ (ฉากหลัง ทรงระฆังขาว ยอดทอง)
    ch = root('TH_Chedi')
    prim('cylinder', 'Base1', WHITE, loc=(0, 0, 0.8), vertices=16, radius=6, depth=1.6, parent=ch)
    prim('cylinder', 'Base2', WHITE, loc=(0, 0, 2.2), vertices=16, radius=4.6, depth=1.2, parent=ch)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.6, location=(0, 0, 4.6), segments=20, ring_count=10)
    o = bpy.context.active_object; o.name = 'Bell'; o.scale = (1, 1, 1.15); o.data.materials.append(WHITE); o.parent = ch
    prim('cone', 'Spire', GOLD, loc=(0, 0, 11), vertices=16, radius1=1.2, radius2=0.05, depth=8, parent=ch)
    # เรือนไทยใต้ถุนสูง (ฟาร์มบริษัทในไทย): เสาสูง ห้องไม้สัก หลังคาจั่วสูงชันปลายงอน ระเบียงหน้าบ้าน
    th = root('TH_House')
    for x in (-3.6, -1.2, 1.2, 3.6):
        for y in (-2.4, 2.4):
            prim('cylinder', 'Stilt', TEAK, loc=(x, y, 1.0), vertices=8, radius=0.16, depth=2.0, parent=th)
    prim('cube', 'Platform', TEAK, loc=(0, -0.6, 2.05), scale=(4.2, 3.4, 0.1), parent=th)
    prim('cube', 'Room', TEAK, loc=(0, 0.8, 3.4), scale=(3.8, 1.9, 1.3), parent=th)
    for x in (-2.5, 0, 2.5):
        prim('cube', 'Window', mat('Shutter', hexrgb(0x4a2f1c), 0.7), loc=(x, -1.12, 3.4), scale=(0.45, 0.02, 0.6), parent=th)
    gable('HouseRoof', 7.6, 3.8, 3.0, 4.7, ROOF_R, th, 0.6, 0.6)
    prim('cube', 'Stairs', TEAK, loc=(0, -4.3, 1.0), rot=(math.radians(-40), 0, 0), scale=(0.7, 0.12, 1.45), parent=th)
    for x in (-4.1, 4.1):
        prim('cube', 'Rail', TEAK, loc=(x * 0.98, -2.2, 2.45), scale=(0.05, 1.8, 0.35), parent=th)


reset(); japan(); export_glb('japan.glb')
reset(); thai(); export_glb('thai.glb')

# ภาพตัวอย่าง: วางทุกชิ้นเรียงกัน
reset(); japan()
for name, x, y in [('JP_Torii', -8, 0), ('JP_Lantern', -5, 0), ('JP_Sakura', -2.5, 0), ('JP_Pine', 0.5, 0), ('JP_Bamboo', 4, 0), ('JP_Fuji', 0, 70)]:
    bpy.data.objects[name].location = (x, y, 0)
render_preview('japan.png', cam_loc=(0, -18, 7), target=(0, 6, 3), lens=30, size=(1280, 720))
reset(); thai()
for name, x, y in [('TH_SpiritHouse', -9, 0), ('TH_Sala', -5, 0), ('TH_Palm', -1, 0), ('TH_Banana', 1.5, 0), ('TH_House', 7, 3), ('TH_Chedi', -4, 30)]:
    bpy.data.objects[name].location = (x, y, 0)
render_preview('thai.png', cam_loc=(0, -20, 7), target=(0, 6, 3), lens=30, size=(1280, 720))
