# ยานพาหนะกลุ่ม 2 (ปั้นใหม่ 1 พ.ย. 2026 ตามภาพใน โมเดล/Group 2/) ส่งออกทีละไฟล์:
#   reefer.glb   รถบรรทุกห้องเย็น (หัวรถไป +x ยาว 7.5) ตู้ขาวมีโลโก้หลักสูตร
#   van.glb      รถตู้ส่งของสีขาวมีโลโก้ (หัวรถไป -y ของ Blender แบบชุด Kenney เดิม — โค้ดในเว็บหมุนให้หันไป +x เอง)
#   tractor.glb  รถลากลานจอด (tug) สีเหลือง ห้องคนขับเปิดข้าง (หัวรถไป -y เหมือนรถตู้)
#   dolly.glb    แท่นลากวางกล่อง มีลูกกลิ้ง คานพ่วงชี้ไป +x (รถลากอยู่ด้านหน้า) ด้านบนแท่นสูง 1.35
#   cone.glb     กรวยจราจรส้มคาดขาว ฐานสี่เหลี่ยมดำ
# ขนาดของรถตู้/รถลาก/กรวยไม่ต้องเป๊ะ: เว็บย่อขยายให้ยาวตามที่ฉากกำหนดเอง
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, bevel_box, logo_decal, wheel


def mats():
    """สีชุดเดียวกันทุกคัน (เรียกหลัง reset ทุกครั้ง)"""
    return dict(
        WHITE=mat('Paint_White', hexrgb(0xfbfbfb), 0.45),   # ขาวเกือบสนิท กลืนกับพื้นขาวของภาพโลโก้
        GREY=mat('Paint_Grey', hexrgb(0x6b7076), 0.6),
        DARK=mat('Chassis', hexrgb(0x2a2d31), 0.7),
        YELLOW=mat('Paint_Yellow', hexrgb(0xf0b323), 0.5),
        GLASS=mat('Glass', hexrgb(0x3b4654), 0.15, 0.3),
        TYRE=mat('Tyre', hexrgb(0x1e2023), 0.9),
        RIM=mat('Rim', hexrgb(0x9aa0a6), 0.4, 0.6),
        LAMP=mat('Lamp', hexrgb(0xffd27a), 0.3),
        TAIL=mat('TailLamp', hexrgb(0xd9423e), 0.3),
        ORANGE=mat('Indicator', hexrgb(0xf08a24), 0.4),
        STEEL=mat('Steel', hexrgb(0xb8bec4), 0.35, 0.7),
    )


