# ตัวช่วยที่สคริปต์ Blender ทุกตัวใช้ร่วมกัน
# วิธีรัน (ตัวอย่าง):
#   "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python tools/blender/make_airliner.py
# ทุกสคริปต์ล้างฉากก่อน สร้างโมเดลด้วยโค้ด แล้วส่งออกเป็น .glb ไปที่ assets/models/ และเรนเดอร์ภาพตัวอย่างไปที่ assets/previews/
import bpy, bmesh, math, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS = os.path.join(ROOT, 'assets', 'models')
PREVIEWS = os.path.join(ROOT, 'assets', 'previews')


_mats = {}


def reset():
    """ล้างฉากให้ว่าง (ไม่เหลือกล้อง ไฟ ลูกบาศก์เริ่มต้น)"""
    if bpy.app.background:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    else:
        # รันใน Blender ที่เปิดอยู่ (ผ่าน MCP): ห้ามรีเซ็ตทั้งโปรแกรม เพราะหน้าจอที่มาร์ชดูอยู่จะหายไป
        # จึงลบแค่วัตถุและข้อมูลในฉาก
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights, bpy.data.worlds,
                     bpy.data.images):
            for d in list(coll):
                if d.users == 0:
                    coll.remove(d)
    _mats.clear()   # วัสดุเก่าถูกลบไปพร้อมฉากแล้ว ต้องล้างที่จำไว้ด้วย


