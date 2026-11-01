# ปลาคาร์ฟ 3 สายพันธุ์ (โคฮากุ ขาว-แดง / ซันเก้ ขาว-แดง-ดำ / โอกอน ทอง) → assets/models/koi.glb
# รุ่นปั้นใหม่ (1 พ.ย. 2026) ตามภาพอ้างอิง โมเดล/Group 1/koi.jpg: โลว์โพลีเห็นเหลี่ยม ครีบยาว มีหนวด
# ลวดลายใช้ "สีที่จุดยอด" (vertex color) ระบายทีละหน้า จึงเห็นลายเป็นปื้นเหลี่ยมแบบภาพ และไม่ต้องมีไฟล์ภาพ
# ในเว็บ: หัวปลาไปทาง +x ยาวราว 1 หน่วย หางเป็นวัตถุลูกชื่อ "<ชื่อปลา>_Tail" จุดหมุนอยู่ที่โคนหาง (โค้ดหมุนให้ส่ายหาง)
# วิธีรัน: ใน Blender ที่เปิดอยู่ผ่าน MCP หรือ blender --background --factory-startup --python tools/blender/make_koi.py
import bpy, bmesh, math, sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, root, export_glb, render_preview

reset()
random.seed(11)


def vcol_material(name):
    """วัสดุที่ใช้สีจากจุดยอด (สีลวดลายของปลา)"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    attr = nt.nodes.new('ShaderNodeVertexColor'); attr.layer_name = 'Col'
    nt.links.new(attr.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.4
    return m


def lin(rgb):
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb) + (1.0,)


def radius_at(t):
    """รัศมีลำตัวตามความยาว (t = 0 โคนหาง, 1 ปลายจมูก): ท้ายเรียว ตัวป่องช่วงหน้า หัวมน"""
    if t < 0.62:
        r = 0.035 + 0.105 * math.sin(math.pi / 2 * t / 0.62) ** 1.3
    else:
        k = (t - 0.62) / 0.38
        r = 0.14 * math.sqrt(max(0.0, 1 - k ** 2.2)) + 0.01
    return r


def body_mesh(name, paint):
    """ลำตัวโลว์โพลี (12 เหลี่ยมรอบตัว 18 ช่วงตามยาว) จาก x = -0.4 (โคนหาง) ถึง 0.48 (จมูก) ผิวเรียบแบบเหลี่ยม"""
    bm = bmesh.new(); rings, seg = 18, 12; prev = None
    col = bm.loops.layers.color.new('Col')
    for i in range(rings + 1):
        t = i / rings
        x = -0.4 + t * 0.88
        r = radius_at(t)
        ring = [bm.verts.new((x, math.cos(2 * math.pi * j / seg) * r * 0.78,
                              math.sin(2 * math.pi * j / seg) * r * (0.95 if math.sin(2 * math.pi * j / seg) > 0 else 0.8)))
                for j in range(seg)]
        if prev:
            for j in range(seg):
                bm.faces.new((prev[j], prev[(j + 1) % seg], ring[(j + 1) % seg], ring[j]))
        prev = ring
    # ปิดปลายจมูกเป็นจุดเดียว
    tip = bm.verts.new((0.5, 0, -0.005))
    for j in range(seg):
        bm.faces.new((prev[j], prev[(j + 1) % seg], tip))
    bm.normal_update()
    for f in bm.faces:                     # ระบายสีทั้งหน้า (ใช้จุดกลางของหน้า) ลายจึงเป็นปื้นเหลี่ยม
        c = paint(f.calc_center_median())
        for lp in f.loops:
            lp[col] = lin(c)                  # แปลงเป็นค่า linear ก่อน (แบบเดียวกับรุ่นเดิมที่สีในเว็บถูกต้อง)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    me.materials.append(vcol_material(name + '_mat'))
    return ob


def fin(name, verts, material, parent, loc=(0, 0, 0), thick=0.008):
    """ครีบแผ่นบาง (หลายเหลี่ยมแบน)"""
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in verts]; bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=thick)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material); ob.parent = parent; ob.location = loc
    return ob


def spots(centres, colour):
    """ปื้นลายบนผิวปลา: [(x, มุมรอบตัว, ครึ่งความยาว, ครึ่งความกว้างเป็นองศา)]
    มุม 90 = กลางหลัง, 30 = ข้างซ้ายค่อนบน, 150 = ข้างขวาค่อนบน (ลายจึงไม่พันรอบตัวเป็นปล้อง)"""
    return [(x, math.radians(a), rx, math.radians(ra), colour) for x, a, rx, ra in centres]


def painter(base, marks, belly):
    def paint(co):
        ang = math.atan2(co.z, -co.y)      # มุมรอบแกนตัวปลา (0 = ข้างขวา, 90 = หลัง, 180 = ข้างซ้าย)
        if co.z < -0.035:                  # ท้องสีอ่อนเสมอ (ลายอยู่บนหลังและข้างตัว)
            return belly
        c = base
        for cx, ca, rx, ra, colour in marks:
            if ((co.x - cx) / rx) ** 2 + ((ang - ca) / ra) ** 2 < 1:
                c = colour
        return c
    return paint


WHITE, RED, BLACK, GOLD = hexrgb(0xf4f3ef), hexrgb(0xd72a22), hexrgb(0x18181c), hexrgb(0xf0c64a)
BELLY_W, BELLY_G = hexrgb(0xfbfaf7), hexrgb(0xfae38e)
# ลายวางตามภาพ: โคฮากุ ปื้นแดงบนหัว แล้วสลับซ้าย-ขวาตามหลัง ปิดท้ายที่โคนหาง
KOHAKU = spots([(0.36, 90, 0.07, 50), (0.2, 55, 0.06, 40), (0.14, 125, 0.06, 40),
                (-0.02, 80, 0.07, 45), (-0.14, 140, 0.05, 35), (-0.3, 90, 0.05, 45)], RED)
# ซันเก้ = ลายแดงแบบโคฮากุ + จุดดำเล็ก ๆ บนหลัง (ไม่มีดำบนหัว)
SANKE = spots([(0.36, 90, 0.07, 50), (0.18, 120, 0.06, 45), (0.02, 60, 0.07, 45), (-0.2, 110, 0.06, 40),
               (-0.32, 80, 0.04, 40)], RED) + \
    spots([(0.24, 60, 0.025, 22), (0.1, 105, 0.03, 25), (-0.08, 140, 0.03, 25), (-0.12, 50, 0.025, 20),
           (-0.27, 120, 0.02, 20)], BLACK)

breeds = {
    'Koi_Kohaku': (painter(WHITE, KOHAKU, BELLY_W), mat('fin_white', hexrgb(0xf1f0ec), 0.4, alpha=0.88)),
    'Koi_Sanke': (painter(WHITE, SANKE, BELLY_W), mat('fin_white2', hexrgb(0xf1f0ec), 0.4, alpha=0.88)),
    'Koi_Ogon': (painter(GOLD, [], BELLY_G), mat('fin_gold', hexrgb(0xeab52e), 0.35, 0.15, alpha=0.92)),
}
EYE = mat('eye', hexrgb(0x111111), 0.2)

for k, (name, (paint, finmat)) in enumerate(breeds.items()):
    fish = root(name); fish.location = (0, k * 0.6 - 0.6, 0.25)
    body = body_mesh(name + '_Body', paint); body.parent = fish
    if name == 'Koi_Ogon':                  # โอกอนเป็นสีทองทั้งตัว: ใช้วัสดุสีเดียวกับครีบ ไม่ใช้สีจุดยอด (สีจะได้ตรงกัน)
        body.data.materials[0] = mat('gold_body', hexrgb(0xe9ad1f), 0.35, 0.15)
    # หาง: ตัวแม่ว่างที่โคนหาง (x = -0.4) ลูกคือครีบหางสองแฉก
    tail = bpy.data.objects.new(name + '_Tail', None); bpy.context.scene.collection.objects.link(tail)
    tail.parent = fish; tail.location = (-0.4, 0, 0)
    fin(name + '_TailFin', [(0.02, 0, 0.025), (-0.12, 0, 0.09), (-0.26, 0, 0.17), (-0.2, 0, 0.0),
                            (-0.26, 0, -0.15), (-0.12, 0, -0.08), (0.02, 0, -0.025)], finmat, tail)
    # ครีบหลังยาวตามแนวหลัง (สูงด้านหน้า ลาดไปด้านหลัง)
    fin(name + '_Dorsal', [(0.16, 0, 0.11), (0.08, 0, 0.21), (-0.04, 0, 0.17), (-0.2, 0, 0.1), (-0.22, 0, 0.07)], finmat, fish)
    for s, side in ((1, 'L'), (-1, 'R')):
        # ครีบอก (ใหญ่ กางออกข้าง) · ครีบท้อง · ครีบก้น
        fin(name + '_Pectoral' + side, [(0.24, s * 0.07, -0.07), (0.1, s * 0.24, -0.13), (0.04, s * 0.2, -0.13), (0.14, s * 0.07, -0.08)], finmat, fish)
        fin(name + '_Pelvic' + side, [(0.0, s * 0.05, -0.09), (-0.1, s * 0.13, -0.15), (-0.12, s * 0.07, -0.12)], finmat, fish)
        # ตา (นูนเล็ก ๆ ข้างหัว)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.017, segments=8, ring_count=6)
        e = bpy.context.active_object; e.name = name + '_Eye' + side; e.data.materials.append(EYE); e.parent = fish
        e.location = (0.39, s * 0.068, 0.035)
        # หนวด 1 คู่ที่มุมปาก
        fin(name + '_Barbel' + side, [(0.47, s * 0.03, -0.035), (0.43, s * 0.075, -0.075), (0.425, s * 0.07, -0.07)], finmat, fish, thick=0.006)
    fin(name + '_Anal', [(-0.16, 0, -0.07), (-0.22, 0, -0.14), (-0.27, 0, -0.06)], finmat, fish)

export_glb('koi.glb')
if bpy.app.background:
    render_preview('koi.png', cam_loc=(1.6, -1.6, 1.4), target=(0, 0, 0.2), lens=50)