# ---------------- รถห้องเย็น ----------------
def reefer():
    M = mats(); t = root('Reefer')
    # แชสซีดำ + ถังน้ำมัน/กล่องเครื่องมือใต้ตู้
    prim('cube', 'Chassis', M['DARK'], loc=(-0.2, 0, 0.72), scale=(3.65, 0.95, 0.14), parent=t)
    prim('cube', 'SideBox', M['DARK'], loc=(0.2, -0.9, 0.62), scale=(0.6, 0.12, 0.2), parent=t)
    # ตู้ห้องเย็นสีขาว ขอบเทา
    bevel_box('ColdBox', (5.3, 2.4, 2.45), (-1.05, 0, 2.1), M['WHITE'], t, 0.05)
    prim('cube', 'BoxRail', M['GREY'], loc=(-1.05, 0, 0.9), scale=(2.66, 1.22, 0.04), parent=t)
    for x in (-3.7, 1.6):
        prim('cube', 'BoxFrame', M['GREY'], loc=(x, 0, 2.1), scale=(0.05, 1.22, 1.24), parent=t)
    # เครื่องทำความเย็นหน้าตู้ด้านบน (กล่องเทามีตะแกรง)
    prim('cube', 'CoolingUnit', M['GREY'], loc=(1.75, 0, 2.9), scale=(0.16, 0.8, 0.38), parent=t)
    for k in range(4):
        prim('cube', 'UnitGrill', M['DARK'], loc=(1.92, 0, 2.66 + k * 0.15), scale=(0.01, 0.7, 0.03), parent=t)
    # ท้ายตู้: ประตูคู่ + ไฟท้าย
    for y in (-0.6, 0.6):
        prim('cube', 'RearDoor', M['WHITE'], loc=(-3.72, y, 2.1), scale=(0.02, 0.58, 1.18), parent=t)
    for y in (-1.0, 1.0):
        prim('cube', 'TailLamp', M['TAIL'], loc=(-3.75, y, 0.95), scale=(0.03, 0.14, 0.08), parent=t)
    # หัวรถสีขาว: ห้องโดยสารทรงกล่องหน้าตัด + กระจก + กระจกมองข้าง + ไฟ + กันชน
    bevel_box('CabBody', (1.8, 2.3, 1.9), (2.75, 0, 1.75), M['WHITE'], t, 0.1)
    bevel_box('CabFront', (0.3, 2.2, 0.8), (3.72, 0, 1.15), M['WHITE'], t, 0.06)
    prim('cube', 'Windshield', M['GLASS'], loc=(3.66, 0, 2.15), rot=(0, math.radians(-8), 0), scale=(0.02, 1.0, 0.42), parent=t)
    for s in (1, -1):
        prim('cube', 'SideWindow', M['GLASS'], loc=(2.95, s * 1.155, 2.15), scale=(0.5, 0.01, 0.36), parent=t)
        prim('cube', 'Mirror', M['DARK'], loc=(3.55, s * 1.3, 2.1), scale=(0.04, 0.08, 0.18), parent=t)
        prim('cube', 'HeadLamp', M['LAMP'], loc=(3.88, s * 0.82, 1.2), scale=(0.02, 0.18, 0.09), parent=t)
        prim('cube', 'Indicator', M['ORANGE'], loc=(3.88, s * 1.05, 1.2), scale=(0.02, 0.05, 0.09), parent=t)
    prim('cube', 'Grill', M['DARK'], loc=(3.88, 0, 1.2), scale=(0.02, 0.5, 0.15), parent=t)
    prim('cube', 'Bumper', M['DARK'], loc=(3.85, 0, 0.82), scale=(0.08, 1.15, 0.13), parent=t)
    # ล้อ: หน้า 1 คู่ หลัง 1 คู่ (ล้อคู่)
    for x in (2.75, -2.3):
        for y in (-1.0, 1.0):
            wheel('Wheel', (x, y, 0.48), 0.48, 0.34, M['TYRE'], M['RIM'], t)
    # โลโก้หลักสูตรข้างตู้ทั้งสองข้าง
    logo_decal('BoxLogo', t, (-1.05, -1.207, 2.15), 4.0, '-y')
    logo_decal('BoxLogo', t, (-1.05, 1.207, 2.15), 4.0, '+y')
    return t


