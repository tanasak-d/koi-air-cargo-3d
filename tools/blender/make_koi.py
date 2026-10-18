# ปลาคาร์ฟ 3 สายพันธุ์ (โคฮากุ ขาว-แดง / ซันเก้ ขาว-แดง-ดำ / โอกอน ทอง) สร้างด้วยโค้ด → assets/models/koi.glb
# ลวดลายใช้ "สีที่จุดยอด" (vertex color) จึงไม่ต้องมีไฟล์ภาพ
# ในเว็บ: หัวปลาไปทาง +x ยาว 1 หน่วย หางเป็นวัตถุลูกชื่อ "<ชื่อปลา>_Tail" จุดหมุนอยู่ที่โคนหาง (ไว้ส่ายหาง)
import bpy, bmesh, math, sys, os, random
sys.path.insert(0, os.path.dirname(__file__))
from common import reset, mat, hexrgb, root, export_glb, render_preview

reset()
random.seed(7)

def vcol_material(name):
    """วัสดุที่ใช้สีจากจุดยอด (สีลวดลายของปลา)"""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    attr = nt.nodes.new('ShaderNodeVertexColor'); attr.layer_name = 'Col'
    nt.links.new(attr.outputs['Color'], p.inputs['Base Color'])
    p.inputs['Roughness'].default_value = 0.35
    return m

def lin(rgb):
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb) + (1.0,)

def body_mesh(name, paint):
    """ลำตัวทรงตอร์ปิโด แบนข้างเล็กน้อย หัวมน ท้ายเรียวไปที่โคนหาง (x = -0.5 .. 0.5)"""
    bm = bmesh.new(); rings, seg = 22, 16; prev = None; first = None
    col = bm.loops.layers.color.new('Col')
    for i in range(rings + 1):
        t = i / rings                       # 0 = โคนหาง, 1 = ปลายจมูก
        x = -0.38 + t * 0.86
        r = 0.13 * math.sin(math.pi * min(1, (t * 0.92 + 0.08))) ** 0.7 + 0.012
        if t > 0.9: r *= math.sqrt(max(0.0, 1 - ((t - 0.9) / 0.1) ** 2)) * 0.9 + 0.1
        ring = [bm.verts.new((x, math.cos(2 * math.pi * j / seg) * r * 0.72, math.sin(2 * math.pi * j / seg) * r * 0.95))
                for j in range(seg)]
        if prev:
            for j in range(seg):
                bm.faces.new((prev[j], prev[(j + 1) % seg], ring[(j + 1) % seg], ring[j]))
        prev = ring
    bm.normal_update()
    for f in bm.faces:
        for lp in f.loops:
            lp[col] = lin(paint(lp.vert.co))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    me.materials.append(vcol_material(name + '_mat'))
    for p in me.polygons: p.use_smooth = True
    return ob

def fin(name, verts, material, parent, loc=(0, 0, 0)):
    """ครีบแผ่นบาง (หลายเหลี่ยมแบน) จากจุดในแนว x-z หรือ x-y"""
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in verts]; bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.008)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material); ob.parent = parent; ob.location = loc
    return ob

def blobs(n, colour, spread=0.33):
    """จุดลวดลายสุ่มบนหลังปลา (ศูนย์กลาง รัศมี สี)"""
    return [((random.uniform(-0.3, 0.38), random.uniform(-0.05, 0.05), random.uniform(0.02, 0.12)), random.uniform(0.07, 0.13), colour)
            for _ in range(n)]

def painter(base, spots):
    def paint(co):
        c = base
        for (cx, cy, cz), r, colour in spots:
            if (co.x - cx) ** 2 + ((co.y - cy) * 0.7) ** 2 + (co.z - cz) ** 2 < r * r: c = colour
        if co.z < -0.06: c = tuple(min(1, v * 0.9 + 0.08) for v in base)   # ท้องสีอ่อน
        return c
    return paint

WHITE, RED, BLACK, GOLD = hexrgb(0xf7f5f0), hexrgb(0xd8342a), hexrgb(0x1b1b1f), hexrgb(0xf6c64a)
breeds = {
    'Koi_Kohaku': (WHITE, blobs(4, RED), mat('fin_white', hexrgb(0xf3f1ec), 0.4, alpha=0.85)),
    'Koi_Sanke': (WHITE, blobs(3, RED) + blobs(3, BLACK), mat('fin_white2', hexrgb(0xf3f1ec), 0.4, alpha=0.85)),
    'Koi_Ogon': (GOLD, [], mat('fin_gold', hexrgb(0xf0b23a), 0.3, 0.3, alpha=0.9)),
}
EYE = mat('eye', hexrgb(0x111111), 0.2)
for k, (name, (base, spots, finmat)) in enumerate(breeds.items()):
    fish = root(name); fish.location = (0, k * 0.6 - 0.6, 0.25)
    body = body_mesh(name + '_Body', painter(base, spots)); body.parent = fish
    # หาง (ลูกของปลา จุดหมุนที่โคนหาง x = -0.38) เป็นแฉกสองแฉก
    tail = bpy.data.objects.new(name + '_Tail', None); bpy.context.scene.collection.objects.link(tail)
    tail.parent = fish; tail.location = (-0.38, 0, 0)
    fin(name + '_TailFin', [(0, 0, 0.02), (-0.26, 0, 0.16), (-0.18, 0, 0.0), (-0.26, 0, -0.14), (0, 0, -0.02)], finmat, tail)
    fin(name + '_Dorsal', [(-0.2, 0, 0.1), (0.12, 0, 0.12), (0.02, 0, 0.2), (-0.16, 0, 0.16)], finmat, fish)
    for s in (1, -1):
        fin(name + '_Pectoral', [(0.22, s * 0.06, -0.06), (0.1, s * 0.2, -0.12), (0.06, s * 0.08, -0.08)], finmat, fish)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, location=(0.36, s * 0.055, 0.03), segments=8, ring_count=6)
        e = bpy.context.active_object; e.name = name + '_Eye'; e.data.materials.append(EYE); e.parent = fish
        e.location = (0.36, s * 0.062, 0.035)

export_glb('koi.glb')
render_preview('koi.png', cam_loc=(1.6, -1.6, 1.4), target=(0, 0, 0.2), lens=50)