def mat(name, rgb, rough=0.6, metal=0.0, alpha=1.0):
    """วัสดุสีเดียว (rgb เป็นค่า 0..1 แบบที่ตาเห็น) ใช้ซ้ำตามชื่อ"""
    if name in _mats:
        return _mats[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    # Blender เก็บสีแบบ linear: แปลงจากสีที่ตาเห็น (sRGB) ก่อน
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    p.inputs['Base Color'].default_value = (*lin, 1.0)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if alpha < 1.0:
        p.inputs['Alpha'].default_value = alpha
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            m.blend_method = 'BLEND'
    _mats[name] = m
    return m


def hexrgb(h):
    return ((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255


def obj_from_bmesh(name, bm, material, smooth=False, parent=None):
    """สร้างวัตถุจาก bmesh แล้วใส่วัสดุ"""
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(material)
    for poly in me.polygons:
        poly.use_smooth = smooth
    if parent is not None:
        ob.parent = parent
    return ob


def prim(kind, name, material, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, smooth=False, **kw):
    """สร้างรูปทรงพื้นฐาน (cube / cylinder / uv_sphere / cone / torus)"""
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    ob.data.materials.append(material)
    for poly in ob.data.polygons:
        poly.use_smooth = smooth
    if parent is not None:
        ob.parent = parent
    return ob


def root(name):
    """วัตถุว่างเป็นตัวแม่ของทั้งโมเดล (ส่งออกเป็นโหนดเดียว)"""
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def export_glb(filename):
    """ส่งออกทั้งฉากเป็น .glb (แกน +Y ขึ้นแบบ glTF) — ใช้ค่าสี/วัสดุ ไม่มีภาพ texture"""
    os.makedirs(MODELS, exist_ok=True)
    path = os.path.join(MODELS, filename)
    bpy.ops.object.select_all(action='SELECT')
    # ภาพ texture (เช่น โลโก้) แปลงเป็น JPEG — Three.js r128 อ่าน webp ใน glTF ไม่ได้ และ JPEG ไฟล์เล็ก
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=False, export_image_format='JPEG',
                              export_apply=True, export_yup=True, export_cameras=False, export_lights=False)
    print('EXPORTED', path, os.path.getsize(path))
    return path


def render_preview(filename, cam_loc, target=(0, 0, 0), lens=50, size=(960, 540)):
    """เรนเดอร์ภาพตัวอย่าง (ไว้ให้มาร์ชดู) ด้วยไฟแดด + พื้นสีเทาอ่อน"""
    os.makedirs(PREVIEWS, exist_ok=True)
    sc = bpy.context.scene
    for eng in ('BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH'):
        try:
            sc.render.engine = eng
            break
        except Exception:
            continue
    sc.render.resolution_x, sc.render.resolution_y = size
    world = bpy.data.worlds.new('w'); world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.62, 0.78, 0.92, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8
    sc.world = world
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5
    so = bpy.data.objects.new('sun', sun); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    sc.collection.objects.link(so)
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(mat('ground_preview', (0.78, 0.8, 0.82)))
    cam = bpy.data.cameras.new('cam'); cam.lens = lens
    co = bpy.data.objects.new('cam', cam); co.location = cam_loc
    sc.collection.objects.link(co)
    tgt = bpy.data.objects.new('tgt', None); tgt.location = target; sc.collection.objects.link(tgt)
    c = co.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    sc.camera = co
    sc.render.filepath = os.path.join(PREVIEWS, filename)
    bpy.ops.render.render(write_still=True)
    print('PREVIEW', sc.render.filepath)


# ---------- ตัวช่วยรูปทรง (ใช้ร่วมกันหลายสคริปต์) ----------
THAI_FONT = 'C:/Windows/Fonts/tahoma.ttf'     # ฟอนต์ของ Windows ที่มีตัวอักษรไทย (ฟอนต์ในตัวของ Blender ไม่มีภาษาไทย)


def text(body, size, material, loc, rot, parent, extrude=0.004, name='Text', font=None):
    """ตัวอักษรแปลงเป็นเมช · ค่าเริ่มต้นใช้ฟอนต์ในตัวของ Blender (ภาษาอังกฤษ) · ข้อความไทยส่ง font=THAI_FONT"""
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.active_object
    if font:
        t.data.font = bpy.data.fonts.load(font, check_existing=True)
        # Blender วางวรรณยุกต์ไทยไม่เป็น: "น้ำ" จะเห็นไม้โทจมหายใต้สระอำ
        # แก้โดยแยกสระอำเป็นนิคหิต + สระอา แล้ววางนิคหิตก่อนวรรณยุกต์ (ทดสอบกับ tahoma แล้วตรง)
        import re
        body = re.sub('([่-๋])ำ', 'ํ\\1า', body)
    t.data.body = body; t.data.size = size; t.data.extrude = extrude
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    t.data.resolution_u = 2          # เส้นโค้งของตัวอักษรหยาบลงหน่อย ไฟล์จะเล็กลงมาก (มองไม่ออกในฉาก)
    bpy.ops.object.convert(target='MESH')
    t = bpy.context.active_object; t.name = name
    t.data.materials.clear(); t.data.materials.append(material)
    if parent is not None:
        t.parent = parent            # ตำแหน่ง loc นับจากตัวแม่ (เหมือนชิ้นอื่น ๆ)
    return t


def bevel_box(name, size, loc, material, parent, width=0.04):
    """กล่องขอบมน (bevel) — ให้ดูเป็นของจริงกว่ากล่องเหลี่ยมคม"""
    ob = prim('cube', name, material, loc=loc, scale=(size[0] / 2, size[1] / 2, size[2] / 2), parent=parent)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(scale=True)
    m = ob.modifiers.new('bevel', 'BEVEL'); m.width = width; m.segments = 2
    return ob


def empty(name, parent, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.parent = parent; e.location = loc
    return e


def lathe(name, profile, material, parent, seg=20, loc=(0, 0, 0)):
    """หมุนเส้นโปรไฟล์ (รัศมี, ความสูง) รอบแกนตั้ง ได้รูปทรงกลมแบบถุง/ขวด"""
    bm = bmesh.new(); rings = []
    for r_, z in profile:
        rings.append([bm.verts.new((loc[0] + math.cos(2 * math.pi * j / seg) * r_, loc[1] + math.sin(2 * math.pi * j / seg) * r_, loc[2] + z)) for j in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for j in range(seg):
            bm.faces.new((a[j], a[(j + 1) % seg], b[(j + 1) % seg], b[j]))
    bm.normal_update()
    return obj_from_bmesh(name, bm, material, smooth=True, parent=parent)


# ---------- โลโก้หลักสูตร (ใช้กับเครื่องบินและรถทุกคัน) ----------
LOGO_PATH = os.path.join(ROOT, 'assets', 'textures', 'aviation-logo.webp')
# ส่วนของภาพที่มีโลโก้ (ภาพ 2000×2000 พื้นโปร่งใส โลโก้อยู่ช่วงกลาง) เป็นพิกัด UV: u ซ้าย→ขวา, v ล่าง→บน
LOGO_UV = (0.005, 0.99, 0.29, 0.76)
_logo = {}
LOGO_PX = 512                 # ความละเอียดภาพโลโก้ (512 px ชัดพอบนรถในฉาก และไฟล์เล็กกว่า 1024 ราว 3 เท่า)


def logo_material(bg=(1.0, 1.0, 1.0)):
    """วัสดุภาพโลโก้บนพื้นสี bg (ค่า 0..1 แบบที่ตาเห็น ค่าเริ่มต้นขาว) ภาพย่อเหลือ LOGO_PX px ไฟล์จะได้เล็ก
    ใช้สีพื้นเดียวกับผิวที่แปะ (เช่น หางสีฟ้า) แผ่นโลโก้จะกลืนไปกับผิว — สร้างครั้งเดียวต่อสีพื้นต่อฉาก"""
    key = tuple(round(c, 3) for c in bg)
    if key in _logo and _logo[key].name in bpy.data.materials:
        return _logo[key]
    import numpy as np
    src = bpy.data.images.load(LOGO_PATH, check_existing=True)
    img = src.copy(); img.name = 'logo_%02x%02x%02x' % tuple(int(c * 255) for c in bg)
    img.scale(LOGO_PX, LOGO_PX)
    # ภาพต้นฉบับมีพื้นโปร่งใส: เทสีพื้นลงไปแทน (ส่งออกเป็น JPEG ซึ่งไม่มีความโปร่งใส ส่วนโปร่งใสจะกลายเป็นสีดำ)
    px = np.empty(LOGO_PX * LOGO_PX * 4, dtype=np.float32); img.pixels.foreach_get(px)
    px = px.reshape(-1, 4); a_ = px[:, 3:4]
    px[:, :3] = px[:, :3] * a_ + np.array(bg, dtype=np.float32) * (1.0 - a_); px[:, 3] = 1.0
    img.pixels.foreach_set(px.ravel())
    img.pack()                    # เก็บภาพที่แก้แล้วไว้ในไฟล์ ตัวส่งออกจะได้ใช้ภาพนี้ (ไม่ไปอ่านไฟล์ต้นฉบับใหม่)
    m = bpy.data.materials.new('Logo'); m.use_nodes = True
    tex = m.node_tree.nodes.new('ShaderNodeTexImage'); tex.image = img
    m.node_tree.links.new(tex.outputs['Color'], m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.5
    _logo[key] = m
    return m


def logo_decal(name, parent, center, width, face='-y', bg=(1.0, 1.0, 1.0)):
    """แผ่นโลโก้บาง ๆ แปะผิว (ไม่หนา ไม่บังรูปทรง) รักษาสัดส่วนภาพ
    face = ทิศที่แผ่นหันออก: '-y' / '+y' (ด้านข้างรถ/ลำตัว) หรือ '+x' / '-x' (หน้า/ท้าย)
    ใน Blender ด้าน -y = ด้าน +z ในเว็บ (ฝั่งกล้อง)"""
    u0, u1, v0, v1 = LOGO_UV
    h = width * (v1 - v0) / (u1 - u0)
    cx, cy, cz = center
    bm = bmesh.new(); uv = bm.loops.layers.uv.new('UVMap')
    # มุมซ้ายล่าง → ขวาล่าง → ขวาบน → ซ้ายบน เมื่อมองจากด้านที่แผ่นหันออก (ตัวอักษรจึงไม่กลับด้าน)
    if face == '-y':
        pts = [(cx - width / 2, cy, cz - h / 2), (cx + width / 2, cy, cz - h / 2), (cx + width / 2, cy, cz + h / 2), (cx - width / 2, cy, cz + h / 2)]
    elif face == '+y':
        pts = [(cx + width / 2, cy, cz - h / 2), (cx - width / 2, cy, cz - h / 2), (cx - width / 2, cy, cz + h / 2), (cx + width / 2, cy, cz + h / 2)]
    elif face == '+x':
        pts = [(cx, cy - width / 2, cz - h / 2), (cx, cy + width / 2, cz - h / 2), (cx, cy + width / 2, cz + h / 2), (cx, cy - width / 2, cz + h / 2)]
    else:
        pts = [(cx, cy + width / 2, cz - h / 2), (cx, cy - width / 2, cz - h / 2), (cx, cy - width / 2, cz + h / 2), (cx, cy + width / 2, cz + h / 2)]
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    for lp, c in zip(f.loops, ((u0, v0), (u1, v0), (u1, v1), (u0, v1))):
        lp[uv].uv = c
    bm.normal_update()
    return obj_from_bmesh(name, bm, logo_material(bg), parent=parent)


def wheel(name, loc, radius, width, tyre, rim, parent, seg=12, axis='y'):
    """ล้อโลว์โพลี: ยาง + กระทะล้อทั้งสองข้าง (แกนล้อตามแกน y ของรถ)"""
    rot = (math.radians(90), 0, 0) if axis == 'y' else (0, math.radians(90), 0)
    prim('cylinder', name, tyre, loc=loc, rot=rot, vertices=seg, radius=radius, depth=width, parent=parent)
    for s in (1, -1):
        off = (0, s * (width / 2 + 0.005), 0) if axis == 'y' else (s * (width / 2 + 0.005), 0, 0)
        prim('cylinder', name + '_Rim', rim, loc=(loc[0] + off[0], loc[1] + off[1], loc[2]), rot=rot,
             vertices=seg, radius=radius * 0.55, depth=0.01, parent=parent)


def boxes(name, items, material, parent, bevel=0.0):
    """รวมกล่องหลายใบเป็นเมชเดียว (ไฟล์เล็กกว่าสร้างทีละชิ้นมาก เหมาะกับซี่ผนัง เสา คาน)
    items = [(ศูนย์กลาง (x, y, z), ครึ่งขนาด (hx, hy, hz))] · bevel > 0 = ลบมุมทุกกล่อง"""
    bm = bmesh.new()
    for (cx, cy, cz), (hx, hy, hz) in items:
        res = bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.scale(bm, vec=(hx, hy, hz), verts=res['verts'])
        bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=res['verts'])
    ob = obj_from_bmesh(name, bm, material, parent=parent)
    if bevel > 0:
        m = ob.modifiers.new('bevel', 'BEVEL'); m.width = bevel; m.segments = 1
    return ob


def emblem(name, parent, center, radius, face='-y'):
    """ตราหน่วยงานแบบวงกลมเรียบ ๆ (ไม่ใช่ตราจริง): วงกลมน้ำเงิน ขอบทอง จุดกลางทอง — มาร์ชเลือก 1 พ.ย. 2026"""
    BLUE = mat('EmblemBlue', hexrgb(0x1f3f8a), 0.5)
    GOLD = mat('EmblemGold', hexrgb(0xd4a63a), 0.35, 0.5)
    rot = {'-y': (math.radians(90), 0, 0), '+y': (math.radians(-90), 0, 0),
           '+x': (0, math.radians(90), 0), '-x': (0, math.radians(-90), 0)}[face]
    out = {'-y': (0, -1, 0), '+y': (0, 1, 0), '+x': (1, 0, 0), '-x': (-1, 0, 0)}[face]
    g = empty(name, parent, center)
    prim('cylinder', name + '_Ring', GOLD, loc=(0, 0, 0), rot=rot, vertices=20, radius=radius, depth=0.06, parent=g)
    prim('cylinder', name + '_Disc', BLUE, loc=tuple(o * 0.035 for o in out), rot=rot, vertices=20, radius=radius * 0.82, depth=0.02, parent=g)
    prim('cylinder', name + '_Dot', GOLD, loc=tuple(o * 0.05 for o in out), rot=rot, vertices=12, radius=radius * 0.3, depth=0.02, parent=g)
    return g