# ---------------- รถตู้ (หน้ารถไป -y) ----------------
def van():
    M = mats(); t = root('Van')
    L, W = 4.6, 1.9
    # ตัวถัง: ช่วงหลังทรงกล่องสูง + ช่วงหน้าลาดลงเป็นฝากระโปรงสั้น
    bevel_box('VanBody', (W, 3.5, 1.65), (0, 0.5, 1.3), M['WHITE'], t, 0.1)
    bevel_box('VanNose', (W, 1.0, 0.75), (0, -1.75, 0.85), M['WHITE'], t, 0.12)
    # กระจกหน้าแปะที่หน้าตัวถังช่วงบน (เหนือฝากระโปรง)
    prim('cube', 'Windshield', M['GLASS'], loc=(0, -1.255, 1.65), scale=(0.86, 0.01, 0.34), parent=t)
    for s in (1, -1):
        prim('cube', 'SideWindow', M['GLASS'], loc=(s * (W / 2 + 0.005), -0.78, 1.62), scale=(0.01, 0.4, 0.3), parent=t)
        prim('cube', 'Mirror', M['DARK'], loc=(s * 1.05, -1.2, 1.45), scale=(0.08, 0.04, 0.12), parent=t)
        prim('cube', 'HeadLamp', M['LAMP'], loc=(s * 0.7, -2.255, 0.95), scale=(0.18, 0.02, 0.08), parent=t)
        prim('cube', 'Indicator', M['ORANGE'], loc=(s * 0.9, -2.255, 0.95), scale=(0.05, 0.02, 0.08), parent=t)
        prim('cube', 'TailLamp', M['TAIL'], loc=(s * 0.85, 2.255, 1.0), scale=(0.07, 0.02, 0.22), parent=t)
        prim('cube', 'DoorHandle', M['DARK'], loc=(s * (W / 2 + 0.01), -0.35, 1.25), scale=(0.01, 0.1, 0.02), parent=t)
    prim('cube', 'Grill', M['DARK'], loc=(0, -2.255, 0.8), scale=(0.5, 0.02, 0.12), parent=t)
    prim('cube', 'FrontBumper', M['DARK'], loc=(0, -2.25, 0.45), scale=(0.98, 0.08, 0.14), parent=t)
    prim('cube', 'RearBumper', M['DARK'], loc=(0, 2.25, 0.45), scale=(0.98, 0.08, 0.12), parent=t)
    prim('cube', 'Sill', M['DARK'], loc=(0, 0, 0.42), scale=(0.94, 2.1, 0.08), parent=t)
    for y in (-1.5, 1.5):
        for x in (-0.82, 0.82):
            wheel('Wheel', (x, y, 0.36), 0.36, 0.24, M['TYRE'], M['RIM'], t, axis='x')
    # โลโก้ข้างตัวถังทั้งสองข้าง (ด้าน ±x ของ Blender = ด้านข้างรถในเว็บ)
    logo_decal('VanLogo', t, (-W / 2 - 0.012, 1.0, 1.3), 2.1, '-x')
    logo_decal('VanLogo', t, (W / 2 + 0.012, 1.0, 1.3), 2.1, '+x')
    return t


