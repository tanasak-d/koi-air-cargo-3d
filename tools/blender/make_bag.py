# ถุงใส่ปลา 3 ชั้น (Triple Bagging) → assets/models/bag.glb
# รุ่นปั้นใหม่ (1 พ.ย. 2026) ตามภาพอ้างอิง โมเดล/Group 1/bag.jpg: ถุงใสทรงโอ่ง 3 ชั้นซ้อนกัน ปากถุงบิดเป็นเกลียว
# น้ำอยู่ราวครึ่งล่างของถุง ส่วนบนเป็นออกซิเจน (น้ำ : ออกซิเจน = 1 : 2 ตามปริมาตร)
# ขนาด 0.84 x 1.0 x 0.84 · ในเว็บ: Bag_L1 / Bag_L2 / Bag_L3 = ชั้นนอก / กลาง / ใน (โค้ดให้โผล่ทีละชั้น)
# ปลาในถุงโค้ดใส่เอง (ปลาตัวเล็กที่ความสูงราว 0.17) จึงไม่ต้องปั้นปลาในไฟล์นี้
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, render_preview, lathe

reset()
FILM = mat('BagFilm', hexrgb(0xdcefff), 0.15, alpha=0.22)
WATER = mat('Water', hexrgb(0x4aa3df), 0.05, alpha=0.55)
BAND = mat('Band', hexrgb(0xf28c28), 0.5)

r = root('Bag')
SEG = 12                                    # 12 เหลี่ยมรอบถุง = โลว์โพลีเห็นเส้นแบ่งแบบภาพ


def bag_profile(rad, h):
    """เส้นโปรไฟล์ (รัศมี, ความสูง) ของถุงหนึ่งชั้น: ก้นแบน ป่องช่วงล่าง แล้วรวบเข้าหาคอถุง"""
    return [(0.01, 0.0), (rad * 0.82, 0.01), (rad * 0.98, 0.08), (rad, 0.25 * h), (rad * 0.97, 0.48 * h),
            (rad * 0.82, 0.66 * h), (rad * 0.5, 0.8 * h), (rad * 0.16, 0.87 * h), (0.045, 0.9 * h)]


# ชั้นนอก → ชั้นใน (แต่ละชั้นเล็กลงเล็กน้อย จึงเห็นซ้อนกัน 3 ชั้น)
for k, (rad, h) in enumerate([(0.42, 0.92), (0.395, 0.88), (0.37, 0.84)]):
    lathe('Bag_L' + str(k + 1), bag_profile(rad, h), FILM, r, seg=SEG)

# น้ำในถุงชั้นใน (สูงราว 0.5 = 1 ส่วนจาก 3 ส่วนของปริมาตร ที่เหลือเป็นออกซิเจน)
lathe('Bag_Water', [(0.01, 0.012), (0.3, 0.02), (0.355, 0.08), (0.362, 0.21), (0.355, 0.44), (0.01, 0.44)], WATER, r, seg=SEG)

# ปากถุงบิดเป็นเกลียว (กรวยหัวกลับ 2 ชิ้นบิดคนละมุม) + ยางรัดสีส้ม
NECK = mat('BagNeck', hexrgb(0xdcefff), 0.15, alpha=0.4)
prim('cone', 'Bag_Twist', NECK, loc=(0, 0, 0.88), vertices=6, radius1=0.04, radius2=0.075, depth=0.1, parent=r)
prim('cone', 'Bag_Tail', NECK, loc=(0, 0, 0.96), vertices=6, radius1=0.05, radius2=0.11, depth=0.08,
     rot=(0, 0, math.radians(30)), parent=r)
prim('torus', 'Bag_Knot', BAND, loc=(0, 0, 0.84), major_radius=0.05, minor_radius=0.016, major_segments=10, minor_segments=5, parent=r)

export_glb('bag.glb')
if bpy.app.background:
    render_preview('bag.png', cam_loc=(1.6, -2.2, 1.4), target=(0, 0, 0.45), lens=50)
