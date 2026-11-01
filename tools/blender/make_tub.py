# ถังพักปลา (ใช้ขั้น 1–3 ก่อนบรรจุถุง) → assets/models/tub.glb
# ใหม่ (1 พ.ย. 2026) ตามภาพอ้างอิง โมเดล/Group 1/tub.jpg: ถังพลาสติกสีขาวทรงสี่เหลี่ยมมุมมน ขอบบนหนา
# มีเส้นคาดกลางถัง ซี่เสริมแนวตั้ง และท่อระบายน้ำด้านหน้า · ขนาด 1.1 x 0.5 x 1.1
# ในเว็บ: Tub_Water = ผิวน้ำ · ปลาในถังโค้ดใส่เอง (ไม่ต้องปั้นในไฟล์นี้)
# แกน: Blender -y = ด้านหน้าในเว็บ (+z) · ฐานอยู่ที่ z = 0
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, prim, root, export_glb, render_preview, bevel_box, obj_from_bmesh

reset()
PLASTIC = mat('TubPlastic', hexrgb(0xeef0f2), 0.6)
RIB = mat('TubRib', hexrgb(0xd9dde2), 0.6)
WATER = mat('TubWater', hexrgb(0x5fb4e6), 0.05, alpha=0.8)
PIPE = mat('TubPipe', hexrgb(0x3a3f45), 0.5)

S, H, WALL = 1.1, 0.5, 0.06        # ด้านกว้าง ความสูง ความหนาผนัง
r = root('Tub')


def hollow_box(name, size, height, wall, material, parent, ring=False):
    """กล่องเปิดด้านบน (ผนัง 4 ด้าน + ก้น) มุมมนด้วย bevel · ring=True = ไม่มีก้นด้วย (เป็นกรอบรอบตัวถัง)"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(size, size, height), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, height / 2), verts=bm.verts)
    top = [f for f in bm.faces if f.normal.z > 0.9 or (ring and f.normal.z < -0.9)]
    bmesh.ops.delete(bm, geom=top, context='FACES_ONLY')
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=wall)
    ob = obj_from_bmesh(name, bm, material, parent=parent)
    m = ob.modifiers.new('bevel', 'BEVEL'); m.width = 0.04; m.segments = 2; m.limit_method = 'ANGLE'
    return ob


hollow_box('Tub_Body', S - 0.08, H - 0.06, WALL, PLASTIC, r)
# ขอบบนหนา (กรอบยื่นออกรอบปากถัง) = กล่องกลวงเตี้ย ๆ ที่ใหญ่กว่าตัวถังเล็กน้อย
hollow_box('Tub_Rim', S, 0.06, 0.07, PLASTIC, r, ring=True).location = (0, 0, H - 0.06)
# เส้นคาดกลางถังรอบตัว
hollow_box('Tub_Band', S - 0.04, 0.05, 0.03, RIB, r, ring=True).location = (0, 0, 0.22)
# ซี่เสริมแนวตั้ง 2 ซี่ต่อด้าน
for k in (-0.22, 0.22):
    for sx, sy, sc in ((k, -(S - 0.08) / 2 - 0.012, (0.025, 0.012, 0.21)), (k, (S - 0.08) / 2 + 0.012, (0.025, 0.012, 0.21)),
                       (-(S - 0.08) / 2 - 0.012, k, (0.012, 0.025, 0.21)), ((S - 0.08) / 2 + 0.012, k, (0.012, 0.025, 0.21))):
        prim('cube', 'Tub_Rib', RIB, loc=(sx, sy, 0.23), scale=sc, parent=r)
# ท่อระบายน้ำด้านหน้า (-y) ช่วงล่าง
prim('cylinder', 'Tub_Drain', PIPE, loc=(0, -(S - 0.08) / 2 - 0.02, 0.1), vertices=10, radius=0.045, depth=0.05,
     rot=(math.radians(90), 0, 0), parent=r)
# ผิวน้ำ (แผ่นเรียบใกล้ปากถัง)
prim('cube', 'Tub_Water', WATER, loc=(0, 0, H - 0.1), scale=((S - 0.08) / 2 - WALL, (S - 0.08) / 2 - WALL, 0.01), parent=r)

export_glb('tub.glb')
if bpy.app.background:
    render_preview('tub.png', cam_loc=(1.8, -2.4, 1.8), target=(0, 0, 0.25), lens=50)