# ---------------- รถลากลานจอด (หน้ารถไป -y) ----------------
def tractor():
    M = mats(); t = root('Tractor')
    # แชสซีเทา + ตัวถังเหลือง ฝากระโปรงหน้าลาด
    prim('cube', 'Chassis', M['GREY'], loc=(0, 0, 0.55), scale=(0.85, 1.75, 0.22), parent=t)
    bevel_box('Hood', (1.6, 1.3, 0.55), (0, -0.95, 1.0), M['YELLOW'], t, 0.08)
    bevel_box('RearDeck', (1.6, 1.2, 0.35), (0, 1.1, 0.9), M['GREY'], t, 0.05)
    # ห้องคนขับ: เสา 4 ต้น + หลังคา + ผนังหลังมีกระจก (ด้านข้างเปิด)
    bevel_box('CabFloor', (1.6, 1.0, 0.3), (0, 0.05, 0.85), M['YELLOW'], t, 0.04)
    for x in (-0.76, 0.76):
        for y in (-0.42, 0.52):
            prim('cube', 'CabPost', M['YELLOW'], loc=(x, y, 1.45), scale=(0.04, 0.04, 0.5), parent=t)
    bevel_box('CabRoof', (1.66, 1.06, 0.08), (0, 0.05, 1.98), M['YELLOW'], t, 0.03)
    prim('cube', 'Windshield', M['GLASS'], loc=(0, -0.42, 1.55), scale=(0.72, 0.01, 0.35), parent=t)
    prim('cube', 'Seat', M['DARK'], loc=(0, 0.25, 1.15), scale=(0.3, 0.2, 0.15), parent=t)
    prim('cube', 'SeatBack', M['DARK'], loc=(0, 0.42, 1.4), scale=(0.3, 0.05, 0.22), parent=t)
    # หน้ารถ: กระจังเทาเข้ม ไฟ กันชน + ขอพ่วงหน้า/หลัง
    prim('cube', 'Grill', M['DARK'], loc=(0, -1.61, 1.0), scale=(0.45, 0.02, 0.2), parent=t)
    for s in (1, -1):
        prim('cube', 'HeadLamp', M['LAMP'], loc=(s * 0.62, -1.61, 0.95), scale=(0.08, 0.02, 0.06), parent=t)
        prim('cube', 'TailLamp', M['TAIL'], loc=(s * 0.62, 1.71, 0.9), scale=(0.1, 0.02, 0.07), parent=t)
        prim('cube', 'Mirror', M['DARK'], loc=(s * 0.92, -0.42, 1.6), scale=(0.05, 0.02, 0.1), parent=t)
    prim('cube', 'FrontBumper', M['GREY'], loc=(0, -1.72, 0.6), scale=(0.85, 0.08, 0.12), parent=t)
    for y, n in ((-1.95, 'TowHitchFront'), (1.95, 'TowHitch')):
        prim('cube', n, M['STEEL'], loc=(0, y, 0.6), scale=(0.08, 0.2, 0.05), parent=t)
    for y in (-0.95, 1.05):
        for x in (-0.78, 0.78):
            wheel('Wheel', (x, y, 0.4), 0.4, 0.3, M['TYRE'], M['RIM'], t, axis='x')
    # โลโก้ที่ประตูข้างห้องคนขับ (ทั้งสองข้าง)
    logo_decal('DoorLogo', t, (-0.82, 0.05, 1.05), 0.7, '-x')
    logo_decal('DoorLogo', t, (0.82, 0.05, 1.05), 0.7, '+x')
    return t


# ---------------- แท่นลาก (คานพ่วงไป +x) ----------------
def dolly():
    M = mats(); t = root('Dolly')
    L, W, TOP = 3.2, 2.0, 1.35
    # โครงล่างเหลือง + โต๊ะแท่นด้านบน (ขอบบนสูง TOP)
    bevel_box('Frame', (L - 0.3, W - 0.2, 0.25), (0, 0, 0.55), M['YELLOW'], t, 0.03)
    bevel_box('Body', (L - 0.6, W - 0.4, 0.45), (-0.1, 0, 0.9), M['YELLOW'], t, 0.03)
    bevel_box('Deck', (L, W, 0.1), (0, 0, TOP - 0.15), M['YELLOW'], t, 0.02)
    # ลูกกลิ้ง 9 แท่งขวางตามแนวยาว (ผิวบนพอดี TOP)
    for k in range(9):
        x = -L / 2 + 0.2 + k * (L - 0.4) / 8
        prim('cylinder', 'Roller', M['GREY'], loc=(x, 0, TOP - 0.05), rot=(math.radians(90), 0, 0), vertices=8, radius=0.05, depth=W - 0.25, parent=t)
    # ราวกั้นท้ายและราวสั้นด้านข้าง
    for x in (-L / 2 + 0.04, L / 2 - 0.04):
        prim('cube', 'EndRail', M['YELLOW'], loc=(x, 0, TOP + 0.12), scale=(0.03, W / 2 - 0.05, 0.03), parent=t)
        for y in (-W / 2 + 0.08, W / 2 - 0.08):
            prim('cube', 'RailPost', M['YELLOW'], loc=(x, y, TOP + 0.05), scale=(0.03, 0.03, 0.1), parent=t)
    # ล้อ 4 ล้อ + คานพ่วงรูปสามเหลี่ยมชี้ไป +x
    for x in (-1.05, 1.05):
        for y in (-0.85, 0.85):
            wheel('Wheel', (x, y, 0.3), 0.3, 0.2, M['TYRE'], M['RIM'], t)
    for s in (1, -1):
        prim('cube', 'DrawbarArm', M['STEEL'], loc=(1.95, s * 0.22, 0.45), rot=(0, 0, -s * math.radians(22)), scale=(0.45, 0.035, 0.035), parent=t)
    prim('cube', 'Drawbar', M['STEEL'], loc=(2.6, 0, 0.45), scale=(0.3, 0.035, 0.035), parent=t)
    prim('torus', 'DrawbarEye', M['STEEL'], loc=(2.95, 0, 0.45), major_radius=0.08, minor_radius=0.025, major_segments=10, minor_segments=4, parent=t)
    prim('cube', 'RearHook', M['DARK'], loc=(-L / 2 - 0.05, 0, 0.55), scale=(0.06, 0.05, 0.06), parent=t)
    return t


