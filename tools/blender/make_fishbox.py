# กล่องโฟมใส่ปลา → assets/models/fishbox.glb
# รุ่นปั้นใหม่ (1 พ.ย. 2026) ตามภาพอ้างอิง โมเดล/Group 1/fishbox.jpg: กล่องโฟมสีขาวนวล ฝามีขอบ สายรัดสีเทาเข้ม
# ป้ายเขียว LIVE ANIMALS และป้าย THIS WAY UP (ลูกศรคู่ กรอบแดง)
# มาร์ชเลือกให้ "วางนอน" ตามฉากเดิม: ยาว 1.6 ตามแกน x กว้าง 1.1 สูง 1.1 (ภาพอ้างอิงเป็นกล่องตั้ง ใช้แค่หน้าตา)
# ในเว็บ: Box_Body = ลำตัว (โค้ดเปลี่ยนเป็นสีแดงตอนเกิดความเสี่ยง) · LiveLabel / ArrowLabel = ป้าย (โค้ดซ่อนไว้ แล้วโชว์ในขั้น 5)
# แกน: Blender -y = ด้านหน้าในเว็บ (+z) · ฐานอยู่ที่ z = 0
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, render_preview, text, bevel_box, empty

reset()
FOAM = mat('Foam', hexrgb(0xeceae2), 0.95)
LID = mat('BoxLid', hexrgb(0xe3e1d8), 0.9)
STRAP = mat('Strap', hexrgb(0x4a4f52), 0.7)
GREEN = mat('LabelGreen', hexrgb(0x2f9a4a), 0.6)
WHITE = mat('LabelWhite', hexrgb(0xffffff), 0.6)
RED = mat('LabelRed', hexrgb(0xc8312b), 0.6)
INK = mat('Ink', hexrgb(0x1d1d1d), 0.6)

L, W, H = 1.6, 1.1, 1.1        # ยาว (x) กว้าง (y) สูง (z) รวมฝา
r = root('FishBox')

# ลำตัว + ฝา (ฝาเป็นแผ่นหนาที่ยื่นออกมาเล็กน้อย และมีขอบยกบนฝา)
bevel_box('Box_Body', (L, W, 0.9), (0, 0, 0.45), FOAM, r, 0.04)
bevel_box('Box_Lid', (L + 0.05, W + 0.05, 0.14), (0, 0, 0.97), LID, r, 0.035)
bevel_box('Box_LidTop', (L - 0.12, W - 0.12, 0.03), (0, 0, 1.05), LID, r, 0.01)

# สายรัด: 2 เส้นพันรอบกล่องตามแนวขวาง (แกน y) + 1 เส้นพันตามยาว (แกน x) — เป็นแถบบาง ๆ ห่อผิวกล่อง
T, SW = 0.012, 0.07            # ความหนา / ความกว้างของสายรัด
for x in (-0.42, 0.42):
    prim('cube', 'Strap', STRAP, loc=(x, 0, H / 2), scale=(SW / 2, W / 2 + T, H / 2 + T), parent=r)
prim('cube', 'Strap', STRAP, loc=(0, 0, H / 2), scale=(L / 2 + T, SW / 2, H / 2 + T), parent=r)

# ป้าย LIVE ANIMALS (เขียว ตัวหนังสือขาว) ที่ด้านหน้า (-y) ระหว่างสายรัดทั้งสองเส้น
FRONT = -W / 2 - 0.006
live = empty('LiveLabel', r)
prim('cube', 'LiveBg', GREEN, loc=(0, FRONT, 0.6), scale=(0.24, 0.004, 0.11), parent=live)
text('LIVE', 0.09, WHITE, (0, FRONT - 0.006, 0.635), (math.radians(90), 0, 0), live, name='LiveText1')
text('ANIMALS', 0.08, WHITE, (0, FRONT - 0.006, 0.555), (math.radians(90), 0, 0), live, name='LiveText2')

# ป้าย THIS WAY UP (พื้นขาว กรอบแดง ลูกศรดำ 2 อัน) มุมขวาบนของด้านหน้า และที่ด้านข้าง (+x)
arrow = empty('ArrowLabel', r)


def arrow_label(cx, cy, cz, rz):
    g = empty('ArrowSign', arrow, (cx, cy, cz)); g.rotation_euler = (0, 0, rz)
    prim('cube', 'ArrowFrame', RED, loc=(0, 0, 0), scale=(0.1, 0.004, 0.13), parent=g)
    prim('cube', 'ArrowBg', WHITE, loc=(0, -0.003, 0), scale=(0.085, 0.003, 0.115), parent=g)
    for dx in (-0.032, 0.032):
        prim('cube', 'ArrowStem', INK, loc=(dx, -0.007, -0.03), scale=(0.008, 0.002, 0.045), parent=g)
        prim('cone', 'ArrowHead', INK, loc=(dx, -0.007, 0.035), vertices=3, radius1=0.026, depth=0.002,
             rot=(math.radians(90), 0, 0), parent=g, scale=(1, 1.3, 1))
    prim('cube', 'ArrowBase', INK, loc=(0, -0.007, -0.085), scale=(0.06, 0.002, 0.006), parent=g)


arrow_label(0.66, FRONT, 0.68, 0)                            # ด้านหน้า มุมขวา
arrow_label(L / 2 + 0.006, -0.3, 0.68, math.radians(90))    # ด้านข้าง

# ข้อความบนฝา (ช่วยให้ผู้ชมรู้ว่ากล่องนี้ไปเที่ยวบินไหน)
text('KOI  JL707  NRT-BKK', 0.055, INK, (0, -0.3, 1.068), (0, 0, 0), r, name='LidText')

export_glb('fishbox.glb')
if bpy.app.background:
    render_preview('fishbox.png', cam_loc=(2.6, -3.4, 2.4), target=(0, 0, 0.5), lens=50)
