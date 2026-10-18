# คนทำงาน (สูง 1.75) สร้างด้วยโค้ด → assets/models/person.glb
# ในเว็บ: หันหน้าไปทาง +z, แขนเป็นวัตถุลูกชื่อ Person_ArmL / Person_ArmR จุดหมุนที่หัวไหล่ (ไว้ทำท่ายก/ชี้)
# สีเสื้อใช้วัสดุชื่อ "Shirt" — เว็บจะเปลี่ยนสีเสื้อตามบทบาท (เกษตรกร ผู้ตรวจ พนักงานภาคพื้น ฯลฯ)
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, render_preview

reset()
SHIRT = mat('Shirt', hexrgb(0x2f5fb5), 0.7)
PANTS = mat('Pants', hexrgb(0x2e3a4d), 0.8)
SKIN = mat('Skin', hexrgb(0xe9b98f), 0.6)
HAIR = mat('Hair', hexrgb(0x1f1a17), 0.8)
SHOE = mat('Shoe', hexrgb(0x2a2a2a), 0.6)
EYE = mat('Eye', hexrgb(0x111111), 0.3)

p = root('Person')
for s in (1, -1):                                         # ขา + รองเท้า (ซ้าย/ขวาตามแกน x)
    prim('cylinder', 'Leg', PANTS, loc=(s * 0.11, 0, 0.45), vertices=10, radius=0.085, depth=0.8, smooth=True, parent=p)
    prim('cube', 'Shoe', SHOE, loc=(s * 0.11, -0.03, 0.05), scale=(0.075, 0.11, 0.05), parent=p)
# ลำตัว (ทรงกระบอกเรียวเล็กน้อย) + คอ + หัว + ผม
prim('cone', 'Torso', SHIRT, loc=(0, 0, 1.12), vertices=12, radius1=0.21, radius2=0.24, depth=0.62, smooth=True, parent=p)
prim('cylinder', 'Neck', SKIN, loc=(0, 0, 1.47), vertices=10, radius=0.055, depth=0.1, smooth=True, parent=p)
prim('uv_sphere', 'Head', SKIN, loc=(0, 0, 1.62), segments=16, ring_count=10, radius=0.13, smooth=True, parent=p)
prim('uv_sphere', 'Hair', HAIR, loc=(0, 0.012, 1.66), segments=16, ring_count=10, radius=0.135, smooth=True, parent=p,
     scale=(1, 1, 0.75))
for s in (1, -1):
    prim('uv_sphere', 'Eye', EYE, loc=(s * 0.045, -0.12, 1.63), segments=6, ring_count=4, radius=0.016, parent=p)
# แขน: ตัวแม่ว่างที่หัวไหล่ ลูกคือท่อนแขน + มือ (ห้อยลงตามแกน -z)
for s, nm in ((1, 'Person_ArmL'), (-1, 'Person_ArmR')):
    arm = bpy.data.objects.new(nm, None); bpy.context.scene.collection.objects.link(arm)
    arm.parent = p; arm.location = (s * 0.27, 0, 1.38)
    a = prim('cylinder', nm + '_Sleeve', SHIRT, vertices=8, radius=0.06, depth=0.55, smooth=True, parent=arm); a.location = (0, 0, -0.27)
    h = prim('uv_sphere', nm + '_Hand', SKIN, segments=8, ring_count=6, radius=0.055, smooth=True, parent=arm); h.location = (0, 0, -0.58)

export_glb('person.glb')
render_preview('person.png', cam_loc=(2.2, -3.4, 1.9), target=(0, 0, 0.95), lens=55)