# ---------------- กรวยจราจร ----------------
def cone():
    ORANGE = mat('ConeOrange', hexrgb(0xf26a1b), 0.5)
    WHITE = mat('ConeWhite', hexrgb(0xf4f4f4), 0.5)
    BASE = mat('ConeBase', hexrgb(0x2d3136), 0.7)
    t = root('Cone')
    bevel_box('ConeBase', (0.6, 0.6, 0.05), (0, 0, 0.025), BASE, t, 0.02)
    # กรวย 12 เหลี่ยม แบ่งเป็นปล้องส้ม/ขาวสลับ (ล่าง → บน)
    bands = [(0.05, 0.38, ORANGE), (0.38, 0.5, WHITE), (0.5, 0.64, ORANGE), (0.64, 0.75, WHITE), (0.75, 1.0, ORANGE)]
    def radius(z):
        return 0.24 - (z - 0.05) / 0.95 * 0.19
    for z0, z1, m in bands:
        prim('cone', 'ConeBand', m, loc=(0, 0, (z0 + z1) / 2), vertices=12, radius1=radius(z0), radius2=radius(z1), depth=z1 - z0, parent=t)
    return t


# ---------------- รถ loader ยกตู้ ULD ขึ้นท้องเครื่อง (หัวรถไป +x) ----------------
# ในเว็บ: Loader_Deck = แท่นยก (โค้ดเลื่อนขึ้นลงตามแกนตั้ง) ฐานแท่นอยู่ที่ความสูง DECK_Z
#         Loader_Scissor = ขากรรไกร (จุดหมุนอยู่ที่หลังแชสซี โค้ดยืดตามแกนตั้งให้ตามแท่นได้)
DECK_Z = 2.0          # ความสูงแท่นตอนยกพร้อมส่งตู้ (ราวระดับธรณีประตูห้องสินค้าของเครื่องบินในฉาก)


