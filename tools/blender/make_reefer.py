# รถบรรทุกห้องเย็น (ควบคุมอุณหภูมิ) สำหรับขนกล่องปลา → assets/models/reefer.glb
# ในเว็บ: หัวรถไปทาง +x ยาวราว 7.5 กว้าง 2.4 · ท้ายตู้มีประตูคู่ · เครื่องทำความเย็นอยู่หน้าตู้ด้านบน
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, render_preview, text, bevel_box

reset()
CAB = mat('Cab', hexrgb(0x2f5fb5), 0.35, 0.2)
BOX = mat('ReeferBox', hexrgb(0xf4f6f8), 0.5)
TRIM = mat('ReeferTrim', hexrgb(0x9aa3ae), 0.4, 0.6)
UNIT = mat('ReeferUnit', hexrgb(0x5d6876), 0.5, 0.3)
GRILL = mat('Grill', hexrgb(0x1d2b3a), 0.6)
GLASS = mat('CabGlass', hexrgb(0x2b3d55), 0.1, 0.3)
TYRE = mat('TruckTyre', hexrgb(0x1d1f24), 0.9)
RIM = mat('TruckRim', hexrgb(0xc5ccd5), 0.3, 0.8)
LIGHT = mat('HeadLight', hexrgb(0xfff4c2), 0.2)
RED = mat('TailLight', hexrgb(0xd9423e), 0.3)
INK = mat('ReeferText', hexrgb(0x2f5fb5), 0.5)

t = root('Reefer')
# แชสซี + ตู้ห้องเย็น (ขอบมน) + แถบกันชนท้าย
prim('cube', 'Chassis', GRILL, loc=(-0.2, 0, 0.75), scale=(3.6, 1.0, 0.18), parent=t)
bevel_box('ColdBox', (5.2, 2.4, 2.6), (-1.1, 0, 2.25), BOX, t, 0.06)
for x in (-3.65, 1.45):
    prim('cube', 'BoxFrame', TRIM, loc=(x, 0, 2.25), scale=(0.06, 1.22, 1.32), parent=t)
prim('cube', 'BoxRail', TRIM, loc=(-1.1, 0, 0.96), scale=(2.62, 1.22, 0.05), parent=t)
# ประตูคู่ท้ายตู้ + มือจับ
for y in (-0.6, 0.6):
    prim('cube', 'RearDoor', BOX, loc=(-3.72, y, 2.25), scale=(0.02, 0.58, 1.25), parent=t)
    prim('cube', 'DoorBar', TRIM, loc=(-3.75, y * 0.4, 2.25), scale=(0.02, 0.03, 1.1), parent=t)
for y in (-1.0, 1.0):
    prim('cube', 'TailLamp', RED, loc=(-3.75, y, 1.05), scale=(0.03, 0.15, 0.1), parent=t)
# เครื่องทำความเย็น (กล่องเทาหน้าตู้ด้านบน มีตะแกรง)
prim('cube', 'CoolingUnit', UNIT, loc=(1.62, 0, 3.0), scale=(0.18, 0.85, 0.55), parent=t)
for k in range(5):
    prim('cube', 'UnitGrill', GRILL, loc=(1.81, 0, 2.6 + k * 0.2), scale=(0.01, 0.75, 0.04), parent=t)
# หัวรถ: ห้องโดยสาร + กระจก + ไฟหน้า + กันชน
bevel_box('CabBody', (1.9, 2.3, 2.2), (2.7, 0, 1.95), CAB, t, 0.12)
prim('cube', 'Windshield', GLASS, loc=(3.66, 0, 2.45), rot=(0, math.radians(-12), 0), scale=(0.03, 1.0, 0.5), parent=t)
for y in (-1.16, 1.16):
    prim('cube', 'SideWindow', GLASS, loc=(2.8, y, 2.45), scale=(0.55, 0.02, 0.4), parent=t)
prim('cube', 'Bumper', GRILL, loc=(3.68, 0, 0.95), scale=(0.08, 1.15, 0.18), parent=t)
for y in (-0.85, 0.85):
    prim('cube', 'HeadLamp', LIGHT, loc=(3.68, y, 1.35), scale=(0.03, 0.18, 0.1), parent=t)
# ล้อ (หน้า 1 คู่ หลัง 2 คู่)
for x in (2.7, -1.9, -2.9):
    for y in (-1.05, 1.05):
        prim('cylinder', 'Tyre', TYRE, loc=(x, y, 0.5), rot=(math.radians(90), 0, 0), vertices=18, radius=0.5, depth=0.32, smooth=True, parent=t)
        prim('cylinder', 'Rim', RIM, loc=(x, y * 1.17, 0.5), rot=(math.radians(90), 0, 0), vertices=12, radius=0.26, depth=0.04, parent=t)
# ข้อความข้างตู้ (ด้าน -Y = ฝั่งกล้องในเว็บ)
text('LIVE KOI  -  TEMP CONTROLLED', 0.26, INK, (-1.1, -1.235, 2.4), (math.radians(90), 0, 0), t, name='BoxText')
text('LIVE ANIMALS - HANDLE WITH CARE', 0.2, INK, (-1.1, -1.235, 1.95), (math.radians(90), 0, 0), t, name='BoxText2')

export_glb('reefer.glb')
render_preview('reefer.png', cam_loc=(7, -10, 5), target=(0, 0, 1.6), lens=40)
