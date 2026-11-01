# คนทำงาน (สูง 1.75) → assets/models/person.glb
# รุ่นปั้นใหม่ (1 พ.ย. 2026) ตามภาพอ้างอิง โมเดล/Group 1/person.jpg: หมวกแก๊ป เสื้อโปโลแขนสั้นมีป้ายชื่อ
# กางเกงกรมท่า ถุงมือ และรองเท้าบูตสีน้ำตาล ทรงโลว์โพลีเห็นเหลี่ยม
# ในเว็บ: หันหน้าไปทาง +z (ใน Blender คือ -y), แขนเป็นวัตถุลูกชื่อ Person_ArmL / Person_ArmR จุดหมุนที่หัวไหล่
#   ท่าปกติแขนห้อยลงข้างตัว (โค้ดหมุนแขนขึ้นเองตอนยก/ชี้) — ภาพอ้างอิงกางแขนเพื่อให้เห็นรูปทรงเท่านั้น
# สีเสื้อใช้วัสดุชื่อ "Shirt" — เว็บจะเปลี่ยนสีเสื้อตามบทบาท (เกษตรกร ผู้ตรวจ พนักงานภาคพื้น ฯลฯ) ค่าเริ่มต้นสีส้มตามภาพ
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, render_preview

reset()
SHIRT = mat('Shirt', hexrgb(0xe8762c), 0.75)
PANTS = mat('Pants', hexrgb(0x27324a), 0.85)
SKIN = mat('Skin', hexrgb(0xe0a77c), 0.6)
HAIR = mat('Hair', hexrgb(0x3a2a20), 0.85)
CAP = mat('Cap', hexrgb(0x2f3a52), 0.8)
BOOT = mat('Boot', hexrgb(0x8a5a32), 0.7)
GLOVE = mat('Glove', hexrgb(0x8c5f38), 0.8)
BADGE = mat('Badge', hexrgb(0xf2efe6), 0.5)
EYE = mat('Eye', hexrgb(0x1b1b1b), 0.3)

p = root('Person')

# ขา: กางเกงทรงตรง (8 เหลี่ยม) + รองเท้าบูตหุ้มข้อ ปลายเท้าชี้ไปด้านหน้า (-y)
for s in (1, -1):
    prim('cylinder', 'Leg', PANTS, loc=(s * 0.1, 0, 0.55), vertices=8, radius=0.085, depth=0.8, parent=p)
    prim('cylinder', 'BootTop', BOOT, loc=(s * 0.1, 0, 0.13), vertices=8, radius=0.09, depth=0.2, parent=p)
    prim('cube', 'BootToe', BOOT, loc=(s * 0.1, -0.06, 0.04), scale=(0.085, 0.13, 0.045), parent=p)

# ลำตัว: เสื้อโปโลทรงกล่องเรียวลง (8 เหลี่ยม) + ปกเสื้อ + ป้ายชื่อที่อกซ้าย
prim('cone', 'Torso', SHIRT, loc=(0, 0, 1.17), vertices=8, radius1=0.2, radius2=0.25, depth=0.64, parent=p,
     scale=(1, 0.72, 1))
prim('cone', 'Collar', SHIRT, loc=(0, 0, 1.5), vertices=8, radius1=0.12, radius2=0.08, depth=0.06, parent=p)
prim('cube', 'Badge', BADGE, loc=(0.1, -0.185, 1.3), scale=(0.055, 0.008, 0.03), parent=p)

# คอ + หัว (ทรงเหลี่ยมโลว์โพลี) + จมูก + ตา + ผมด้านหลัง
prim('cylinder', 'Neck', SKIN, loc=(0, 0, 1.53), vertices=8, radius=0.055, depth=0.08, parent=p)
prim('uv_sphere', 'Head', SKIN, loc=(0, 0, 1.64), segments=8, ring_count=6, radius=0.12, parent=p, scale=(0.95, 1, 1.12))
prim('cube', 'Nose', SKIN, loc=(0, -0.12, 1.63), scale=(0.018, 0.02, 0.03), parent=p)
prim('uv_sphere', 'Hair', HAIR, loc=(0, 0.03, 1.66), segments=8, ring_count=6, radius=0.122, parent=p, scale=(1, 0.95, 1))
for s in (1, -1):
    prim('cube', 'Eye', EYE, loc=(s * 0.042, -0.112, 1.665), scale=(0.012, 0.006, 0.012), parent=p)
    prim('cube', 'Ear', SKIN, loc=(s * 0.115, 0.005, 1.64), scale=(0.015, 0.03, 0.04), parent=p)

# หมวกแก๊ป: ทรงโดมครึ่งลูก + ปีกหมวกยื่นไปด้านหน้า
prim('uv_sphere', 'CapTop', CAP, loc=(0, 0, 1.71), segments=8, ring_count=4, radius=0.13, parent=p, scale=(1, 1.02, 0.62))
prim('cube', 'CapBrim', CAP, loc=(0, -0.16, 1.715), scale=(0.1, 0.07, 0.01), rot=(math.radians(-8), 0, 0), parent=p)

# แขน: ตัวแม่ว่างที่หัวไหล่ ลูกคือแขนเสื้อสั้น (สีเสื้อ) + แขนท่อนล่าง (ผิว) + ถุงมือ ห้อยลงตามแกน -z
for s, nm in ((1, 'Person_ArmL'), (-1, 'Person_ArmR')):
    arm = bpy.data.objects.new(nm, None); bpy.context.scene.collection.objects.link(arm)
    arm.parent = p; arm.location = (s * 0.27, 0, 1.42)
    a = prim('cylinder', nm + '_Sleeve', SHIRT, vertices=8, radius=0.075, depth=0.22, parent=arm); a.location = (0, 0, -0.1)
    f = prim('cylinder', nm + '_Forearm', SKIN, vertices=6, radius=0.05, depth=0.36, parent=arm); f.location = (0, 0, -0.38)
    g = prim('cube', nm + '_Glove', GLOVE, scale=(0.045, 0.06, 0.08), parent=arm); g.location = (0, 0, -0.6)

export_glb('person.glb')
if bpy.app.background:
    render_preview('person.png', cam_loc=(2.2, -3.4, 1.9), target=(0, 0, 0.95), lens=55)