def loader():
    M = mats(); t = root('Loader')
    BASE = 0.95                                            # ความสูงหลังแชสซี
    # แชสซียาวสีเหลือง + แผงด้านข้างสีเทา
    bevel_box('Chassis', (7.6, 2.6, 0.45), (-0.3, 0, BASE - 0.22), M['YELLOW'], t, 0.04)
    for s in (1, -1):
        prim('cube', 'SidePanel', M['GREY'], loc=(-0.6, s * 1.305, BASE - 0.25), scale=(1.2, 0.01, 0.12), parent=t)
    # ห้องคนขับเล็กที่หัวรถด้านขวา (+x) มีกระจกรอบ
    bevel_box('Cab', (1.5, 1.2, 1.4), (3.0, -0.6, BASE + 0.7), M['YELLOW'], t, 0.06)
    prim('cube', 'CabWindow', M['GLASS'], loc=(3.755, -0.6, BASE + 0.95), scale=(0.01, 0.48, 0.32), parent=t)
    prim('cube', 'CabSideWindow', M['GLASS'], loc=(3.0, -1.205, BASE + 0.95), scale=(0.5, 0.01, 0.32), parent=t)
    for s in (1, -1):
        prim('cube', 'HeadLamp', M['LAMP'], loc=(3.62, s * 1.0, BASE - 0.2), scale=(0.02, 0.12, 0.07), parent=t)
    prim('cube', 'Bumper', M['DARK'], loc=(3.55, 0, BASE - 0.42), scale=(0.08, 1.3, 0.1), parent=t)
    # ล้อ: หน้า 1 คู่ หลัง 2 คู่ (เพลาคู่)
    for x in (2.6, -2.2, -3.1):
        for y in (-1.15, 1.15):
            wheel('Wheel', (x, y, 0.45), 0.45, 0.32, M['TYRE'], M['RIM'], t)

    # ขากรรไกรยก (X ไขว้กันสองข้าง) — ตัวแม่ว่างที่หลังแชสซี
    sc = bpy.data.objects.new('Loader_Scissor', None); bpy.context.scene.collection.objects.link(sc)
    sc.parent = t; sc.location = (-0.9, 0, BASE)
    h = DECK_Z - BASE                                      # ระยะยกที่ขากรรไกรต้องรับ
    arm = math.hypot(3.6, h)
    ang = math.atan2(h, 3.6)
    for s in (1, -1):
        for d in (1, -1):
            prim('cube', 'ScissorArm', M['GREY'], loc=(0, s * 0.95, h / 2), rot=(0, d * ang, 0), scale=(arm / 2, 0.06, 0.06), parent=sc)
    prim('cylinder', 'ScissorPin', M['STEEL'], loc=(0, 0, h / 2), rot=(math.radians(90), 0, 0), vertices=8, radius=0.07, depth=2.1, parent=sc)

    # แท่นยกพร้อมลูกกลิ้ง + ราวกั้นปลายแท่น (ด้านหัวรถ) — ตัวแม่ว่างชื่อ Loader_Deck
    dk = bpy.data.objects.new('Loader_Deck', None); bpy.context.scene.collection.objects.link(dk)
    dk.parent = t; dk.location = (-0.9, 0, DECK_Z)
    bevel_box('DeckPlate', (5.0, 2.6, 0.16), (0, 0, 0.08), M['GREY'], dk, 0.02)
    for k in range(12):
        prim('cylinder', 'DeckRoller', M['STEEL'], loc=(-2.3 + k * 0.42, 0, 0.2), rot=(math.radians(90), 0, 0), vertices=6, radius=0.05, depth=2.3, parent=dk)
    for s in (1, -1):
        prim('cube', 'DeckEdge', M['YELLOW'], loc=(0, s * 1.28, 0.22), scale=(2.5, 0.03, 0.06), parent=dk)
    # ราวกั้นรูปตัว U ที่ปลายแท่นด้านหัวรถ (กันตู้ไหลตก) + เสาราวข้าง
    for s in (1, -1):
        prim('cube', 'GuardPost', M['YELLOW'], loc=(2.4, s * 1.2, 0.65), scale=(0.04, 0.04, 0.5), parent=dk)
    prim('cube', 'GuardRail', M['YELLOW'], loc=(2.4, 0, 1.15), scale=(0.04, 1.2, 0.04), parent=dk)
    prim('cube', 'GuardRail', M['YELLOW'], loc=(2.4, 0, 0.75), scale=(0.03, 1.2, 0.03), parent=dk)
    # โลโก้ที่ประตูห้องคนขับ
    logo_decal('CabLogo', t, (3.0, -1.212, BASE + 0.35), 0.9, '-y')
    return t


ITEMS = [('reefer.glb', reefer), ('van.glb', van), ('tractor.glb', tractor), ('dolly.glb', dolly), ('cone.glb', cone),
         ('loader.glb', loader)]
ONLY = os.environ.get('KOI_ONLY')            # ตั้งค่าเพื่อสร้างชิ้นเดียว เช่น KOI_ONLY=van
for fname, build in ITEMS:
    if ONLY and not fname.startswith(ONLY):
        continue
    reset(); build(); export_glb(fname)
